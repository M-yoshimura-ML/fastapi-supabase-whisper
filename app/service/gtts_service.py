import asyncio
from gtts import gTTS
import uuid


class GttsService:
    def _generate_audio(self, text: str, lang: str = "ja") -> str:
        tts = gTTS(text=text, lang=lang)
        filename = f"{uuid.uuid4()}.mp3"
        tts.save(filename)
        return filename

    async def generate_audio_async(self, text: str, lang: str = "ja") -> str:
        """An asynchronous wrapper for the synchronous _generate_audio in a separate thread"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._generate_audio, text, lang)

