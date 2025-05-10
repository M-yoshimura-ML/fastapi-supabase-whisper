from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)
    preferred_language = Column(String, default="ja")
    preferred_text_model = Column(String, default="gpt-4o-mini")
    preferred_speech_model = Column(String, default="tts-1")
    preferred_transcribe_model = Column(String, default="whisper-1")
    use_history = Column(Boolean, default=True)
    prompt_template = Column(Text,
                             default="You are kind assistant. Understand user's context and answer simply")
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
