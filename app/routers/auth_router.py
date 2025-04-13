from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import User
from app.service.auth_service import hash_password, verify_password, create_access_token
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
        raise HTTPException(status_code=400, detail="Email already registered")

    if request.password is None or len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password length should be more than 8 characters")

    user = User(
        name=request.name,
        email=request.email,
        password=hash_password(request.password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": "User created successfully"}


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "Bearer"}
