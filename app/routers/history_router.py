from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos.history_dto import HistoryCreate, MessagesCreate
from app.dtos.response_dto import api_response
from app.models import User
from app.models.conversation import Conversation
import uuid
from datetime import datetime
from app.db import get_db
from app.service.auth_service import get_current_user
from app.service.history_service import HistoryService
from app.service.openai_service import OpenAIService

router = APIRouter()


@router.post("/history")
async def save_history(
        data: HistoryCreate,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    try:
        openai_service = OpenAIService()
        if not data.title:
            all_texts = [m.content for m in data.messages if m.role == "user"]
            # ToDo get language setting
            auto_title = await openai_service.generate_title(all_texts, language="en")
            data.title = auto_title

        history_service = HistoryService()

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=data.userId,
            title=data.title,
            created_at=datetime.now()
        )
        session.add(conversation)

        # reflect conversation.id in DB
        await session.flush()

        await history_service.save_messages(data.messages, conversation.id, session)

        return api_response(200, "success", {"conversation_id": str(conversation.id)})

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{user_id}")
async def get_user_history(
        user_id: str,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    try:
        history_service = HistoryService()
        conversations = await history_service.get_user_conversations(user_id, session)
        history = await history_service.get_history(conversations, session)

        return api_response(200, "success", history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-conversations")
async def get_user_conversations(
        user_id: str,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    try:
        history_service = HistoryService()
        conversation_list = await history_service.get_conversation_list(user_id, session)

        return api_response(200, "success", conversation_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation-messages")
async def get_conversation_messages(
        conversation_id: str,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    try:
        history_service = HistoryService()
        message_list = await history_service.get_message_list(conversation_id, session)

        return api_response(200, "success", message_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-messages")
async def save_messages(
        data: MessagesCreate,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    try:
        history_service = HistoryService()
        conversation = await history_service.get_conversation(data.conversationId, session)
        if not conversation:
            return api_response(400, "Invalid conversationId")

        await history_service.save_messages(data.messages, data.conversationId, session)

        return api_response(200, "success")

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

