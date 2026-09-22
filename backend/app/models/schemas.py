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
    
class RefreshResponse(BaseModel):
    access_token: str | None = None
    token_type: str = "bearer"

    class Config:
        from_attributes = True

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


# Message Schemas
class MessageCreate(BaseModel):
    content: str
    role: str

class MessageResponse(BaseModel):
    id: UUID
    content: str
    role: str
    created_at: datetime

    class Config:    
        from_attributes = True

# Chat Schemas
class ChatCreate(BaseModel):
    title: str
    user_id: UUID

class ChatResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class FetchChatResponse(BaseModel):
    id: UUID
    title: str
    messages: list[MessageResponse]
    created_at: datetime