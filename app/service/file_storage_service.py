import asyncio
import os

from fastapi import HTTPException
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SERVICE_ROLE_SECRET")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)


class FileStorageService:
    def _upload_to_supabase(self, filepath: str, bucket: str) -> str:
        """
        :rtype: str
        """
        try:
            filename = os.path.basename(filepath)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"file is not existing: {filepath}")

            with open(filepath, "rb") as f:
                supabase_client.storage.from_(bucket).upload(filename, f, file_options={"content-type": "audio/mpeg"})

            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
            return public_url
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            os.remove(filepath)

    async def upload_to_supabase_async(self, filepath: str, bucket: str = "ai-speak") -> str:
        """An asynchronous wrapper for the synchronous _upload_to_supabase in a separate thread"""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._upload_to_supabase, filepath, bucket)


