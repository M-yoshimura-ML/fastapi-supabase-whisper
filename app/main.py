import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions.exception_handler import (
    custom_http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.routers import websocket_router
from app.routers.auth_router import AuthController
from app.routers.history_router import HistoryController
from app.routers.openai_router import OpenAIController
from app.routers.tts_router import TTSController
from app.routers.user_router import UserController

load_dotenv()

logging = logging.getLogger(__name__)

origins = [
    "http://localhost:3000",  # Next.js server URL
    "https://next-ai-voice-chat.vercel.app"
]
logging.info(origins)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# async def on_startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# custom exception handlers
app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Controllers
user_controller = UserController()
auth_controller = AuthController()
openai_controller = OpenAIController()
tts_controller = TTSController()
history_controller = HistoryController()
# include your routers
app.include_router(user_controller.router)
app.include_router(openai_controller.router)
app.include_router(tts_controller.router)
app.include_router(history_controller.router)
app.include_router(auth_controller.router)
app.include_router(websocket_router.router)

