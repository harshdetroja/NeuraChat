from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.models.db import User
from app.models.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

SessionDep = Annotated[Session, Depends(get_session)]

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception

    try:
        uid = UUID(token_data.user_id)
    except (ValueError, TypeError):
        raise credentials_exception

    user = session.exec(select(User).where(User.id == uid)).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_user_refresh(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception

    try:
        uid = UUID(token_data.user_id)
    except (ValueError, TypeError):
        raise credentials_exception

    user = session.exec(select(User).where(User.id == uid)).first()
    if user is None:
        raise credentials_exception 
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]
CurrentUserRefreshDep = Annotated[User, Depends(get_current_user_refresh)]