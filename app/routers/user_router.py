from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.response_dto import api_response
from app.dtos.user_dto import SettingsUpdateRequest
from app.exceptions.exceptions import NotFoundException
from app.models import User
from app.service.auth_service import get_current_user
from app.service.user_service import UserService


class UserController:
    def __init__(self):
        self.router = APIRouter(prefix="/api/user")
        self.user_service = UserService()
        self._add_routes()

    def _add_routes(self):
        @self.router.put("/update-settings")
        async def update_user_settings(
                update: SettingsUpdateRequest,
                db: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user),
        ):
            user = await self.user_service.get_user_by_id(current_user.id, db)
            if not user:
                raise NotFoundException(item="User ")

            await self.user_service.save_user_preferences(user, update, db)
            return api_response(200, "success")

        @self.router.get("/get-settings")
        def get_user_settings(
                db: AsyncSession = Depends(get_db),
                current_user: User = Depends(get_current_user),
        ):
            data = self.user_service.get_user_preferences(current_user)
            return api_response(200, "success", data)
