from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict

class TaskStatus(str, Enum):
    pending = "в ожидании"
    in_progress = "в работе"
    completed = "завершено"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: int

class TaskCreate(TaskBase):
    pass

class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str
    priority: int
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    class Config:
        from_attributes = True