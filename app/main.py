from typing import List

import logging
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from app.db import get_db
from app.dtos.user_dto import UserResponse, UserCreate
from app.routers import user_router, openai_router, tts_router, history_router, auth_router
from app.service.user_service import create_user, get_users

app = FastAPI()
logging = logging.getLogger(__name__)

# @app.on_event("startup")
# async def on_startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# include your routers
app.include_router(user_router.router)
app.include_router(openai_router.router)
app.include_router(tts_router.router)
app.include_router(history_router.router)
app.include_router(auth_router.router)

origins = [
    "http://localhost:3000",  # Next.js server URL
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/user/", response_model=UserResponse)
async def post_message(data: UserCreate, db: AsyncSession = Depends(get_db)):
    logging.info(f"received data: {data}")
    return await create_user(db, data)


@app.get("/users/", response_model=List[UserResponse])
async def read_messages(limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await get_users(db, limit)

