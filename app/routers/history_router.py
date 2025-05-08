from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos.history_dto import HistoryCreate, MessagesCreate
from app.dtos.response_dto import api_response
from app.models import User
from app.db import get_db
from app.service.auth_service import get_current_user
from app.service.history_service import HistoryService
from app.service.openai_service import OpenAIService


class HistoryController:
    def __init__(self):
        self.router = APIRouter(prefix="/api/history")
        self.history_service = HistoryService()
        self.openai_service = OpenAIService()
        self._add_routes()

    def _add_routes(self):
        @self.router.post("/save")
        async def save_history(
                data: HistoryCreate,
                session: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
            """
            Save initial conversation and messages
            :param data:
            :param session:
            :param current_user:
            :return: api_response
            """
            try:
                if not data.title:
                    all_texts = [m.content for m in data.messages if m.role == "user"]
                    # ToDo get language setting
                    auto_title = await self.openai_service.generate_title(all_texts, language="en")
                    data.title = auto_title

                conversation = await self.history_service.save_conversation(str(current_user.id), data.title, session)
                await self.history_service.save_messages(data.messages, conversation.id, session)

                return api_response(200, "success", {"conversationId": str(conversation.id)})

            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=str(e))

        @self.router.get("/get")
        async def get_user_history(
                session: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
            conversations = await self.history_service.get_user_conversations(str(current_user.id), session)
            history = await self.history_service.get_history(conversations, session)

            return api_response(200, "success", history)

        @self.router.get("/user-conversations")
        async def get_user_conversations(
                # user_id: str,
                session: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
            conversation_list = await self.history_service.get_conversation_list(str(current_user.id), session)
            return api_response(200, "success", conversation_list)

        @self.router.get("/conversation-messages")
        async def get_conversation_messages(
                conversation_id: str,
                session: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
            message_list = await self.history_service.get_message_list(
                conversation_id, str(current_user.id), session
            )
            return api_response(200, "success", message_list)

        @self.router.post("/save-messages")
        async def save_messages(
                data: MessagesCreate,
                session: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user)):
            conversation = await self.history_service.get_conversation(data.conversationId, session)
            if not conversation:
                return api_response(400, "Invalid conversationId")

            await self.history_service.save_messages(data.messages, data.conversationId, session)

            return api_response(200, "success")


