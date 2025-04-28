import uuid
from datetime import datetime
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.history_dto import MessageBase
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

    async def get_user_conversations(self, user_id: str, session: AsyncSession = Depends(get_db)):
        result = await session.execute(
            select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.created_at.desc())
        )
        conversations = result.scalars().all()
        return conversations

    async def get_conversation_list(self, user_id, session: AsyncSession = Depends(get_db)):
        conversations = await self.get_user_conversations(user_id, session)

        conversation_list = []
        for conv in conversations:
            conversation_list.append({
                "id": str(conv.id),
                "title": conv.title,
                "userId": str(conv.user_id),
                "createdAt": conv.created_at.isoformat(),
            })

        return conversation_list

    async def get_message_list(self, conversation_id, session: AsyncSession = Depends(get_db)):
        messages = await self.get_message(conversation_id, session)

        message_list = []
        for message in messages:
            message_list.append({
                "id": str(message.id),
                "role": message.role,
                "content": message.content,
                "translatedContent": message.translated_content,
                "conversationId": str(message.conversation_id),
                "audioUrl": message.audio_url,
                "createdAt": message.created_at.isoformat(),
            })

        return message_list

    async def save_messages(
            self,
            data: List[MessageBase],
            conversationId: str,
            session: AsyncSession = Depends(get_db)):
        try:
            if conversationId:
                for m in data:
                    message = Message(
                        id=uuid.uuid4(),
                        conversation_id=conversationId,
                        role=m.role,
                        content=m.content,
                        translated_content=m.translatedContent,
                        audio_url=m.audioUrl,
                        created_at=datetime.now()
                    )
                    session.add(message)
                await session.commit()

        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_history(self, conversations, session: AsyncSession = Depends(get_db)):
        try:
            history = []
            for conv in conversations:
                conv_result = await session.execute(
                    select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at)
                )
                messages = conv_result.scalars().all()

                history.append({
                    "conversationId": str(conv.id),
                    "title": conv.title,
                    "createdAt": conv.created_at.isoformat(),
                    "messages": [
                        {
                            "role": msg.role,
                            "content": msg.content,
                            "translatedContent": msg.translated_content,
                            "audioUrl": msg.audio_url,
                            "createdAt": msg.created_at.isoformat()
                        } for msg in messages
                    ]
                })

            return history
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

