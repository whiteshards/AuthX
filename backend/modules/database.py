
import os
from motor.motor_asyncio import AsyncIOMotorClient
from backend.typing.user import UserInDB
from datetime import datetime
from bson import ObjectId

class Database:
    client = None
    database = None
    
    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(os.getenv("MONGO"))
        cls.database = cls.client.AuthX
        
    @classmethod
    async def close(cls):
        cls.client.close()
        
    @classmethod
    async def create_user(cls, user_data: dict) -> str:
        user_data["created_at"] = datetime.utcnow()
        result = await cls.database.users.insert_one(user_data)
        return str(result.inserted_id)
        
    @classmethod
    async def get_user_by_email(cls, email: str) -> dict:
        user = await cls.database.users.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
        return user
        
    @classmethod
    async def get_user_by_username(cls, username: str) -> dict:
        user = await cls.database.users.find_one({"username": username})
        if user:
            user["id"] = str(user["_id"])
        return user
