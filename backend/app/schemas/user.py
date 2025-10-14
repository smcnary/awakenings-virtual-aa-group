"""
Pydantic schemas for user management and authentication.
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from enum import Enum

from app.models.user import UserRole, ServicePosition


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    preferred_name: Optional[str] = Field(None, min_length=1, max_length=100)
    sobriety_date: Optional[date] = None
    timezone: str = Field(default="America/Chicago")
    language: str = Field(default="en")
    
    # Privacy settings
    show_sobriety_date: bool = Field(default=False)
    show_in_directory: bool = Field(default=True)
    allow_contact: bool = Field(default=False)
    
    # Notification preferences
    notification_preferences: Dict[str, bool] = Field(default={
        "email_notifications": True,
        "meeting_reminders": True,
        "service_updates": False,
        "marketing": False
    })


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    preferred_name: Optional[str] = Field(None, min_length=1, max_length=100)
    sobriety_date: Optional[date] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    
    # Privacy settings
    show_sobriety_date: Optional[bool] = None
    show_in_directory: Optional[bool] = None
    allow_contact: Optional[bool] = None
    
    # Notification preferences
    notification_preferences: Optional[Dict[str, bool]] = None
    
    @validator('notification_preferences')
    def validate_notification_preferences(cls, v):
        if v is not None:
            allowed_keys = {
                "email_notifications", "meeting_reminders", 
                "service_updates", "marketing"
            }
            if not all(key in allowed_keys for key in v.keys()):
                raise ValueError("Invalid notification preference keys")
        return v


class UserResponse(BaseModel):
    """Schema for user response (public profile)."""
    id: UUID
    preferred_name: Optional[str] = None
    sobriety_date: Optional[date] = None
    show_sobriety_date: bool
    show_in_directory: bool
    allow_contact: bool
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    # Service positions
    service_assignments: List['ServiceAssignmentResponse'] = []
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Schema for detailed user profile (own profile)."""
    id: UUID
    email: Optional[str] = None
    email_verified: bool
    phone: Optional[str] = None
    phone_verified: bool
    preferred_name: Optional[str] = None
    sobriety_date: Optional[date] = None
    timezone: str
    language: str
    show_sobriety_date: bool
    show_in_directory: bool
    allow_contact: bool
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    notification_preferences: Dict[str, bool]
    service_assignments: List['ServiceAssignmentResponse'] = []
    
    class Config:
        from_attributes = True


class ServiceAssignmentCreate(BaseModel):
    """Schema for creating service assignment."""
    position: ServicePosition
    group_id: Optional[UUID] = None
    meeting_id: Optional[UUID] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


class ServiceAssignmentUpdate(BaseModel):
    """Schema for updating service assignment."""
    position: Optional[ServicePosition] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class ServiceAssignmentResponse(BaseModel):
    """Schema for service assignment response."""
    id: UUID
    position: ServicePosition
    group_id: Optional[UUID] = None
    meeting_id: Optional[UUID] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MagicLinkRequest(BaseModel):
    """Schema for requesting magic link."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    purpose: str = Field(default="login")
    
    @validator('email', 'phone')
    def validate_contact_method(cls, v, values):
        if not v and not values.get('email') and not values.get('phone'):
            raise ValueError("Either email or phone must be provided")
        return v


class MagicLinkVerify(BaseModel):
    """Schema for verifying magic link."""
    token: str = Field(..., min_length=32, max_length=255)


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfileResponse


class TokenRefresh(BaseModel):
    """Schema for token refresh."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordReset(BaseModel):
    """Schema for password reset."""
    token: str = Field(..., min_length=32, max_length=255)
    new_password: str = Field(..., min_length=8, max_length=128)


class UserListResponse(BaseModel):
    """Schema for user list response (admin)."""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class UserStatsResponse(BaseModel):
    """Schema for user statistics (admin)."""
    total_users: int
    active_users: int
    new_users_this_month: int
    users_by_role: Dict[str, int]
    users_by_service_position: Dict[str, int]
    recent_logins: int


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: UUID
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    success: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MeetingAttendanceCreate(BaseModel):
    """Schema for meeting attendance."""
    meeting_id: UUID
    occurrence_id: Optional[UUID] = None
    share_attendance: bool = Field(default=False)
    anonymous_id: Optional[str] = None


class MeetingAttendanceResponse(BaseModel):
    """Schema for meeting attendance response."""
    id: UUID
    meeting_id: UUID
    occurrence_id: Optional[UUID] = None
    joined_at: datetime
    left_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    share_attendance: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Update forward references
UserResponse.model_rebuild()
UserProfileResponse.model_rebuild()
