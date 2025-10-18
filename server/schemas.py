"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


class MessageCreate(BaseModel):
    """Schema for creating a message"""
    content: str
    room_id: str = "general"


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: int
    user_id: int
    username: str
    content: str
    timestamp: datetime
    room_id: str

    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages"""
    type: str  # "message", "user_joined", "user_left", "heartbeat"
    content: Optional[str] = None
    username: Optional[str] = None
    user_id: Optional[int] = None
    timestamp: Optional[str] = None
