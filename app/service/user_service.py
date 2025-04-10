from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.dtos.user_dto import UserCreate
import uuid


async def create_user(db: AsyncSession, data: UserCreate):
    db_user = User(
        id=uuid.uuid4(),
        **data.dict()
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_users(db: AsyncSession, limit: int = 10):
    result = await db.execute(select(User).order_by(User.created_at.desc()).limit(limit))
    return result.scalars().all()
