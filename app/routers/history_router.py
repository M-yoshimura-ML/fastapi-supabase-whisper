from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import async_session
from app.models.conversation import Conversation
from app.models.message import Message
import uuid
from datetime import datetime

router = APIRouter()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


class MessageCreate(BaseModel):
    role: str
    content: str
    translated_content: str | None = None


class HistoryCreate(BaseModel):
    user_id: uuid.UUID
    title: str
    messages: List[MessageCreate]


@router.post("/history")
async def save_history(data: HistoryCreate, session: AsyncSession = Depends(get_session)):
    try:
        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=data.user_id,
            title=data.title,
            created_at=datetime.now()
        )
        session.add(conversation)

        # reflect conversation.id in DB
        await session.flush()

        for m in data.messages:
            message = Message(
                id=uuid.uuid4(),
                conversation_id=conversation.id,
                role=m.role,
                content=m.content,
                translated_content=m.translated_content,
                created_at=datetime.now()
            )
            session.add(message)

        await session.commit()
        return {"conversation_id": str(conversation.id)}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_user_history(user_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    try:
        result = await session.execute(
            select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.created_at.desc())
        )
        conversations = result.scalars().all()

        history = []
        for conv in conversations:
            conv_result = await session.execute(
                select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at)
            )
            messages = conv_result.scalars().all()

            history.append({
                "conversation_id": str(conv.id),
                "title": conv.title,
                "created_at": conv.created_at,
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "translated_content": msg.translated_content,
                        "created_at": msg.created_at
                    } for msg in messages
                ]
            })

        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

