from dotenv import load_dotenv
from fastapi import HTTPException
from openai import AsyncClient
import os
import uuid
from app.dtos.openai_dto import ChatRequest

load_dotenv()
client = AsyncClient(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_title(message: list[str], language: str = "ja") -> str:
    prompt = f"""
    There are conversations with AI below. 
    Summarize these conversations then make title with {language} and 10 to 20 characters.
    
    Conversations:
    {'\n'.join(message)}
    """

    response = await client.chat.completions.create(
        model="gpt-4-0613",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()


async def chat_with_gpt(data: ChatRequest) -> str:
    try:
        messages = [{"role": m["role"], "content": m["content"]} for m in data.history]
        messages.append({"role": "user", "content": data.message})

        response = await client.chat.completions.create(
            model="gpt-4-0613",
            messages=messages
        )
        reply = response.choices[0].message.content
        return reply

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def translate_text(text: str, target_language: str) -> str:
    try:
        prompt = f"translate below sentences to {target_language}. \n\n{text}"
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[{"role": "user", "content": prompt}]
        )
        translated_text = response.choices[0].message.content
        return translated_text

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_openai_tts(text: str, voice: str = "nova") -> str:
    filename = f"{uuid.uuid4()}.mp3"
    response = await client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename
