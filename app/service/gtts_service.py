import os.path

from dotenv import load_dotenv
from gtts import gTTS
from supabase import create_client
import uuid

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SERVICE_ROLE_SECRET")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)


def generate_audio(text: str, lang: str = "ja") -> str:
    tts = gTTS(text=text, lang=lang)
    filename = f"{uuid.uuid4()}.mp3"
    tts.save(filename)
    return filename


def upload_to_supabase(filepath: str, bucket: str) -> str:
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


def create_audio_and_upload(text: str, lang: str = "ja", bucket: str = "ai-speak") -> str:
    mp3_file = generate_audio(text, lang)
    try:
        url = upload_to_supabase(mp3_file, bucket)
        return url
    finally:
        os.remove(mp3_file)
