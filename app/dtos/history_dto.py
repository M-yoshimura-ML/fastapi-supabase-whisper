import uuid
from typing import List

from pydantic import BaseModel


class MessageBase(BaseModel):
    role: str
    content: str
    translatedContent: str | None = None
    audioUrl: str | None


class HistoryCreate(BaseModel):
    userId: uuid.UUID
    title: str | None
    messages: List[MessageBase]


class MessagesCreate(BaseModel):
    conversationId: str
    messages: List[MessageBase]

