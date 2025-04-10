from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: list
    language: str = "ja"


@router.post("/chat")
async def chat_with_gpt(data: ChatRequest):
    try:
        messages = [{"role": m["role"], "content": m["content"]} for m in data.history]
        messages.append({"role": "user", "content": data.message})

        response = openai.chat.completions.create(
            model="gpt-4-0613",
            messages=messages
        )
        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
