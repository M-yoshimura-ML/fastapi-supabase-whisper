from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.dtos.auth_dto import SignUpRequest, LoginRequest
from app.dtos.response_dto import api_response
from app.models import User
from app.service.auth_service import AuthService, get_current_user
from app.service.user_service import UserService


class AuthController:
    def __init__(self):
        self.router = APIRouter(prefix="/api/auth")
        self.auth_service = AuthService()
        self.user_uservice = UserService()
        self._add_routes()

    def _add_routes(self):
        @self.router.post("/signup")
        async def signup(request: SignUpRequest, db: AsyncSession = Depends(get_db)):
            await self.user_uservice.register_user(request, db)
            return api_response(200, "success")

        @self.router.post("/login")
        async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
            token = await self.user_uservice.authenticate(request, db)
            data = {"access_token": token, "token_type": "Bearer"}
            return api_response(200, "success", data)

        @self.router.post("/refresh-token")
        def refresh_token(current_user: User = Depends(get_current_user)):
            new_token = self.auth_service.create_access_token({"sub": str(current_user.id)})
            data = {"access_token": new_token, "token_type": "Bearer"}
            return api_response(200, "success", data)

        @self.router.get("/auth-me")
        def get_auth_me(current_user: User = Depends(get_current_user)):
            return {
                "id": current_user.id,
                "email": current_user.email,
                "created_at": current_user.created_at
            }

