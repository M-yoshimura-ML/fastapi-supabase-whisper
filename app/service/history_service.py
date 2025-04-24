from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Message, Conversation


class HistoryService:
    async def get_message(self, conversation_id: str, session: AsyncSession = Depends(get_db)):
        result = await session.execute(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
        )
        messages = result.scalars().all()
        return messages

    async def get_conversation(self, conversation_id: str, session: AsyncSession = Depends(get_db)):
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalars().first()
        return conversation
