from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, create_engine, Session
from sqlalchemy import JSON
from enum import Enum

IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_now():
    return datetime.now(IST)

class FilesStatus(Enum):

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"

class MessageUser(str,Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"

class User(SQLModel, table=True):

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str | None = Field(default=None)
    hashed_password: str = Field(nullable=False, default=None)
    email: str = Field(nullable=False, unique=True)
    created_at: datetime = Field(default_factory=get_ist_now, nullable=False)

class Chat(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    title: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=get_ist_now, nullable=False)

    user_id: UUID | None = Field(default=None, foreign_key='user.id')

class File(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str | None = Field(default=None)
    file_size: int = Field(default=None)
    mime_type: str = Field(default=None)
    file_path: str = Field(default=None)
    status: str = Field(default=FilesStatus.PENDING.value)
    error_message: str = Field(default=None)
    created_at: datetime = Field(default_factory=get_ist_now, nullable=False)

    chat_id: UUID | None = Field(default=None, foreign_key='chat.id')

class Message(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    content: str | None = Field(default=None)
    role: str = Field(default=MessageUser.USER.value)
    citation: dict|list|None = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=get_ist_now, nullable=False)

    chat_id: UUID | None = Field(default=None, foreign_key='chat.id')


sqlite_file_name="neurachat.db"
sqlite_path=f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_path, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]