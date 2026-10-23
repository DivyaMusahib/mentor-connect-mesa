from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    avatar_url: Optional[str] = None
    role: str  # "student" | "admin"
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DemoLoginRequest(BaseModel):
    role: str = "student"  # "student" | "admin"
    full_name: Optional[str] = None
    email: Optional[str] = None


class GoogleOAuthUrlResponse(BaseModel):
    authorization_url: str
    state: str


class SessionInfoResponse(BaseModel):
    authenticated: bool
    user: Optional[UserResponse] = None
    session_id: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
