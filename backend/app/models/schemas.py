from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None

class TokenData(BaseModel):
    user_id: str | None = None

# User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    name: str | None
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

