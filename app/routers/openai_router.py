import io
import os
import time
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
import openai
from starlette.responses import StreamingResponse

from app.dtos.openai_dto import ChatRequest, TranslateRequest
from app.dtos.response_dto import api_response
from app.models import User
from app.service.auth_service import get_current_user
from app.service.gtts_service import create_audio_and_upload
from app.service.openai_service import chat_with_gpt, translate_text
from app.utils.string_utils import StringUtils

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.post("/chat")
async def chat(data: ChatRequest, current_user: User = Depends(get_current_user)):
    try:
        reply = await chat_with_gpt(data)
        return api_response(200, "success", reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate(data: TranslateRequest, current_user: User = Depends(get_current_user)):
    try:
        translated_text = await translate_text(data.text, data.target_language)
        return api_response(200, "success", translated_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe")
async def transcribe_audio(
        audio_file: UploadFile = File(...),
        language: str = Form(None),
        current_user: User = Depends(get_current_user)):
    try:
        contents = await audio_file.read()
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=(audio_file.filename, contents),
            language=language
        )
        return api_response(200, "success", response.text)

    except Exception as e:
        raise JSONResponse(status_code=500, contents={"error": str(e)})


@router.post("/text-chat")
async def text_chat(
        payload: ChatRequest,
        current_user: User = Depends(get_current_user)):
    start_time = time.time()
    logger.info("💬 Chat API called")

    try:
        # Call OpenAI
        openai_start = time.time()
        reply = await chat_with_gpt(payload)
        logger.info(f"🧠 OpenAI response time: {time.time() - openai_start:.2f} sec")

        # Translate
        translate_start = time.time()
        translated_text = await translate_text(reply, payload.language)
        logger.info(f"🌍 Translation time: {time.time() - translate_start:.2f} sec")

        # TTS
        tts_start = time.time()
        audio_url = await create_audio_and_upload(reply, payload.language)
        logger.info(f"🔊 TTS time: {time.time() - tts_start:.2f} sec")

        logger.info(f"✅ Total chat endpoint time: {time.time() - start_time:.2f} sec")

        response_data = {
            "role": "assistant",
            "content": reply,
            "translatedContent": translated_text,
            "audioUrl": audio_url
        }

        return api_response(200, "success", response_data)
    except Exception as e:
        logger.exception("❌ Chat API failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-chat")
async def voice_chat(
    audio_file: UploadFile = File(...),
    language: str = Form("ja"),  # or auto-detect
    current_user: User = Depends(get_current_user)
):
    start_time = time.time()
    logger.info("💬 Voice Chat API called")

    try:
        transcribe_start = time.time()
        contents = await audio_file.read()

        # 1. Transcribe
        transcribed = openai.audio.transcriptions.create(
            model="whisper-1",
            file=(audio_file.filename, contents),
            language=language
        )
        user_text = transcribed.text
        logger.info(f"🧠 OpenAI transcribe time: {time.time() - transcribe_start:.2f} sec")

        chat_start = time.time()

        # 2. Chat
        chat_response = openai.chat.completions.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": user_text}],
        )
        reply_text = chat_response.choices[0].message.content
        logger.info(f"🧠 OpenAI chat time: {time.time() - chat_start:.2f} sec")

        tts_start = time.time()
        # 3. TTS
        speech_response = openai.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=reply_text,
        )

        # ToDo save audio stream to audio file and upload to storage

        # sanitized = StringUtils.sanitize_filename(reply_text)
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


