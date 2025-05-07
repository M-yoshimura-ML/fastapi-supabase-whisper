from pydantic import BaseModel, field_validator


class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str

    @field_validator("password")
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str

