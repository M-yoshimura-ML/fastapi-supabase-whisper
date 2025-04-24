import os.path
import asyncio
from dotenv import load_dotenv
from gtts import gTTS
from supabase import create_client
import uuid
import time
import logging

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SERVICE_ROLE_SECRET")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _generate_audio(text: str, lang: str = "ja") -> str:
    tts = gTTS(text=text, lang=lang)
    filename = f"{uuid.uuid4()}.mp3"
    tts.save(filename)
    return filename


async def generate_audio_async(text: str, lang: str = "ja") -> str:
    """同期的な generate_audio を別スレッドで実行する非同期ラッパー"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _generate_audio, text, lang)


def _upload_to_supabase(filepath: str, bucket: str) -> str:
    """
    :rtype: str
    """
    filename = os.path.basename(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"file is not existing: {filepath}")

    with open(filepath, "rb") as f:
        supabase_client.storage.from_(bucket).upload(filename, f, file_options={"content-type": "audio/mpeg"})

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    return public_url


async def upload_to_supabase_async(filepath: str, bucket: str) -> str:
    """同期的な upload_to_supabase を別スレッドで実行する非同期ラッパー"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _upload_to_supabase, filepath, bucket)


async def create_audio_and_upload(text: str, lang: str = "ja", bucket: str = "ai-speak") -> str:
    start = time.time()
    mp3_file = await generate_audio_async(text, lang)
    logger.info(f"TTS生成: {time.time() - start:.2f} sec")
    try:
        start_upload = time.time()
        url = await upload_to_supabase_async(mp3_file, bucket)
        logger.info(f"Supabaseアップロード: {time.time() - start_upload:.2f} sec")
        return url
    finally:
        os.remove(mp3_file)
