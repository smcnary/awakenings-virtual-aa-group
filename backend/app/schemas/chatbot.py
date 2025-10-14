"""
Pydantic schemas for chatbot functionality.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID


class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session."""
    user_type: str = Field(default="anonymous", description="Type of user: anonymous, guest, member")
    retain_history: bool = Field(default=False, description="Whether to retain chat history")
    retention_days: int = Field(default=7, ge=1, le=30, description="Days to retain history")


class ChatSessionResponse(BaseModel):
    """Schema for chat session response."""
    id: UUID
    session_token: str
    user_type: str
    is_active: bool
    retain_history: bool
    retention_days: int
    message_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    message_type: str = Field(default="text", description="Type of message")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    id: UUID
    role: str
    content: str
    message_type: str
    created_at: datetime
    processing_time_ms: Optional[int] = None
    detected_intent: Optional[str] = None
    confidence_score: Optional[int] = None
    quick_replies: Optional[List[Dict[str, str]]] = None
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Schema for complete chat response."""
    message: ChatMessageResponse
    session: ChatSessionResponse
    suggestions: Optional[List[str]] = None
    resources: Optional[List[Dict[str, Any]]] = None


class ChatResourceResponse(BaseModel):
    """Schema for chat resource response."""
    id: UUID
    title: str
    description: Optional[str] = None
    resource_type: str
    url: Optional[str] = None
    category: str
    tags: List[str] = []
    priority: int
    
    class Config:
        from_attributes = True


class ChatAnalyticsResponse(BaseModel):
    """Schema for chat analytics response."""
    date: datetime
    total_sessions: int
    new_sessions: int
    total_messages: int
    intent_counts: Dict[str, int] = {}
    avg_response_time_ms: Optional[int] = None
    satisfaction_ratings: List[int] = []
    
    class Config:
        from_attributes = True


class QuickReply(BaseModel):
    """Schema for quick reply options."""
    text: str = Field(..., min_length=1, max_length=100)
    payload: str = Field(..., min_length=1, max_length=50)


class ChatbotConfig(BaseModel):
    """Schema for chatbot configuration."""
    max_message_length: int = Field(default=2000, ge=100, le=5000)
    max_session_messages: int = Field(default=50, ge=10, le=200)
    session_timeout_minutes: int = Field(default=30, ge=5, le=120)
    rate_limit_per_minute: int = Field(default=10, ge=1, le=100)
    enable_analytics: bool = Field(default=True)
    default_retention_days: int = Field(default=7, ge=1, le=30)
