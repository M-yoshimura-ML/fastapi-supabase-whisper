import random

from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from app.db import get_db
from app.exceptions.exceptions import InvalidCredentialException, NotFoundException
from app.models.user import User
from app.service.email_service import EmailService

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class AuthService:
    def __init__(self):
        self.email_service = EmailService()

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_pw: str, hashed_pw: str) -> bool:
        return pwd_context.verify(plain_pw, hashed_pw)

    def create_access_token(self, data: dict, expire_delta: timedelta = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expire_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        print("expire:", expire)
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def generate_otp(self) -> str:
        return f"{random.randint(100000, 999999)}"

    async def send_otp_email(self, user_email: str, otp: str):
        subject = "【Cymbal Direct】2段階認証コードのお知らせ"
        body = f"""
        あなたの認証コードは {otp} です。
        このコードは5分以内に有効です。
        """
        self.email_service.send_text_email(to_email=user_email, subject=subject, body=body)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise InvalidCredentialException()

    result = await db.execute(select(User).where(User.id == payload.get("sub")))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException(item="User ")

    return user

