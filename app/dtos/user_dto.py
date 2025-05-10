from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: str
    name: str
    preferred_language: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    preferred_language: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SettingsUpdateRequest(BaseModel):
    language: Optional[str] = None
    textModel: Optional[str] = None
    speechModel: Optional[str] = None
    transcribeModel: Optional[str] = None
    useHistory: Optional[bool] = None
    promptTemplate: Optional[str] = None

