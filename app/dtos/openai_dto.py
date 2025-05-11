from typing import Literal, TypedDict, List
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    history: list
    language: str = "ja"


class TranslateRequest(BaseModel):
    text: str
    target_language: str


class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


ChatMessages = List[ChatMessage]

