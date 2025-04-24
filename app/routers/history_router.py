from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import async_session
from app.dtos.openai_dto import ChatRequest
from app.dtos.response_dto import api_response
from app.models import User
from app.models.conversation import Conversation
from app.models.message import Message
import uuid
from datetime import datetime, timezone
from app.db import get_db
from app.service.auth_service import get_current_user
from app.service.gtts_service import create_audio_and_upload
from app.service.openai_service import generate_title, chat_with_gpt, translate_text

router = APIRouter()


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


@router.post("/history")
async def save_history(
        data: HistoryCreate,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    try:
        if not data.title:
            all_texts = [m.content for m in data.messages if m.role == "user"]
            # ToDo get language setting
            auto_title = await generate_title(all_texts, language="ja")
            data.title = auto_title

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=data.userId,
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
                translated_content=m.translatedContent,
                audio_url=m.audioUrl,
                created_at=datetime.now()
            )
            session.add(message)

        await session.commit()
        return api_response(200, "success", {"conversation_id": str(conversation.id)})

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_user_history(
        user_id: uuid.UUID,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
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
                "conversationId": str(conv.id),
                "title": conv.title,
                "createdAt": conv.created_at,
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "translatedContent": msg.translated_content,
                        "audioUrl": msg.audio_url,
                        "createdAt": msg.created_at
                    } for msg in messages
                ]
            })

        return api_response(200, "success", history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-conversations")
async def get_user_conversations(
        user_id: uuid.UUID,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    try:
        result = await session.execute(
            select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.created_at.desc())
        )
        conversations = result.scalars().all()

        response_data = []
        for conv in conversations:
            response_data.append({
                "id": str(conv.id),
                "title": conv.title,
                "userId": str(conv.user_id),
                "createdAt": conv.created_at.isoformat(),
            })

        return api_response(200, "success", response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation-messages")
async def get_conversation_messages(
        conversation_id: uuid.UUID,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    try:
        result = await session.execute(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
        )
        messages = result.scalars().all()

        response_data = []
        for message in messages:
            response_data.append({
                "id": str(message.id),
                "role": message.role,
                "content": message.content,
                "translatedContent": message.translated_content,
                "conversationId": str(message.conversation_id),
                "audioUrl": message.audio_url,
                "createdAt": message.created_at.isoformat(),
            })

        return api_response(200, "success", response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-messages")
async def save_messages(
        data: MessagesCreate,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    try:
        result = await session.execute(
            select(Conversation).where(Conversation.id == data.conversationId)
        )
        conversation = result.scalars().all()
        if not conversation:
            return api_response(400, "Invalid conversationId")

        for m in data.messages:
            message = Message(
                id=uuid.uuid4(),
                conversation_id=data.conversationId,
                role=m.role,
                content=m.content,
                translated_content=m.translatedContent,
                audio_url=m.audioUrl,
                created_at=datetime.now()
            )
            session.add(message)

        await session.commit()
        return api_response(200, "success")

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.post("/text-chat")
async def chat(
        payload: ChatRequest,
        current_user: User = Depends(get_current_user)):
    start_time = time.time()
    logger.info("💬 Chat API called")

    try:
        # Call OpenAI
        openai_start = time.time()
        reply = await chat_with_gpt(payload)
        logger.info(f"🧠 OpenAI response time: {time.time() - openai_start:.2f} sec")

        # Translate
        translate_start = time.time()
        translated_text = await translate_text(reply, payload.language)
        logger.info(f"🌍 Translation time: {time.time() - translate_start:.2f} sec")

        # TTS
        tts_start = time.time()
        audio_url = await create_audio_and_upload(reply, payload.language)
        logger.info(f"🔊 TTS time: {time.time() - tts_start:.2f} sec")

        logger.info(f"✅ Total chat endpoint time: {time.time() - start_time:.2f} sec")

        response_data = {
            "role": "assistant",
            "content": reply,
            "translatedContent": translated_text,
            "audioUrl": audio_url
        }

        return api_response(200, "success", response_data)
    except Exception as e:
        logger.exception("❌ Chat API failed")
        raise HTTPException(status_code=500, detail=str(e))
