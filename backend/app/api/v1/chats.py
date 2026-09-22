from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select
from app.api.deps import SessionDep, CurrentUserDep
from app.models.db import Chat, Message
from app.models.schemas import ChatCreate, ChatResponse, FetchChatResponse, MessageResponse

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.get("/", response_model=list[ChatResponse])
def get_chats(current_user: CurrentUserDep, session: SessionDep):
    chats = session.exec(select(Chat).where(Chat.user_id == current_user.id)).all()
    return chats

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(chat_in: ChatCreate, current_user: CurrentUserDep, session: SessionDep):
    chat = Chat(
        title=chat_in.title,
        user_id=current_user.id
    )
    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat

@router.get("/{chat_id}", response_model=FetchChatResponse)
def get_chat(chat_id: UUID, current_user: CurrentUserDep, session: SessionDep):
    chat = session.exec(select(Chat).where(Chat.id == chat_id)).first()
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to view this chat"
        )
    
    messages = session.exec(select(Message).where(Message.chat_id == chat_id)).all()

    return FetchChatResponse(
        id=chat.id,
        title=chat.title,
        messages=[MessageResponse.model_validate(message) for message in messages],
        created_at=chat.created_at
    )

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(chat_id: UUID, current_user: CurrentUserDep, session: SessionDep):
    chat = session.exec(select(Chat).where(Chat.id == chat_id)).first()
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to delete this chat"
        )
    session.delete(chat)
    session.commit()
    return