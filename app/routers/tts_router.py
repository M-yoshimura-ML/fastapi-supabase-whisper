import io

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from gtts import gTTS

from app.dtos.response_dto import api_response
from app.models import User
from app.service.auth_service import get_current_user
from app.service.file_storage_service import FileStorageService
from app.service.gtts_service import GttsService

# router = APIRouter()
# file_storage_service = FileStorageService()
# gtts_service = GttsService()


class TTSRequest(BaseModel):
    text: str
    language: str = "ja"


class TTSController:
    def __init__(self):
        self.router = APIRouter(prefix="/api/tts")
        self.file_storage_service = FileStorageService()
        self.gtts_service = GttsService()
        self._add_routes()

    def _add_routes(self):
        @self.router.post("/tts-audio")
        async def text_to_speech(data: TTSRequest):
            try:
                tts = gTTS(text=data.text, lang=data.language)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                return StreamingResponse(fp, media_type="audio/mpeg")

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.router.post("/tts-api")
        async def tts_api(data: TTSRequest, current_user: User = Depends(get_current_user)):
            mp3_file = await self.gtts_service.generate_audio_async(data.text, data.language)
            url = await self.file_storage_service.upload_to_supabase_async(mp3_file)
            return api_response(200, "success", {"audio_url": url})

