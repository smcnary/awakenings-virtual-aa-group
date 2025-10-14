"""
User models for AA Virtual platform.
Handles members, admins, and service positions with privacy-first approach.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system."""
    ANONYMOUS = "anonymous"
    GUEST = "guest"
    MEMBER = "member"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    HOST = "host"
    ADMIN = "admin"


class ServicePosition(str, enum.Enum):
    """Service positions within AA groups."""
    CHAIRPERSON = "chairperson"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    CHAIR = "chair"
    CO_CHAIR = "co_chair"
    HOST = "host"
    CO_HOST = "co_host"
    TECH_HOST = "tech_host"
    LITERATURE = "literature"
    OUTREACH = "outreach"
    TWELFTH_STEP = "twelfth_step"


class User(Base):
    """User account for AA Virtual platform."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=True, index=True)  # Optional for privacy
    email_verified = Column(Boolean, default=False)
    phone = Column(String(20), nullable=True, index=True)
    phone_verified = Column(Boolean, default=False)
    
    # Profile (minimal for privacy)
    preferred_name = Column(String(100), nullable=True)  # Not necessarily real name
    sobriety_date = Column(DateTime, nullable=True)  # Optional
    timezone = Column(String(50), default="America/Chicago")
    language = Column(String(10), default="en")
    
    # Privacy settings
    show_sobriety_date = Column(Boolean, default=False)
    show_in_directory = Column(Boolean, default=True)
    allow_contact = Column(Boolean, default=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.GUEST)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Preferences
    notification_preferences = Column(JSON, default={
        "email_notifications": True,
        "meeting_reminders": True,
        "service_updates": False,
        "marketing": False
    })
    
    # Relationships
    service_assignments = relationship("ServiceAssignment", foreign_keys="ServiceAssignment.user_id", back_populates="user", cascade="all, delete-orphan")
    login_sessions = relationship("LoginSession", foreign_keys="LoginSession.user_id", back_populates="user", cascade="all, delete-orphan")
    meeting_attendance = relationship("MeetingAttendance", foreign_keys="MeetingAttendance.user_id", back_populates="user")


class ServiceAssignment(Base):
    """Service position assignments for users."""
    
    __tablename__ = "service_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Service details
    position = Column(Enum(ServicePosition), nullable=False)
    group_id = Column(UUID(as_uuid=True), nullable=True)  # For group-specific roles
    meeting_id = Column(UUID(as_uuid=True), nullable=True)  # For meeting-specific roles
    
    # Assignment period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="service_assignments", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])


class LoginSession(Base):
    """Active login sessions for users."""
    
    __tablename__ = "login_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Session details
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True, index=True)
    
    # Device information (anonymized)
    device_fingerprint = Column(String(64), nullable=True)
    user_agent_hash = Column(String(64), nullable=True)
    ip_hash = Column(String(64), nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="login_sessions", foreign_keys=[user_id])


class MagicLink(Base):
    """Magic link tokens for passwordless authentication."""
    
    __tablename__ = "magic_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Link details
    token = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True, index=True)
    
    # Usage tracking
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    used_by_ip = Column(String(45), nullable=True)
    
    # Expiration
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Purpose
    purpose = Column(String(50), default="login")  # login, verify_email, verify_phone, reset_password


class UserAuditLog(Base):
    """Audit log for user actions (privacy-compliant)."""
    
    __tablename__ = "user_audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Action details
    action = Column(String(100), nullable=False)  # login, logout, profile_update, etc.
    resource_type = Column(String(50), nullable=True)  # user, meeting, budget, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Metadata (no PII)
    ip_hash = Column(String(64), nullable=True)
    user_agent_hash = Column(String(64), nullable=True)
    success = Column(Boolean, default=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


class MeetingAttendance(Base):
    """Meeting attendance records (optional, privacy-compliant)."""
    
    __tablename__ = "meeting_attendance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Optional for anonymous attendance
    meeting_id = Column(UUID(as_uuid=True), nullable=False)
    occurrence_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Attendance details
    joined_at = Column(DateTime, nullable=False)
    left_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Anonymous identifier (if user chooses not to be tracked)
    anonymous_id = Column(String(64), nullable=True, index=True)
    
    # Privacy settings
    share_attendance = Column(Boolean, default=False)  # Whether to share with group
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meeting_attendance", foreign_keys=[user_id])
