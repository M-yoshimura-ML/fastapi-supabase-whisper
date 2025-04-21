from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.dtos.response_dto import api_response
from app.models import User
from app.service.auth_service import hash_password, verify_password, create_access_token, get_current_user
from pydantic import BaseModel


router = APIRouter()


class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
async def signup(request: SignUpRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    if user:
        return api_response(400, "Email already registered")

    if request.password is None or len(request.password) < 8:
        return api_response(400, "Password length should be more than 8 characters")

    user = User(
        name=request.name,
        email=request.email,
        password=hash_password(request.password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return api_response(200, "success")


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(request.password, user.password):
        return api_response(401, "Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    data = {"access_token": token, "token_type": "Bearer"}
    return api_response(200, "success", data)


@router.post("/refresh-token")
def refresh_token(current_user: User = Depends(get_current_user)):
    new_token = create_access_token({"sub": str(current_user.id)})
    data = {"access_token": new_token, "token_type": "Bearer"}
    return api_response(200, "success", data)


@router.get("/auth-me")
def get_auth_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

