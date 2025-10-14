"""
Chatbot models for AA Virtual platform.
Handles chat sessions, messages, and conversation analytics while maintaining privacy.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class ChatSession(Base):
    """Represents a chat session with the AA Virtual chatbot."""
    
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_token = Column(String(64), unique=True, nullable=False, index=True)
    user_type = Column(String(20), nullable=False, default="anonymous")  # anonymous, guest, member
    ip_hash = Column(String(64), nullable=True)  # Hashed IP for rate limiting
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Privacy settings
    retain_history = Column(Boolean, default=False)  # User consent for history retention
    retention_days = Column(Integer, default=7)  # How long to keep messages
    
    # Analytics (aggregated, no PII)
    message_count = Column(Integer, default=0)
    topics_discussed = Column(JSON, default=list)
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 scale
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Individual messages within a chat session."""
    
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    
    # Message content
    role = Column(String(10), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, quick_reply, link, resource
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_time_ms = Column(Integer, nullable=True)
    
    # Context for better responses
    detected_intent = Column(String(50), nullable=True)  # meeting_info, resources, crisis, general
    confidence_score = Column(Integer, nullable=True)  # 0-100
    
    # Quick reply options (for assistant messages)
    quick_replies = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class ChatResource(Base):
    """Resources that can be shared through the chatbot."""
    
    __tablename__ = "chat_resources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Resource details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String(30), nullable=False)  # document, link, meeting, contact
    url = Column(String(500), nullable=True)
    file_path = Column(String(300), nullable=True)
    
    # Categorization
    category = Column(String(50), nullable=False)  # meetings, literature, crisis, service
    tags = Column(JSON, default=list)
    priority = Column(Integer, default=1)  # 1-5, higher = more important
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChatAnalytics(Base):
    """Aggregated analytics for chatbot usage (no PII)."""
    
    __tablename__ = "chat_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Session metrics
    total_sessions = Column(Integer, default=0)
    new_sessions = Column(Integer, default=0)
    returning_sessions = Column(Integer, default=0)
    
    # Message metrics
    total_messages = Column(Integer, default=0)
    user_messages = Column(Integer, default=0)
    assistant_messages = Column(Integer, default=0)
    
    # Intent analysis
    intent_counts = Column(JSON, default=dict)  # {"meeting_info": 45, "crisis": 3, ...}
    
    # Performance metrics
    avg_response_time_ms = Column(Integer, nullable=True)
    satisfaction_ratings = Column(JSON, default=list)  # [4, 5, 3, ...]
    
    # Geographic (country/region level only)
    top_countries = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
