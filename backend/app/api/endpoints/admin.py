"""
Admin API endpoints for AA Virtual platform.
Handles user management, service assignments, and administrative functions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from app.db.database import get_db
from app.models.user import (
    User, ServiceAssignment, UserRole, ServicePosition, 
    UserAuditLog, LoginSession, MeetingAttendance
)
from app.schemas.user import (
    UserListResponse, UserResponse, UserStatsResponse, UserUpdate, UserCreate,
    ServiceAssignmentCreate, ServiceAssignmentUpdate, ServiceAssignmentResponse,
    AuditLogResponse
)
from app.api.endpoints.auth import require_role, get_current_active_user
from app.services.admin_service import AdminService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/users", response_model=UserListResponse)
async def get_users(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get list of users (admin/secretary only)."""
    try:
        admin_service = AdminService(db)
        result = await admin_service.get_users(
            page=page,
            per_page=per_page,
            role=role,
            is_active=is_active,
            search=search
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Create a new user (admin/secretary only)."""
    try:
        admin_service = AdminService(db)
        
        # Determine role based on current user permissions
        role = UserRole.ADMIN if current_user.role == UserRole.ADMIN else UserRole.GUEST
        
        new_user = await admin_service.create_user(
            user_create=user_create,
            created_by=current_user.id,
            role=role
        )
        
        logger.info(f"Admin {current_user.id} created user {new_user.id}")
        return UserResponse.from_orm(new_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Get user details (admin/secretary only)."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update user (admin only)."""
    try:
        admin_service = AdminService(db)
        updated_user = await admin_service.update_user(
            user_id=user_id,
            user_update=user_update,
            updated_by=current_user.id
        )
        
        logger.info(f"Admin {current_user.id} updated user {user_id}")
        return UserResponse.from_orm(updated_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: UserRole,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update user role (admin only)."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        old_role = user.role
        user.role = role
        user.updated_at = datetime.utcnow()
        
        # Log role change
        audit_log = UserAuditLog(
            user_id=user_id,
            action="role_updated",
            resource_type="user",
            resource_id=user_id,
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"Admin {current_user.id} changed user {user_id} role from {old_role} to {role}")
        
        return {"message": f"User role updated to {role.value}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user role"
        )


@router.get("/service-assignments", response_model=List[ServiceAssignmentResponse])
async def get_service_assignments(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db),
    position: Optional[ServicePosition] = Query(None),
    is_active: Optional[bool] = Query(None),
    group_id: Optional[str] = Query(None)
):
    """Get service assignments (admin/secretary only)."""
    query = db.query(ServiceAssignment)
    
    if position:
        query = query.filter(ServiceAssignment.position == position)
    
    if is_active is not None:
        query = query.filter(ServiceAssignment.is_active == is_active)
    
    if group_id:
        query = query.filter(ServiceAssignment.group_id == group_id)
    
    assignments = query.order_by(desc(ServiceAssignment.created_at)).all()
    return assignments


@router.post("/service-assignments", response_model=ServiceAssignmentResponse)
async def create_service_assignment(
    assignment_data: ServiceAssignmentCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Create service assignment (admin/secretary only)."""
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == assignment_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check for existing assignment
        existing = db.query(ServiceAssignment).filter(
            ServiceAssignment.user_id == assignment_data.user_id,
            ServiceAssignment.position == assignment_data.position,
            ServiceAssignment.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has this service position"
            )
        
        # Create assignment
        assignment = ServiceAssignment(
            user_id=assignment_data.user_id,
            position=assignment_data.position,
            group_id=assignment_data.group_id,
            meeting_id=assignment_data.meeting_id,
            start_date=assignment_data.start_date,
            end_date=assignment_data.end_date,
            notes=assignment_data.notes,
            is_active=True,
            created_by=current_user.id
        )
        
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        logger.info(f"Admin {current_user.id} created service assignment for user {assignment_data.user_id}")
        return assignment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating service assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating service assignment"
        )


@router.put("/service-assignments/{assignment_id}", response_model=ServiceAssignmentResponse)
async def update_service_assignment(
    assignment_id: str,
    assignment_update: ServiceAssignmentUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Update service assignment (admin/secretary only)."""
    try:
        assignment = db.query(ServiceAssignment).filter(
            ServiceAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service assignment not found"
            )
        
        # Update fields
        for field, value in assignment_update.dict(exclude_unset=True).items():
            setattr(assignment, field, value)
        
        assignment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(assignment)
        
        logger.info(f"Admin {current_user.id} updated service assignment {assignment_id}")
        return assignment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating service assignment"
        )


@router.delete("/service-assignments/{assignment_id}")
async def delete_service_assignment(
    assignment_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Delete service assignment (admin/secretary only)."""
    try:
        assignment = db.query(ServiceAssignment).filter(
            ServiceAssignment.id == assignment_id
        ).first()
        
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service assignment not found"
            )
        
        # Soft delete
        assignment.is_active = False
        assignment.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Admin {current_user.id} deleted service assignment {assignment_id}")
        return {"message": "Service assignment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting service assignment"
        )


@router.get("/stats", response_model=UserStatsResponse)
async def get_admin_stats(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Get admin statistics."""
    try:
        # Total users
        total_users = db.query(User).count()
        
        # Active users
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # New users this month
        month_ago = datetime.utcnow() - timedelta(days=30)
        new_users_this_month = db.query(User).filter(
            User.created_at >= month_ago
        ).count()
        
        # Users by role
        users_by_role = {}
        for role in UserRole:
            count = db.query(User).filter(User.role == role).count()
            users_by_role[role.value] = count
        
        # Users by service position
        users_by_service_position = {}
        for position in ServicePosition:
            count = db.query(ServiceAssignment).filter(
                ServiceAssignment.position == position,
                ServiceAssignment.is_active == True
            ).count()
            users_by_service_position[position.value] = count
        
        # Recent logins (last 24 hours)
        day_ago = datetime.utcnow() - timedelta(hours=24)
        recent_logins = db.query(LoginSession).filter(
            LoginSession.created_at >= day_ago
        ).count()
        
        return UserStatsResponse(
            total_users=total_users,
            active_users=active_users,
            new_users_this_month=new_users_this_month,
            users_by_role=users_by_role,
            users_by_service_position=users_by_service_position,
            recent_logins=recent_logins
        )
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None)
):
    """Get audit logs (admin only)."""
    try:
        query = db.query(UserAuditLog)
        
        if action:
            query = query.filter(UserAuditLog.action == action)
        
        if user_id:
            query = query.filter(UserAuditLog.user_id == user_id)
        
        logs = query.order_by(desc(UserAuditLog.created_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        return logs
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving audit logs"
        )


@router.get("/meeting-attendance")
async def get_meeting_attendance_stats(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get meeting attendance statistics."""
    try:
        days_ago = datetime.utcnow() - timedelta(days=days)
        
        # Total attendance
        total_attendance = db.query(MeetingAttendance).filter(
            MeetingAttendance.joined_at >= days_ago
        ).count()
        
        # Unique attendees
        unique_attendees = db.query(MeetingAttendance.user_id).filter(
            MeetingAttendance.joined_at >= days_ago,
            MeetingAttendance.user_id.isnot(None)
        ).distinct().count()
        
        # Anonymous attendees
        anonymous_attendees = db.query(MeetingAttendance).filter(
            MeetingAttendance.joined_at >= days_ago,
            MeetingAttendance.user_id.is_(None)
        ).count()
        
        # Average attendance per meeting
        avg_attendance = db.query(
            func.avg(func.count(MeetingAttendance.id))
        ).filter(
            MeetingAttendance.joined_at >= days_ago
        ).group_by(MeetingAttendance.meeting_id).scalar() or 0
        
        return {
            "period_days": days,
            "total_attendance": total_attendance,
            "unique_attendees": unique_attendees,
            "anonymous_attendees": anonymous_attendees,
            "average_attendance_per_meeting": round(avg_attendance, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting meeting attendance stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving attendance statistics"
        )


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Deactivate user account (admin only)."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        # Log deactivation
        audit_log = UserAuditLog(
            user_id=user_id,
            action="account_deactivated",
            resource_type="user",
            resource_id=user_id,
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        logger.info(f"Admin {current_user.id} deactivated user {user_id}")
        return {"message": "User account deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deactivating user account"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    permanent: bool = Query(False, description="Permanent deletion (anonymizes all data)"),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete user account with privacy controls (admin only)."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        admin_service = AdminService(db)
        await admin_service.delete_user(
            user_id=user_id,
            deleted_by=current_user.id,
            permanent=permanent
        )
        
        action = "permanently deleted" if permanent else "deactivated"
        logger.info(f"Admin {current_user.id} {action} user {user_id}")
        
        return {
            "message": f"User account {action} successfully",
            "permanent": permanent
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user account"
        )
