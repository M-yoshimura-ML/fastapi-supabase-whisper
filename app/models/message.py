from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversation.id", ondelete="CASCADE"))
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    translated_content = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        CheckConstraint("role in ('user', 'assistant')", name="valid_role"),
    )

    conversation = relationship("Conversation", back_populates="messages")
