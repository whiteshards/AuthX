
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

class UserInDB(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    hashed_password: str
    created_at: datetime
