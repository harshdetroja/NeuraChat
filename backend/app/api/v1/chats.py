from uuid import UUID
from fastapi import APIRouter, HTTPException, UploadFile, status, File as FastAPIFile
from sqlmodel import Session, select
from app.api.deps import SessionDep, CurrentUserDep
from app.models.db import Chat, FilesStatus, Message, File
from app.models.schemas import ChatCreate, ChatResponse, FetchChatResponse, MessageResponse, FileResponse
from app.core.config import settings
from app.services.storage import storage_service

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
            status_code=status.HTTP_403_FORBIDDEN,
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this chat"
        )
    session.delete(chat)
    session.commit()
    return


@router.post("/{chat_id}/files", response_model=list[FileResponse])
async def upload_file(chat_id: UUID, current_user: CurrentUserDep, session: SessionDep, files: list[UploadFile] = FastAPIFile(...)):
    chat = session.exec(select(Chat).where(Chat.id == chat_id)).first()
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to upload files to this chat"
        )
    existing_files = session.exec(select(File).where(File.chat_id == chat_id)).all()
    file_count = len(files) + len(existing_files)
    if file_count > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only upload up to 5 files at a time"
        )
    
    total_size = 0
    for file in files:
        total_size += file.size
    if total_size > settings.MAX_TOTAL_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only upload files up to 50MB at a time"
        )
    
    db_files = []
    for file in files:

        object_key = f"chats/{chat_id}/{uuid4().hex[:8]}_{file.filename}"
        file_bytes = await file.read()
        fobject_key = storage_service.upload_file_to_s3(file_bytes, object_key, file.content_type)
        db_file = File(
            name=file.filename,
            file_path=fobject_key,
            file_size=file.size,
            mime_type=file.content_type,
            status=FilesStatus.PENDING.value,
            chat_id=chat_id
        )
        session.add(db_file)
        db_files.append(db_file)
    session.commit()
    for db_file in db_files:
        session.refresh(db_file)
    return db_files

@router.get("/{chat_id}/files", response_model=list[FileResponse])
def get_files(chat_id: UUID, current_user: CurrentUserDep, session: SessionDep):
    chat = session.exec(select(Chat).where(Chat.id == chat_id)).first()
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view files in this chat"
        )
    
    files = session.exec(select(File).where(File.chat_id == chat_id)).all()

    return [FileResponse.model_validate(file) for file in files]


@router.delete("/{chat_id}/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(chat_id: UUID, file_id: UUID, current_user: CurrentUserDep, session: SessionDep):
    chat = session.exec(select(Chat).where(Chat.id == chat_id)).first()
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete files in this chat"
        )
    
    file = session.exec(select(File).where(File.id == file_id)).first()
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    if file.chat_id != chat_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this file"
        )
    storage_service.delete_file_from_s3(file.file_path)
    session.delete(file)
    session.commit()    
    return