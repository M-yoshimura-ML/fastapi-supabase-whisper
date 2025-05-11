import io
import time
import logging

from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile, File, Form
from openai import AsyncClient
from starlette.responses import StreamingResponse
import os
import uuid
from app.dtos.openai_dto import ChatRequest, ChatMessages
from app.models import User
from app.service.file_storage_service import FileStorageService

load_dotenv()
client = AsyncClient(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OpenAIService:
    def __init__(self):
        self.text_model = "gpt-4o-mini"
        self.translate_model = "gpt-3.5-turbo-1106"
        self.file_storage_service = FileStorageService()

    async def chat_with_text(self, model: str, messages: ChatMessages):
        gpt_model = model if model else self.text_model
        try:
            chat_response = await client.chat.completions.create(
                model=gpt_model,
                messages=messages,
                temperature=0.5
            )
            reply_text = chat_response.choices[0].message.content
            return reply_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_title(self, model: str, message: list[str], language: str = "ja") -> str:
        conversation = "\n".join(message)
        prompt = f"""
        There are conversations with AI below. 
        Summarize these conversations then make title with {language} and 10 to 20 characters.
        
        Conversations:
        {conversation}
        """

        messages: ChatMessages = [{"role": "user", "content": prompt}]
        return await self.chat_with_text(model, messages)

    async def chat_with_history(self, data: ChatRequest, current_user: User) -> str:
        messages: ChatMessages = []
        try:
            if current_user.prompt_template:
                messages.append({
                    "role": "system",
                    "content": current_user.prompt_template
                })

            if current_user.use_history:
                messages.extend([
                    {"role": m["role"], "content": m["content"]} for m in data.history
                ])
            # messages = [{"role": m["role"], "content": m["content"]} for m in data.history]
            messages.append({"role": "user", "content": data.message})

            return await self.chat_with_text(current_user.preferred_text_model, messages)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def translate_text(self, text: str, target_language: str) -> str:
        try:
            prompt = f"translate below sentences to {target_language}. \n\n{text}"
            response = await client.chat.completions.create(
                model=self.translate_model,
                messages=[{"role": "user", "content": prompt}]
            )
            translated_text = response.choices[0].message.content
            return translated_text

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def tts(self, text: str, voice: str = "nova"):
        try:
            speech_response = await client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            return speech_response
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_openai_tts(self, text: str, voice: str = "nova") -> str:
        """
        Text-To-Speech: generate audio file from text
        :param text:
        :param voice:
        :return: audio file name
        """
        filename = f"{uuid.uuid4()}.mp3"
        response = await self.tts(text, voice)
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename

    async def transcribe(self, audio_file: UploadFile = File(...), language: str = Form(None)):
        """
        from audio file, generate text
        :param audio_file:
        :param language:
        :return: text
        """
        try:
            contents = await audio_file.read()
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=(audio_file.filename, contents),
                language=language
            )
            return response.text
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def chat_response(self, payload: ChatRequest, current_user: User):
        try:
            start_time = time.time()
            logger.info("💬 Chat API called")
            # Call OpenAI
            openai_start = time.time()
            reply = await self.chat_with_history(payload, current_user)
            logger.info(f"🧠 OpenAI response time: {time.time() - openai_start:.2f} sec")

            # Translate
            translate_start = time.time()
            translated_text = await self.translate_text(reply, payload.language)
            logger.info(f"🌍 Translation time: {time.time() - translate_start:.2f} sec")

            # TTS
            tts_start = time.time()
            mp3_file = await self.generate_openai_tts(reply)
            logger.info(f"🔊 TTS time: {time.time() - tts_start:.2f} sec")
            audio_url = await self.file_storage_service.upload_to_supabase_async(mp3_file)
            logger.info(f"✅ Total chat endpoint time: {time.time() - start_time:.2f} sec")

            return {
                "role": "assistant",
                "content": reply,
                "translatedContent": translated_text,
                "audioUrl": audio_url
            }

        except Exception as e:
            logger.exception("❌ Chat API failed")
            raise HTTPException(status_code=500, detail=str(e))

    async def voice_response(
            self, audio_file: UploadFile = File(...), language: str = "ja", model: str = "gpt-4o-mini"):
        try:
            start_time = time.time()
            logger.info("💬 Voice Chat API called")

            transcribe_start = time.time()
            # 1. Transcribe
            user_text = await self.transcribe(audio_file, language)
            logger.info(f"🧠 OpenAI transcribe time: {time.time() - transcribe_start:.2f} sec")

            chat_start = time.time()
            # 2. Chat
            messages = [{"role": "user", "content": user_text}]
            reply_text = await self.chat_with_text(model, messages)
            logger.info(f"🧠 OpenAI chat time: {time.time() - chat_start:.2f} sec")

            tts_start = time.time()
            # 3. TTS
            speech_response = await self.tts(reply_text)

            # ToDo save audio stream to audio file and upload to storage
            import base64
            reply_text_b64 = base64.b64encode(reply_text.encode("utf-8")).decode("ascii")
            audio_byte = await speech_response.aread()

            logger.info(f"🧠 OpenAI tts time: {time.time() - tts_start:.2f} sec")
            logger.info(f"✅ Total chat endpoint time: {time.time() - start_time:.2f} sec")

            # 4. Return both text and audio
            return StreamingResponse(
                io.BytesIO(audio_byte),
                media_type="audio/mpeg",
                headers={"X-Reply-Text": reply_text_b64}
            )

        except Exception as e:
            import traceback
            logger.error("Exception occurred")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))
