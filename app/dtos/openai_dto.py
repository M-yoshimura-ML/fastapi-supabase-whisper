from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    history: list
    language: str = "ja"


class TranslateRequest(BaseModel):
    text: str
    target_language: str

