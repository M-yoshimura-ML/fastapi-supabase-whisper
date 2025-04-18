from dotenv import load_dotenv
from openai import AsyncClient
import os

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

