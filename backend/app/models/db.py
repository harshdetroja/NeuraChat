from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from enum import Enum

IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now():
    return datetime.now(IST)

class FilesStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"

class MessageRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"

class User(SQLModel, table=True):
    __tablename__ = "user"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str | None = Field(default=None)
    hashed_password: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True, index=True)
    created_at: datetime = Field(default_factory=get_ist_now, nullable=False)

class Chat(SQLModel, table=True):
    __tablename__ = "chat"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str | None = Field(default="New Chat")
    created_at: datetime = Field(default_factory=get_ist_now, nullable=False)
    user_id: UUID = Field(foreign_key="user.id")

class File(SQLModel, table=True):
    __tablename__ = "file"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)
    file_size: int = Field(default=0)
    mime_type: str = Field(default="application/octet-stream")
    file_path: str = Field(nullable=False)
    status: str = Field(default=FilesStatus.PENDING.value)
    error_message: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=get_ist_now, nullable=False)
    chat_id: UUID = Field(foreign_key="chat.id")

class Message(SQLModel, table=True):
    __tablename__ = "message"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    content: str = Field(nullable=False)
    role: str = Field(default=MessageRole.USER.value)
    citation: dict | list | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=get_ist_now, nullable=False)
    chat_id: UUID = Field(foreign_key="chat.id")

