
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from backend.typing.user import UserCreate, UserResponse
from modules.database import Database
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/v1/users")
security = HTTPBearer()

@router.post("/register", response_model=dict)
@limiter.limit("5/minute")
async def register_user(request, user: UserCreate):
    existing_email = await Database.get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    existing_username = await Database.get_user_by_username(user.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password.decode('utf-8')
    }
    
    user_id = await Database.create_user(user_data)
    
    token = jwt.encode({
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=30)
    }, os.getenv("JWT_SECRET", "fallback-secret"), algorithm="HS256")
    
    return {
        "message": "User registered successfully",
        "token": token,
        "user_id": user_id
    }

@router.post("/login", response_model=dict)
@limiter.limit("10/minute")
async def login_user(request, email: str, password: str):
    user = await Database.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.checkpw(password.encode('utf-8'), user["hashed_password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode({
        "user_id": user["id"],
        "exp": datetime.utcnow() + timedelta(days=30)
    }, os.getenv("JWT_SECRET", "fallback-secret"), algorithm="HS256")
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    }
