from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.group import TrustedServant
from app.models.user import User, UserRole, ServiceAssignment, ServicePosition
from app.schemas.group import TrustedServant as TrustedServantSchema, TrustedServantCreate, TrustedServantUpdate
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.admin_service import AdminService
from app.services.privacy_service import PrivacyService
from app.api.endpoints.auth import get_current_active_user, require_role
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[TrustedServantSchema])
async def get_trusted_servants(db: Session = Depends(get_db)):
    """Get all trusted servants - public endpoint"""
    return db.query(TrustedServant).filter(TrustedServant.is_active == True).all()

@router.get("/positions", response_model=List[dict])
async def get_service_positions():
    """Get available service positions"""
    positions = [
        {"value": pos.value, "label": pos.value.replace("_", " ").title(), "description": _get_position_description(pos)}
        for pos in ServicePosition
    ]
    return positions

def _get_position_description(position: ServicePosition) -> str:
    """Get description for service position"""
    descriptions = {
        ServicePosition.CHAIRPERSON: "Leads group business meetings and represents the group",
        ServicePosition.SECRETARY: "Maintains group records and handles communications",
        ServicePosition.TREASURER: "Manages group finances and 7th Tradition contributions",
        ServicePosition.CHAIR: "Facilitates daily meetings and ensures smooth operation",
        ServicePosition.CO_CHAIR: "Assists the chair and provides backup leadership",
        ServicePosition.HOST: "Manages meeting logistics and welcomes newcomers",
        ServicePosition.CO_HOST: "Assists the host and provides backup support",
        ServicePosition.TECH_HOST: "Manages online meeting platform and technical support",
        ServicePosition.LITERATURE: "Manages literature inventory and distribution",
        ServicePosition.OUTREACH: "Coordinates outreach activities and newcomer support",
        ServicePosition.TWELFTH_STEP: "Coordinates 12th step work and sponsorship"
    }
    return descriptions.get(position, "Service position in the group")

@router.post("/", response_model=TrustedServantSchema)
async def create_trusted_servant(
    servant: TrustedServantCreate, 
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Create a new trusted servant - requires admin or secretary role"""
    # Check if position already has an active servant
    existing = db.query(TrustedServant).filter(
        TrustedServant.position == servant.position,
        TrustedServant.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Position '{servant.position}' already has an active trusted servant"
        )
    
    db_servant = TrustedServant(**servant.dict())
    db.add(db_servant)
    db.commit()
    db.refresh(db_servant)
    return db_servant

@router.put("/{servant_id}", response_model=TrustedServantSchema)
async def update_trusted_servant(
    servant_id: int, 
    servant: TrustedServantUpdate, 
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Update a trusted servant - requires admin or secretary role"""
    db_servant = db.query(TrustedServant).filter(TrustedServant.id == servant_id).first()
    if not db_servant:
        raise HTTPException(status_code=404, detail="Trusted servant not found")
    
    # If changing position, check for conflicts
    if servant.position and servant.position != db_servant.position:
        existing = db.query(TrustedServant).filter(
            TrustedServant.position == servant.position,
            TrustedServant.is_active == True,
            TrustedServant.id != servant_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Position '{servant.position}' already has an active trusted servant"
            )
    
    update_data = servant.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_servant, field, value)
    
    db_servant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_servant)
    return db_servant

