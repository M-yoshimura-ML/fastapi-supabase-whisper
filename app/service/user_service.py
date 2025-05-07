from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_db
from app.dtos.auth_dto import SignUpRequest, LoginRequest
from app.exceptions.exceptions import UserAlreadyExistsException, InvalidCredentialException
from app.models.user import User
from app.dtos.user_dto import UserCreate
import uuid

from app.service.auth_service import AuthService


class UserService:
    def __init__(self):
        self.auth_service = AuthService()

    async def create_user(self, db: AsyncSession, data: UserCreate):
        db_user = User(
            id=uuid.uuid4(),
            **data.dict()
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def get_users(self, db: AsyncSession, limit: int = 10):
        result = await db.execute(select(User).order_by(User.created_at.desc()).limit(limit))
        return result.scalars().all()

    async def get_user_by_email(self, email: str, db: AsyncSession = Depends(get_db)) -> User:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return user

    async def register_user(self, request: SignUpRequest, db: AsyncSession = Depends(get_db)):
        user = await self.get_user_by_email(request.email, db)
        if user:
            raise UserAlreadyExistsException()

        user = User(
            name=request.name,
            email=request.email,
            password=self.auth_service.hash_password(request.password)
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

    async def authenticate(self, request: LoginRequest, db: AsyncSession = Depends(get_db)):
        user = await self.get_user_by_email(request.email, db)

        if not user or not self.auth_service.verify_password(request.password, user.password):
            raise InvalidCredentialException()

        token = self.auth_service.create_access_token({"sub": str(user.id)})
        return token
