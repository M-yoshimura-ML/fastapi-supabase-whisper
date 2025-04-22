import logging
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from starlette.middleware.cors import CORSMiddleware

from app.routers import user_router, openai_router, tts_router, history_router, auth_router
from app.routers.exception_handler import (
    custom_http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

app = FastAPI()
logging = logging.getLogger(__name__)

# @app.on_event("startup")
# async def on_startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# custom exception handlers
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

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
