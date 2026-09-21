from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id : str | None = None
    name : str | None = None
    email : EmailStr | None = None
    hashed_password : str | None = None


class TokenData(BaseModel):
    user_id : str | None = None