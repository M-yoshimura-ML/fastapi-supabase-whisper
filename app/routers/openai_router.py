from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import openai
import os

from app.dtos.response_dto import api_response
from app.models import User
from app.service.auth_service import get_current_user

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    history: list
    language: str = "ja"


class TranslateRequest(BaseModel):
    text: str
    target_language: str


@router.post("/chat")
async def chat_with_gpt(data: ChatRequest, current_user: User = Depends(get_current_user)):
    try:
        messages = [{"role": m["role"], "content": m["content"]} for m in data.history]
        messages.append({"role": "user", "content": data.message})

        response = openai.chat.completions.create(
            model="gpt-4-0613",
            messages=messages
        )
        reply = response.choices[0].message.content
        return api_response(200, "success", reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_text(data: TranslateRequest, current_user: User = Depends(get_current_user)):
    try:
        prompt = f"translate below sentences to {data.target_language}. \n\n{data.text}"
        response = openai.chat.completions.create(
            model="gpt-4-0613",
            messages=[{"role": "user", "content": prompt}]
        )
        translated_text = response.choices[0].message.content
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

