from typing import List

import logging
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import async_session
from app.dtos.user_dto import UserResponse, UserCreate
from app.routers import user_router
from app.service.user_service import create_user, get_users

app = FastAPI()
logging = logging.getLogger(__name__)

# @app.on_event("startup")
# async def on_startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# include your routers
app.include_router(user_router.router)


async def get_db():
    async with async_session() as session:
        yield session


@app.post("/user/", response_model=UserResponse)
async def post_message(data: UserCreate, db: AsyncSession = Depends(get_db)):
    logging.info(f"received data: {data}")
    return await create_user(db, data)


@app.get("/users/", response_model=List[UserResponse])
async def read_messages(limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_users(db, limit)

