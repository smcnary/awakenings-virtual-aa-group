"""
Privacy service for AA Virtual platform.
Handles data anonymization, privacy controls, and compliance features.
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import hashlib
import secrets
import logging

from app.models.user import (
    User, UserAuditLog, LoginSession, MeetingAttendance, 
    ServiceAssignment, MagicLink
)

logger = logging.getLogger(__name__)


class PrivacyService:
    """Service for handling privacy controls and data anonymization."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for privacy compliance."""
        if not data:
            return None
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def generate_anonymous_id(self, prefix: str = "anon") -> str:
        """Generate anonymous identifier for privacy."""
        return f"{prefix}_{secrets.token_urlsafe(16)}"
    
    async def anonymize_user_data(self, user_id: str, preserve_audit: bool = True) -> bool:
        """Anonymize all user data while preserving system integrity."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Generate anonymous identifiers
            anonymous_id = self.generate_anonymous_id()
            
            # Anonymize user profile
            user.email = None
            user.phone = None
            user.preferred_name = f"Anonymous_{anonymous_id[:8]}"
            user.sobriety_date = None
            user.show_sobriety_date = False
            user.show_in_directory = False
            user.allow_contact = False
            user.is_active = False
            user.updated_at = datetime.utcnow()
            
            # Anonymize login sessions
            sessions = self.db.query(LoginSession).filter(
                LoginSession.user_id == user_id
            ).all()
            
            for session in sessions:
                session.device_fingerprint = self.hash_sensitive_data(session.device_fingerprint)
                session.user_agent_hash = self.hash_sensitive_data(session.user_agent_hash)
                session.ip_hash = self.hash_sensitive_data(session.ip_hash)
            
            # Anonymize meeting attendance
            attendance_records = self.db.query(MeetingAttendance).filter(
                MeetingAttendance.user_id == user_id
            ).all()
            
            for attendance in attendance_records:
                attendance.anonymous_id = self.generate_anonymous_id("attendance")
                attendance.share_attendance = False
            
            # Anonymize service assignments
            assignments = self.db.query(ServiceAssignment).filter(
                ServiceAssignment.user_id == user_id
            ).all()
            
            for assignment in assignments:
                assignment.notes = "Anonymized service assignment"
            
            # Anonymize magic links
            magic_links = self.db.query(MagicLink).filter(
                MagicLink.email == user.email or MagicLink.phone == user.phone
            ).all()
            
            for link in magic_links:
                link.email = None
                link.phone = None
                link.used_by_ip = self.hash_sensitive_data(link.used_by_ip)
            
            # Conditionally anonymize audit logs
            if not preserve_audit:
                audit_logs = self.db.query(UserAuditLog).filter(
                    UserAuditLog.user_id == user_id
                ).all()
                
                for log in audit_logs:
                    log.user_id = None
                    log.resource_id = None
                    log.ip_hash = self.hash_sensitive_data(log.ip_hash)
                    log.user_agent_hash = self.hash_sensitive_data(log.user_agent_hash)
            
            self.db.commit()
            logger.info(f"Anonymized all data for user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error anonymizing user data: {str(e)}")
            return False
    
    async def enforce_privacy_settings(self, user: User) -> Dict[str, Any]:
        """Enforce user privacy settings and return filtered data."""
        try:
            # Base user data
            user_data = {
                "id": str(user.id),
                "preferred_name": user.preferred_name if user.show_in_directory else "Anonymous",
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_login": user.last_login if user.show_in_directory else None
            }
            
            # Conditional data based on privacy settings
            if user.show_sobriety_date and user.sobriety_date:
                user_data["sobriety_date"] = user.sobriety_date
                # Ensure both dates are date objects
                today = datetime.utcnow().date()
                sobriety_date = user.sobriety_date.date() if hasattr(user.sobriety_date, 'date') else user.sobriety_date
                user_data["sobriety_days"] = (today - sobriety_date).days
            
            if user.allow_contact:
                user_data["contact_allowed"] = True
            else:
                user_data["contact_allowed"] = False
            
            # Service positions (always visible for service purposes)
            if user.service_assignments:
                user_data["service_positions"] = [
                    {
                        "position": assignment.position.value,
                        "is_active": assignment.is_active,
                        "start_date": assignment.start_date
                    }
                    for assignment in user.service_assignments
                    if assignment.is_active
                ]
            
            return user_data
            
        except Exception as e:
            logger.error(f"Error enforcing privacy settings: {str(e)}")
            return {"error": "Privacy enforcement failed"}
    
    async def get_privacy_compliant_user_list(
        self, 
        current_user: User,
        include_inactive: bool = False,
        role_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get list of users with privacy controls applied."""
        try:
            query = self.db.query(User)
            
            # Apply filters
            if not include_inactive:
                query = query.filter(User.is_active == True)
            
            if role_filter:
                query = query.filter(User.role == role_filter)
            
            # Only show users who opted into directory
            users = query.filter(User.show_in_directory == True).all()
            
            # Apply privacy controls
            privacy_compliant_users = []
            for user in users:
                user_data = await self.enforce_privacy_settings(user)
                privacy_compliant_users.append(user_data)
            
            return privacy_compliant_users
            
        except Exception as e:
            logger.error(f"Error getting privacy compliant user list: {str(e)}")
            return []
    
    async def create_anonymous_user_profile(self, service_position: Optional[str] = None) -> User:
        """Create anonymous user profile for service purposes."""
        try:
            anonymous_id = self.generate_anonymous_id()
            
            user = User(
                role="anonymous",
                preferred_name=f"Anonymous_{anonymous_id[:8]}",
                is_active=True,
                is_verified=False,
                show_in_directory=False,
                allow_contact=False,
                show_sobriety_date=False,
                notification_preferences={
                    "email_notifications": False,
                    "meeting_reminders": True,
                    "service_updates": False,
                    "marketing": False
                }
            )
            
            self.db.add(user)
            self.db.flush()
            
            # Create service assignment if position specified
            if service_position:
                from app.models.user import ServiceAssignment, ServicePosition
                
                assignment = ServiceAssignment(
                    user_id=user.id,
                    position=ServicePosition(service_position),
                    start_date=datetime.utcnow(),
                    notes=f"Anonymous service assignment for {service_position}",
                    is_active=True
                )
                
                self.db.add(assignment)
            
            # Log anonymous user creation
            audit_log = UserAuditLog(
                user_id=user.id,
                action="anonymous_user_created",
                resource_type="user",
                resource_id=str(user.id),
                success=True
            )
            self.db.add(audit_log)
            self.db.commit()
            
            logger.info(f"Created anonymous user {user.id} for service position {service_position}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating anonymous user: {str(e)}")
            raise
    
    async def audit_privacy_compliance(self, user_id: str) -> Dict[str, Any]:
        """Audit user's privacy compliance and data handling."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            # Check privacy settings
            privacy_score = 0
            max_score = 8
            
            if not user.email:
                privacy_score += 1  # No email = more private
            if not user.phone:
                privacy_score += 1  # No phone = more private
            if not user.show_sobriety_date:
                privacy_score += 1  # Sobriety date hidden = more private
            if not user.show_in_directory:
                privacy_score += 1  # Not in directory = more private
            if not user.allow_contact:
                privacy_score += 1  # No contact allowed = more private
            if user.role == "anonymous":
                privacy_score += 2  # Anonymous role = most private
            if not user.is_verified:
                privacy_score += 1  # Unverified = more private
            
            # Check data retention
            data_retention = {
                "audit_logs": self.db.query(UserAuditLog).filter(
                    UserAuditLog.user_id == user_id
                ).count(),
                "login_sessions": self.db.query(LoginSession).filter(
                    LoginSession.user_id == user_id
                ).count(),
                "meeting_attendance": self.db.query(MeetingAttendance).filter(
                    MeetingAttendance.user_id == user_id
                ).count(),
                "service_assignments": self.db.query(ServiceAssignment).filter(
                    ServiceAssignment.user_id == user_id
                ).count()
            }
            
            # Calculate privacy level
            privacy_percentage = (privacy_score / max_score) * 100
            
            if privacy_percentage >= 80:
                privacy_level = "Maximum"
            elif privacy_percentage >= 60:
                privacy_level = "High"
            elif privacy_percentage >= 40:
                privacy_level = "Medium"
            else:
                privacy_level = "Low"
            
            return {
                "user_id": str(user_id),
                "privacy_score": privacy_score,
                "max_score": max_score,
                "privacy_percentage": round(privacy_percentage, 2),
                "privacy_level": privacy_level,
                "data_retention": data_retention,
                "recommendations": self._get_privacy_recommendations(privacy_score, max_score)
            }
            
        except Exception as e:
            logger.error(f"Error auditing privacy compliance: {str(e)}")
            return {"error": "Privacy audit failed"}
    
    def _get_privacy_recommendations(self, score: int, max_score: int) -> List[str]:
        """Get privacy recommendations based on score."""
        recommendations = []
        
        if score < max_score * 0.5:  # Less than 50%
            recommendations.extend([
                "Consider using anonymous role for maximum privacy",
                "Disable directory visibility",
                "Hide sobriety date",
                "Disable contact permissions"
            ])
        
        if score < max_score * 0.75:  # Less than 75%
            recommendations.extend([
                "Review data retention policies",
                "Consider anonymizing old audit logs",
                "Regularly clean up inactive sessions"
            ])
        
        return recommendations
