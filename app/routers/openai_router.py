from fastapi import APIRouter, UploadFile, File, Form, Depends

from app.dtos.openai_dto import ChatRequest, TranslateRequest
from app.dtos.response_dto import api_response
from app.models import User
from app.service.auth_service import get_current_user
from app.service.openai_service import OpenAIService


class OpenAIController:
    def __init__(self):
        self.router = APIRouter(prefix="/api/openai")
        self.openai_service = OpenAIService()
        self._add_routes()

    def _add_routes(self):
        @self.router.post("/chat")
        async def chat(data: ChatRequest, current_user: User = Depends(get_current_user)):
            reply = await self.openai_service.chat_with_history(data, current_user)
            return api_response(200, "success", reply)

        @self.router.post("/translate")
        async def translate(data: TranslateRequest, current_user: User = Depends(get_current_user)):
            translated_text = await self.openai_service.translate_text(data.text, data.target_language)
            return api_response(200, "success", translated_text)

        @self.router.post("/transcribe")
        async def transcribe_audio(
                audio_file: UploadFile = File(...),
                language: str = Form(None),
                current_user: User = Depends(get_current_user)):
            response_text = await self.openai_service.transcribe(audio_file, language)
            return api_response(200, "success", response_text)

        @self.router.post("/text-chat")
        async def text_chat(
                payload: ChatRequest,
                current_user: User = Depends(get_current_user)):

            response_data = await self.openai_service.chat_response(payload, current_user)
            return api_response(200, "success", response_data)

        @self.router.post("/voice-chat")
        async def voice_chat(
            audio_file: UploadFile = File(...),
            language: str = Form("ja"),  # or auto-detect
            current_user: User = Depends(get_current_user)
        ):
            return await self.openai_service.voice_response(audio_file, language, current_user.preferred_text_model)

