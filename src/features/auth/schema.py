# src/features/auth/schemas.py
from pydantic import BaseModel, EmailStr, Field

from typing import Optional
from datetime import datetime

class EmailSchema(BaseModel):
    email: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    nickname: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    nickname: str
    create_time: datetime
    is_active: bool

    class Config:
        from_attributes = True  # 替代 orm_mode（新版本写法）