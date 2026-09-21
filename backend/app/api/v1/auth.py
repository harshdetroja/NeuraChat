from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.api.deps import SessionDep, CurrentUserDep
from app.core.security import get_hashed_password, verify_password, create_access_token, create_refresh_token
from app.models.db import User
from app.models.schemas import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, session: SessionDep):
    existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=get_hashed_password(user_in.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, session: SessionDep):
    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

@router.post("/token", response_model=Token)
def login_form(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    # Compatible with Swagger UI 'Authorize' button
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: CurrentUserDep):
    return current_user

