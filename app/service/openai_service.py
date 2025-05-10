from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile, File, Form
from openai import AsyncClient
import os
import uuid
from app.dtos.openai_dto import ChatRequest

load_dotenv()
client = AsyncClient(api_key=os.getenv("OPENAI_API_KEY"))


class OpenAIService:
    async def generate_title(self, message: list[str], language: str = "ja") -> str:
        conversation = "\n".join(message)
        prompt = f"""
        There are conversations with AI below. 
        Summarize these conversations then make title with {language} and 10 to 20 characters.
        
        Conversations:
        {conversation}
        """

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        return response.choices[0].message.content.strip()

    async def chat_with_text(self, text: str):
        try:
            chat_response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": text}],
            )
            reply_text = chat_response.choices[0].message.content
            return reply_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def chat_with_history(self, data: ChatRequest) -> str:
        try:
            messages = [{"role": m["role"], "content": m["content"]} for m in data.history]
            messages.append({"role": "user", "content": data.message})

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            reply = response.choices[0].message.content
            return reply

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def translate_text(self, text: str, target_language: str) -> str:
        try:
            prompt = f"translate below sentences to {target_language}. \n\n{text}"
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
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
