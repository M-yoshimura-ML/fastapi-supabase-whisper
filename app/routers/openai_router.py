from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
import openai
import os

from app.dtos.openai_dto import ChatRequest, TranslateRequest
from app.dtos.response_dto import api_response
from app.models import User
from app.service.auth_service import get_current_user
from app.service.openai_service import chat_with_gpt, translate_text

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

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
        response = await openai.audio.transcriptions.create(
            model="whisper-1",
            file=(audio_file.filename, contents),
            language=language
        )
        return api_response(200, "success", response.text)

    except Exception as e:
        raise JSONResponse(status_code=500, contents={"error": str(e)})

