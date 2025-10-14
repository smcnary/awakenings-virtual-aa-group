"""
Authentication service for AA Virtual platform.
Handles user authentication, session management, and security.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import secrets
import hashlib

from app.models.user import User, LoginSession
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_login_session(
        self, 
        user_id: str, 
        device_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """Create a new login session for a user."""
        
        # Generate session tokens
        session_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        
        # Create session record
        session = LoginSession(
            user_id=user_id,
            session_token=session_token,
            refresh_token=refresh_token,
            device_fingerprint=hashlib.sha256(
                str(device_info).encode()
            ).hexdigest()[:64],
            user_agent_hash=hashlib.sha256(
                device_info.get("user_agent", "").encode()
            ).hexdigest()[:64] if device_info.get("user_agent") else None,
            ip_hash=hashlib.sha256(
                device_info.get("ip", "").encode()
            ).hexdigest()[:64] if device_info.get("ip") else None,
            expires_at=datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        )
        
        self.db.add(session)
        self.db.flush()  # Get the session ID
        
        # Create JWT tokens
        access_token = create_access_token(
            data={"sub": user_id, "session_id": str(session.id)}
        )
        
        refresh_token_jwt = create_refresh_token(
            data={"sub": user_id, "session_id": str(session.id)}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_jwt,
            "session_id": str(session.id)
        }
    
    async def refresh_session_tokens(self, session_id: str) -> Dict[str, str]:
        """Refresh tokens for an existing session."""
        
        session = self.db.query(LoginSession).filter(
            LoginSession.id == session_id
        ).first()
        
        if not session:
            raise ValueError("Session not found")
        
        # Update session expiry
        session.expires_at = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        session.last_activity = datetime.utcnow()
        
        # Create new tokens
        access_token = create_access_token(
            data={"sub": str(session.user_id), "session_id": str(session.id)}
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(session.user_id), "session_id": str(session.id)}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        session = self.db.query(LoginSession).filter(
            LoginSession.id == session_id
        ).first()
        
        if session:
            session.is_active = False
            self.db.commit()
            return True
        
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        expired_sessions = self.db.query(LoginSession).filter(
            LoginSession.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired_sessions)
        for session in expired_sessions:
            session.is_active = False
        
        self.db.commit()
        return count
