from abs_repository_core.schemas import ModelBaseInfo, make_optional, FindBase
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime
    
    class Config:
        extra = "allow"


class SafeIntegration(make_optional(ModelBaseInfo)):
    provider_name: str
    user_id: int
    email: Optional[EmailStr] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class Integration(TokenData, SafeIntegration):
    pass


class IsConnectedResponse(BaseModel):
    connected: bool
    is_active: bool


class CreateIntegration(BaseModel):
    """Model for creating a new integration"""
    provider_name: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    user_id: int
    email: Optional[EmailStr] = None
    is_active: bool = True


class UpdateIntegration(BaseModel):
    """Model for updating an existing integration"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

    class Config:
        extra = "ignore"
