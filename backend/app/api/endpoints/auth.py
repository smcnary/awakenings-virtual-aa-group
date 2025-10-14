"""
Authentication API endpoints for AA Virtual platform.
Handles magic link authentication, JWT tokens, and user management.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import secrets
import hashlib
import time
from datetime import datetime, timedelta
import logging

from app.db.database import get_db
from app.models.user import User, MagicLink, LoginSession, UserAuditLog, UserRole
from app.schemas.user import (
    UserCreate, UserUpdate, UserProfileResponse, UserResponse,
    MagicLinkRequest, MagicLinkVerify, LoginResponse, TokenRefresh,
    PasswordResetRequest, PasswordReset
)
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: list[UserRole]):
    """Decorator to require specific user roles."""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


@router.post("/magic-link", response_model=dict)
async def request_magic_link(
    request_data: MagicLinkRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request a magic link for passwordless authentication."""
    try:
        # Rate limiting check
        ip_hash = hashlib.sha256(request.client.host.encode()).hexdigest()
        
        # Check recent magic link requests
        recent_links = db.query(MagicLink).filter(
            MagicLink.email == request_data.email or MagicLink.phone == request_data.phone,
            MagicLink.created_at > time.time() - 300,  # 5 minutes
            MagicLink.is_used == False
        ).count()
        
        if recent_links > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Magic link already sent. Please check your email/phone."
            )
        
        # Generate magic link token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Create magic link record
        magic_link = MagicLink(
            token=token,
            email=request_data.email,
            phone=request_data.phone,
            purpose=request_data.purpose,
            expires_at=expires_at
        )
        
        db.add(magic_link)
        db.commit()
        
        # Send magic link via email or SMS
        if request_data.email:
            email_service = EmailService()
            await email_service.send_magic_link(
                email=request_data.email,
                token=token,
                purpose=request_data.purpose
            )
        
        # Log the request
        audit_log = UserAuditLog(
            action="magic_link_requested",
            ip_hash=ip_hash,
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"Magic link requested for {request_data.email or request_data.phone}")
        
        return {
            "message": "Magic link sent successfully",
            "expires_in": 15 * 60  # 15 minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting magic link: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error sending magic link"
        )


@router.post("/verify-magic-link", response_model=LoginResponse)
async def verify_magic_link(
    verify_data: MagicLinkVerify,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify magic link and create login session."""
    try:
        # Find and validate magic link
        magic_link = db.query(MagicLink).filter(
            MagicLink.token == verify_data.token,
            MagicLink.is_used == False,
            MagicLink.expires_at > datetime.utcnow()
        ).first()
        
        if not magic_link:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired magic link"
            )
        
        # Mark magic link as used
        magic_link.is_used = True
        magic_link.used_at = datetime.utcnow()
        magic_link.used_by_ip = request.client.host
        
        # Find or create user
        user = None
        if magic_link.email:
            user = db.query(User).filter(User.email == magic_link.email).first()
        elif magic_link.phone:
            user = db.query(User).filter(User.phone == magic_link.phone).first()
        
        if not user:
            # Create new user
            user = User(
                email=magic_link.email,
                phone=magic_link.phone,
                email_verified=bool(magic_link.email),
                phone_verified=bool(magic_link.phone),
                role=UserRole.GUEST
            )
            db.add(user)
            db.flush()  # Get the user ID
        
        # Update user verification status
        if magic_link.email and not user.email_verified:
            user.email_verified = True
        if magic_link.phone and not user.phone_verified:
            user.phone_verified = True
        
        user.last_login = datetime.utcnow()
        
        # Create login session
        auth_service = AuthService(db)
        session_data = await auth_service.create_login_session(
            user_id=user.id,
            device_info={
                "ip": request.client.host,
                "user_agent": request.headers.get("User-Agent", "")
            }
        )
        
        db.commit()
        
        # Log successful login
        audit_log = UserAuditLog(
            user_id=user.id,
            action="login",
            ip_hash=hashlib.sha256(request.client.host.encode()).hexdigest(),
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User {user.id} logged in successfully")
        
        return LoginResponse(
            access_token=session_data["access_token"],
            refresh_token=session_data["refresh_token"],
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserProfileResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying magic link: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying magic link"
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token, token_type="refresh")
        session_id = payload.get("session_id")
        
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Find active session
        session = db.query(LoginSession).filter(
            LoginSession.id == session_id,
            LoginSession.is_active == True,
            LoginSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
        
        # Update session activity
        session.last_activity = datetime.utcnow()
        
        # Create new tokens
        auth_service = AuthService(db)
        new_tokens = await auth_service.refresh_session_tokens(session_id)
        
        db.commit()
        
        return LoginResponse(
            access_token=new_tokens["access_token"],
            refresh_token=new_tokens["refresh_token"],
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserProfileResponse.from_orm(session.user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout user and invalidate session."""
    try:
        # Invalidate all active sessions for user
        db.query(LoginSession).filter(
            LoginSession.user_id == current_user.id,
            LoginSession.is_active == True
        ).update({"is_active": False})
        
        # Log logout
        audit_log = UserAuditLog(
            user_id=current_user.id,
            action="logout",
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User {current_user.id} logged out")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout"
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile."""
    return UserProfileResponse.from_orm(current_user)


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    try:
        # Update user fields
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
        # Log profile update
        audit_log = UserAuditLog(
            user_id=current_user.id,
            action="profile_updated",
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User {current_user.id} updated profile")
        
        return UserProfileResponse.from_orm(current_user)
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )


@router.post("/anonymous", response_model=LoginResponse)
async def create_anonymous_account(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create an anonymous user account - no email/phone required."""
    try:
        # Generate anonymous identifier
        anonymous_id = secrets.token_urlsafe(16)
        
        # Create anonymous user
        user = User(
            role=UserRole.ANONYMOUS,
            preferred_name=f"Anonymous_{anonymous_id[:8]}",
            is_verified=False,  # Anonymous users don't need verification
            show_in_directory=False,  # Anonymous users hidden by default
            allow_contact=False,  # Anonymous users don't allow contact
            notification_preferences={
                "email_notifications": False,
                "meeting_reminders": True,
                "service_updates": False,
                "marketing": False
            }
        )
        
        db.add(user)
        db.flush()  # Get the user ID
        
        # Create login session
        auth_service = AuthService(db)
        session_data = await auth_service.create_login_session(
            user_id=user.id,
            device_info={
                "ip": request.client.host,
                "user_agent": request.headers.get("User-Agent", ""),
                "anonymous": True
            }
        )
        
        db.commit()
        
        # Log anonymous account creation
        audit_log = UserAuditLog(
            user_id=user.id,
            action="anonymous_account_created",
            ip_hash=hashlib.sha256(request.client.host.encode()).hexdigest(),
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"Anonymous user {user.id} created successfully")
        
        return LoginResponse(
            access_token=session_data["access_token"],
            refresh_token=session_data["refresh_token"],
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserProfileResponse.from_orm(user)
        )
        
    except Exception as e:
        logger.error(f"Error creating anonymous account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating anonymous account"
        )


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete user account (soft delete)."""
    try:
        # Soft delete user
        current_user.is_active = False
        current_user.email = None
        current_user.phone = None
        current_user.preferred_name = None
        current_user.updated_at = datetime.utcnow()
        
        # Invalidate all sessions
        db.query(LoginSession).filter(
            LoginSession.user_id == current_user.id
        ).update({"is_active": False})
        
        # Log account deletion
        audit_log = UserAuditLog(
            user_id=current_user.id,
            action="account_deleted",
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"User {current_user.id} deleted account")
        
        return {"message": "Account deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting account"
        )
