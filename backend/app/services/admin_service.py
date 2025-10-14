"""
Admin service for AA Virtual platform.
Handles user management, service assignments, and administrative functions with privacy controls.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import logging

from app.models.user import (
    User, ServiceAssignment, UserRole, ServicePosition, 
    UserAuditLog, LoginSession, MeetingAttendance
)
from app.schemas.user import (
    UserCreate, UserUpdate, UserListResponse, UserResponse, 
    ServiceAssignmentCreate, ServiceAssignmentUpdate
)

logger = logging.getLogger(__name__)


class AdminService:
    """Service for administrative functions with privacy controls."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(
        self, 
        user_create: UserCreate, 
        created_by: str,
        role: UserRole = UserRole.GUEST
    ) -> User:
        """Create a new user with privacy controls."""
        try:
            # Check for existing user with same email/phone
            existing_user = None
            if user_create.email:
                existing_user = self.db.query(User).filter(User.email == user_create.email).first()
            elif user_create.phone:
                existing_user = self.db.query(User).filter(User.phone == user_create.phone).first()
            
            if existing_user:
                raise ValueError("User with this email or phone already exists")
            
            # Create user with privacy-first defaults
            user_data = user_create.dict()
            user_data.update({
                "role": role,
                "is_active": True,
                "is_verified": False,  # Requires manual verification for admin-created users
                "show_in_directory": False,  # Default to hidden for privacy
                "allow_contact": False,  # Default to no contact for privacy
            })
            
            # Generate anonymous identifier if no name provided
            if not user_data.get("preferred_name"):
                anonymous_id = secrets.token_urlsafe(8)
                user_data["preferred_name"] = f"Member_{anonymous_id}"
            
            user = User(**user_data)
            self.db.add(user)
            self.db.flush()  # Get the user ID
            
            # Log user creation
            audit_log = UserAuditLog(
                user_id=user.id,
                action="user_created_by_admin",
                resource_type="user",
                resource_id=user.id,
                success=True
            )
            self.db.add(audit_log)
            self.db.commit()
            
            logger.info(f"Admin {created_by} created user {user.id} with role {role}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def update_user(
        self, 
        user_id: str, 
        user_update: UserUpdate,
        updated_by: str
    ) -> User:
        """Update user with privacy controls."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Update user fields
            update_data = user_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            
            # Log user update
            audit_log = UserAuditLog(
                user_id=user_id,
                action="user_updated_by_admin",
                resource_type="user",
                resource_id=user_id,
                success=True
            )
            self.db.add(audit_log)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Admin {updated_by} updated user {user_id}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user: {str(e)}")
            raise
    
    async def get_users(
        self,
        page: int = 1,
        per_page: int = 20,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> UserListResponse:
        """Get paginated list of users with privacy controls."""
        try:
            query = self.db.query(User)
            
            # Apply filters
            if role:
                query = query.filter(User.role == role)
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        User.preferred_name.ilike(search_term),
                        User.email.ilike(search_term) if search else None
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * per_page
            users = query.order_by(desc(User.created_at)).offset(offset).limit(per_page).all()
            
            # Convert to response format with privacy controls
            user_responses = []
            for user in users:
                user_response = UserResponse.from_orm(user)
                # Remove sensitive data based on privacy settings
                if not user.show_sobriety_date:
                    user_response.sobriety_date = None
                user_responses.append(user_response)
            
            total_pages = (total + per_page - 1) // per_page
            
            return UserListResponse(
                users=user_responses,
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            raise
    
    async def delete_user(
        self, 
        user_id: str, 
        deleted_by: str,
        permanent: bool = False
    ) -> bool:
        """Delete user account with privacy controls."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            if permanent:
                # Hard delete - anonymize all related data first
                await self._anonymize_user_data(user_id)
                self.db.delete(user)
            else:
                # Soft delete - preserve data but mark as inactive
                user.is_active = False
                user.email = None
                user.phone = None
                user.preferred_name = f"Deleted_User_{secrets.token_urlsafe(8)}"
                user.updated_at = datetime.utcnow()
                
                # Invalidate all sessions
                self.db.query(LoginSession).filter(
                    LoginSession.user_id == user_id
                ).update({"is_active": False})
            
            # Log deletion
            audit_log = UserAuditLog(
                user_id=user_id,
                action="user_deleted_by_admin" if permanent else "user_deactivated_by_admin",
                resource_type="user",
                resource_id=user_id,
                success=True
            )
            self.db.add(audit_log)
            self.db.commit()
            
            logger.info(f"Admin {deleted_by} {'deleted' if permanent else 'deactivated'} user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            raise
    
    async def _anonymize_user_data(self, user_id: str):
        """Anonymize all user-related data for privacy compliance."""
        try:
            # Anonymize audit logs
            self.db.query(UserAuditLog).filter(
                UserAuditLog.user_id == user_id
            ).update({
                "user_id": None,
                "resource_id": None
            })
            
            # Anonymize login sessions
            self.db.query(LoginSession).filter(
                LoginSession.user_id == user_id
            ).update({
                "user_id": None,
                "device_fingerprint": None,
                "user_agent_hash": None,
                "ip_hash": None
            })
            
            # Anonymize meeting attendance
            self.db.query(MeetingAttendance).filter(
                MeetingAttendance.user_id == user_id
            ).update({
                "user_id": None,
                "anonymous_id": f"anon_{secrets.token_urlsafe(16)}"
            })
            
            # Anonymize service assignments
            self.db.query(ServiceAssignment).filter(
                ServiceAssignment.user_id == user_id
            ).update({
                "user_id": None,
                "notes": "Anonymized service assignment"
            })
            
            logger.info(f"Anonymized all data for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error anonymizing user data: {str(e)}")
            raise
    
    async def create_service_assignment(
        self,
        user_id: str,
        assignment_data: ServiceAssignmentCreate,
        created_by: str
    ) -> ServiceAssignment:
        """Create service assignment for user."""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Check for existing active assignment
            existing = self.db.query(ServiceAssignment).filter(
                ServiceAssignment.user_id == user_id,
                ServiceAssignment.position == assignment_data.position,
                ServiceAssignment.is_active == True
            ).first()
            
            if existing:
                raise ValueError(f"User already has active assignment for position {assignment_data.position}")
            
            assignment = ServiceAssignment(
                user_id=user_id,
                position=assignment_data.position,
                group_id=assignment_data.group_id,
                meeting_id=assignment_data.meeting_id,
                start_date=assignment_data.start_date,
                end_date=assignment_data.end_date,
                notes=assignment_data.notes,
                is_active=True,
                created_by=created_by
            )
            
            self.db.add(assignment)
            self.db.commit()
            self.db.refresh(assignment)
            
            # Log assignment creation
            audit_log = UserAuditLog(
                user_id=user_id,
                action="service_assignment_created",
                resource_type="service_assignment",
                resource_id=str(assignment.id),
                success=True
            )
            self.db.add(audit_log)
            self.db.commit()
            
            logger.info(f"Admin {created_by} created service assignment {assignment.id} for user {user_id}")
            return assignment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating service assignment: {str(e)}")
            raise
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics with privacy controls."""
        try:
            # Basic counts (no PII)
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.is_active == True).count()
            
            # New users this month
            month_ago = datetime.utcnow() - timedelta(days=30)
            new_users_this_month = self.db.query(User).filter(
                User.created_at >= month_ago
            ).count()
            
            # Users by role
            users_by_role = {}
            for role in UserRole:
                count = self.db.query(User).filter(User.role == role).count()
                users_by_role[role.value] = count
            
            # Users by service position
            users_by_service_position = {}
            for position in ServicePosition:
                count = self.db.query(ServiceAssignment).filter(
                    ServiceAssignment.position == position,
                    ServiceAssignment.is_active == True
                ).count()
                users_by_service_position[position.value] = count
            
            # Recent logins (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_logins = self.db.query(User).filter(
                User.last_login >= week_ago
            ).count()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "new_users_this_month": new_users_this_month,
                "users_by_role": users_by_role,
                "users_by_service_position": users_by_service_position,
                "recent_logins": recent_logins
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            raise
