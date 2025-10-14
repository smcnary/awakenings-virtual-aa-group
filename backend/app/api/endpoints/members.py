"""
Member management API endpoints for AA Virtual platform.
Handles member profiles, service assignments, and directory access.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging

from app.db.database import get_db
from app.models.user import User, ServiceAssignment, ServicePosition, UserRole
from app.schemas.user import (
    UserResponse, UserUpdate, UserProfileResponse, UserListResponse,
    ServiceAssignmentCreate, ServiceAssignmentUpdate, ServiceAssignmentResponse,
    MeetingAttendanceCreate, MeetingAttendanceResponse
)
from app.api.endpoints.auth import get_current_active_user, require_role
from app.services.member_service import MemberService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/profile", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's detailed profile."""
    return UserProfileResponse.from_orm(current_user)


@router.put("/profile", response_model=UserProfileResponse)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    try:
        member_service = MemberService(db)
        updated_user = await member_service.update_user_profile(
            user_id=current_user.id,
            user_update=user_update
        )
        
        logger.info(f"User {current_user.id} updated profile")
        return UserProfileResponse.from_orm(updated_user)
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile"
        )


@router.get("/service-assignments", response_model=List[ServiceAssignmentResponse])
async def get_my_service_assignments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's service assignments."""
    assignments = db.query(ServiceAssignment).filter(
        ServiceAssignment.user_id == current_user.id,
        ServiceAssignment.is_active == True
    ).all()
    
    return assignments


@router.post("/service-assignments", response_model=ServiceAssignmentResponse)
async def request_service_assignment(
    assignment_data: ServiceAssignmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Request a service assignment."""
    try:
        # Check if user already has this position
        existing = db.query(ServiceAssignment).filter(
            ServiceAssignment.user_id == current_user.id,
            ServiceAssignment.position == assignment_data.position,
            ServiceAssignment.is_active == True
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have this service position"
            )
        
        # Create service assignment request
        assignment = ServiceAssignment(
            user_id=current_user.id,
            position=assignment_data.position,
            group_id=assignment_data.group_id,
            meeting_id=assignment_data.meeting_id,
            start_date=assignment_data.start_date,
            end_date=assignment_data.end_date,
            notes=assignment_data.notes,
            is_active=False  # Requires approval
        )
        
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        
        logger.info(f"User {current_user.id} requested service assignment: {assignment_data.position}")
        return assignment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting service assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error requesting service assignment"
        )


@router.get("/directory", response_model=List[UserResponse])
async def get_member_directory(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    show_sobriety: Optional[bool] = Query(None, description="Filter by sobriety date visibility"),
    service_position: Optional[ServicePosition] = Query(None, description="Filter by service position"),
    limit: int = Query(50, ge=1, le=100)
):
    """Get member directory (only users who opted in)."""
    query = db.query(User).filter(
        User.is_active == True,
        User.show_in_directory == True
    )
    
    # Apply filters
    if show_sobriety is not None:
        query = query.filter(User.show_sobriety_date == show_sobriety)
    
    if service_position:
        query = query.join(ServiceAssignment).filter(
            ServiceAssignment.position == service_position,
            ServiceAssignment.is_active == True
        )
    
    users = query.limit(limit).all()
    
    # Filter out sensitive information
    public_users = []
    for user in users:
        user_data = UserResponse.from_orm(user)
        if not user.show_sobriety_date:
            user_data.sobriety_date = None
        public_users.append(user_data)
    
    return public_users


@router.get("/meeting-history", response_model=List[MeetingAttendanceResponse])
async def get_my_meeting_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """Get current user's meeting attendance history."""
    from app.models.user import MeetingAttendance
    
    attendance = db.query(MeetingAttendance).filter(
        MeetingAttendance.user_id == current_user.id
    ).order_by(MeetingAttendance.joined_at.desc()).limit(limit).all()
    
    return attendance


@router.post("/meeting-attendance", response_model=MeetingAttendanceResponse)
async def record_meeting_attendance(
    attendance_data: MeetingAttendanceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record meeting attendance."""
    try:
        from app.models.user import MeetingAttendance
        
        # Check if already attended this occurrence
        if attendance_data.occurrence_id:
            existing = db.query(MeetingAttendance).filter(
                MeetingAttendance.user_id == current_user.id,
                MeetingAttendance.occurrence_id == attendance_data.occurrence_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Already recorded attendance for this meeting"
                )
        
        # Create attendance record
        attendance = MeetingAttendance(
            user_id=current_user.id,
            meeting_id=attendance_data.meeting_id,
            occurrence_id=attendance_data.occurrence_id,
            joined_at=datetime.utcnow(),
            share_attendance=attendance_data.share_attendance,
            anonymous_id=attendance_data.anonymous_id
        )
        
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        
        logger.info(f"User {current_user.id} recorded meeting attendance")
        return attendance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording attendance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error recording attendance"
        )


@router.get("/stats")
async def get_my_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's statistics."""
    try:
        from app.models.user import MeetingAttendance
        
        # Calculate stats
        total_meetings = db.query(MeetingAttendance).filter(
            MeetingAttendance.user_id == current_user.id
        ).count()
        
        active_service_positions = db.query(ServiceAssignment).filter(
            ServiceAssignment.user_id == current_user.id,
            ServiceAssignment.is_active == True
        ).count()
        
        # Calculate sobriety days
        sobriety_days = None
        if current_user.sobriety_date:
            sobriety_days = (datetime.utcnow().date() - current_user.sobriety_date).days
        
        return {
            "total_meetings_attended": total_meetings,
            "active_service_positions": active_service_positions,
            "sobriety_days": sobriety_days,
            "member_since_days": (datetime.utcnow() - current_user.created_at).days,
            "profile_completion_percentage": _calculate_profile_completion(current_user)
        }
        
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting user statistics"
        )


def _calculate_profile_completion(user: User) -> int:
    """Calculate profile completion percentage."""
    fields = [
        user.preferred_name,
        user.sobriety_date,
        user.timezone,
        user.language
    ]
    
    completed_fields = sum(1 for field in fields if field is not None)
    return int((completed_fields / len(fields)) * 100)
