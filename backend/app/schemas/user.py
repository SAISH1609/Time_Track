from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    timezone: Optional[str] = "UTC"


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


# Properties to return via API
class User(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    avatar_url: Optional[str] = None
    default_project_id: Optional[int] = None

    class Config:
        from_attributes = True


# Authentication schemas
class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[int] = None


# User profile schemas
class UserProfile(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserSettings(BaseModel):
    timezone: Optional[str] = None
    default_project_id: Optional[int] = None
    notification_preferences: Optional[dict] = None
    ace_integration_settings: Optional[dict] = None