@router.delete("/{servant_id}")
async def delete_trusted_servant(
    servant_id: int, 
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Delete a trusted servant - requires admin or secretary role"""
    db_servant = db.query(TrustedServant).filter(TrustedServant.id == servant_id).first()
    if not db_servant:
        raise HTTPException(status_code=404, detail="Trusted servant not found")
    
    # Soft delete by setting is_active to False
    db_servant.is_active = False
    db_servant.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Trusted servant removed successfully"}

@router.post("/apply")
async def apply_for_service_position(
    position: ServicePosition,
    anonymous_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Apply for a service position - maintains anonymity"""
    # Check if position already has an active servant
    existing = db.query(TrustedServant).filter(
        TrustedServant.position == position.value,
        TrustedServant.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Position '{position.value}' is already filled"
        )
    
    # Create service assignment request
    assignment = ServiceAssignment(
        user_id=current_user.id,
        position=position,
        start_date=datetime.utcnow(),
        notes=f"Application submitted by {anonymous_name or 'anonymous member'}",
        created_by=current_user.id
    )
    
    db.add(assignment)
    db.commit()
    
    return {
        "message": "Service position application submitted successfully",
        "position": position.value,
        "anonymous_name": anonymous_name or "Anonymous"
    }

@router.get("/my-applications", response_model=List[dict])
async def get_my_service_applications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's service applications"""
    applications = db.query(ServiceAssignment).filter(
        ServiceAssignment.user_id == current_user.id,
        ServiceAssignment.is_active == True
    ).all()
    
    return [
        {
            "id": str(app.id),
            "position": app.position.value,
            "start_date": app.start_date,
            "end_date": app.end_date,
            "is_active": app.is_active,
            "notes": app.notes,
            "created_at": app.created_at
        }
        for app in applications
    ]


# User Management Endpoints for Trusted Servants

@router.post("/users", response_model=UserResponse)
async def create_user_for_service(
    user_create: UserCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Create a new user for service position (admin/secretary only)."""
    try:
        admin_service = AdminService(db)
        
        # Determine role based on current user permissions and intended service
        role = UserRole.MEMBER  # Default for trusted servant-created users
        
        new_user = await admin_service.create_user(
            user_create=user_create,
            created_by=current_user.id,
            role=role
        )
        
        # Log the creation for service purposes
        from app.models.user import UserAuditLog
        audit_log = UserAuditLog(
            user_id=new_user.id,
            action="user_created_for_service",
            resource_type="user",
            resource_id=str(new_user.id),
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        return UserResponse.from_orm(new_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user for service"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_for_service(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Update user profile for service purposes (admin/secretary only)."""
    try:
        admin_service = AdminService(db)
        
        updated_user = await admin_service.update_user(
            user_id=user_id,
            user_update=user_update,
            updated_by=current_user.id
        )
        
        # Log the update for service purposes
        from app.models.user import UserAuditLog
        audit_log = UserAuditLog(
            user_id=user_id,
            action="user_updated_for_service",
            resource_type="user",
            resource_id=user_id,
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        return UserResponse.from_orm(updated_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )


@router.delete("/users/{user_id}")
async def delete_user_for_service(
    user_id: str,
    permanent: bool = False,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete user account for service purposes (admin only, with privacy controls)."""
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
        
        # Log the deletion for service purposes
        from app.models.user import UserAuditLog
        audit_log = UserAuditLog(
            user_id=user_id,
            action="user_deleted_for_service",
            resource_type="user",
            resource_id=user_id,
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        action = "permanently deleted" if permanent else "deactivated"
        return {
            "message": f"User account {action} successfully for service purposes",
            "permanent": permanent,
            "privacy_compliant": True
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )


@router.get("/users", response_model=List[UserResponse])
async def get_service_users(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db),
    include_inactive: bool = False
):
    """Get users for service management (admin/secretary only, privacy-compliant)."""
    try:
        query = db.query(User)
        
        if not include_inactive:
            query = query.filter(User.is_active == True)
        
        # Only show users who have opted into directory or are service-related
        users = query.filter(
            User.show_in_directory == True
        ).order_by(User.created_at.desc()).all()
        
        # Apply privacy filters
        service_users = []
        for user in users:
            user_response = UserResponse.from_orm(user)
            # Remove sensitive data based on privacy settings
            if not user.show_sobriety_date:
                user_response.sobriety_date = None
            service_users.append(user_response)
        
        return service_users
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving service users"
        )


# Privacy and Anonymity Endpoints

@router.post("/anonymous-user")
async def create_anonymous_service_user(
    service_position: Optional[str] = None,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Create anonymous user for service position (maximum privacy)."""
    try:
        privacy_service = PrivacyService(db)
        
        anonymous_user = await privacy_service.create_anonymous_user_profile(
            service_position=service_position
        )
        
        # Log the creation
        from app.models.user import UserAuditLog
        audit_log = UserAuditLog(
            user_id=anonymous_user.id,
            action="anonymous_service_user_created",
            resource_type="user",
            resource_id=str(anonymous_user.id),
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "message": "Anonymous service user created successfully",
            "user_id": str(anonymous_user.id),
            "anonymous_name": anonymous_user.preferred_name,
            "service_position": service_position,
            "privacy_level": "Maximum",
            "data_retention": "Minimal"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating anonymous service user"
        )


@router.post("/users/{user_id}/anonymize")
async def anonymize_user_data(
    user_id: str,
    preserve_audit: bool = True,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    """Anonymize user data while preserving system integrity (admin only)."""
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
                detail="Cannot anonymize your own account"
            )
        
        privacy_service = PrivacyService(db)
        success = await privacy_service.anonymize_user_data(
            user_id=user_id,
            preserve_audit=preserve_audit
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to anonymize user data"
            )
        
        # Log the anonymization
        from app.models.user import UserAuditLog
        audit_log = UserAuditLog(
            user_id=user_id,
            action="user_data_anonymized",
            resource_type="user",
            resource_id=user_id,
            success=True
        )
        db.add(audit_log)
        db.commit()
        
        return {
            "message": "User data anonymized successfully",
            "user_id": user_id,
            "preserve_audit": preserve_audit,
            "privacy_compliant": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error anonymizing user data"
        )


@router.get("/users/{user_id}/privacy-audit")
async def get_user_privacy_audit(
    user_id: str,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db)
):
    """Get privacy compliance audit for user (admin/secretary only)."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        privacy_service = PrivacyService(db)
        audit_result = await privacy_service.audit_privacy_compliance(user_id)
        
        if "error" in audit_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=audit_result["error"]
            )
        
        return audit_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting privacy audit"
        )


@router.get("/privacy-compliant-users")
async def get_privacy_compliant_users(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    db: Session = Depends(get_db),
    include_inactive: bool = False,
    role_filter: Optional[str] = None
):
    """Get users with privacy controls applied (admin/secretary only)."""
    try:
        privacy_service = PrivacyService(db)
        
        users = await privacy_service.get_privacy_compliant_user_list(
            current_user=current_user,
            include_inactive=include_inactive,
            role_filter=role_filter
        )
        
        return {
            "users": users,
            "total_count": len(users),
            "privacy_compliant": True,
            "data_minimization": "Applied"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving privacy compliant users"
        )
