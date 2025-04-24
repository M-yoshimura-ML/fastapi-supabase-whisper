import io

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from gtts import gTTS

from app.dtos.response_dto import api_response
from app.service.gtts_service import create_audio_and_upload

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    language: str = "ja"


@router.post("/tts")
async def text_to_speech(data: TTSRequest):
    try:
        tts = gTTS(text=data.text, lang=data.language)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return StreamingResponse(fp, media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts-api")
async def tts_api(data: TTSRequest):
    try:
        url = await create_audio_and_upload(data.text, data.language)
        return api_response(200, "success", {"audio_url": url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

