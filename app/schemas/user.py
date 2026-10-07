from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.item import ItemRead


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["alice"])
    email: str = Field(..., min_length=5, max_length=100, examples=["alice@example.com"])
    role: str = Field(default="user", max_length=20, examples=["admin", "user"])


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, min_length=5, max_length=100)
    role: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    items: List[ItemRead] = []

    model_config = ConfigDict(from_attributes=True)
