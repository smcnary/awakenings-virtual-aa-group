from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.group import GroupInfo
from app.schemas.group import GroupInfo as GroupInfoSchema, GroupInfoCreate, GroupInfoUpdate

router = APIRouter()

@router.get("/", response_model=GroupInfoSchema)
async def get_group_info(db: Session = Depends(get_db)):
    """Get group information"""
    group_info = db.query(GroupInfo).first()
    if not group_info:
        raise HTTPException(status_code=404, detail="Group information not found")
    return group_info

@router.post("/", response_model=GroupInfoSchema)
async def create_group_info(group_info: GroupInfoCreate, db: Session = Depends(get_db)):
    """Create group information"""
    db_group_info = GroupInfo(**group_info.dict())
    db.add(db_group_info)
    db.commit()
    db.refresh(db_group_info)
    return db_group_info

@router.put("/{group_id}", response_model=GroupInfoSchema)
async def update_group_info(
    group_id: int, 
    group_info: GroupInfoUpdate, 
    db: Session = Depends(get_db)
):
    """Update group information"""
    db_group_info = db.query(GroupInfo).filter(GroupInfo.id == group_id).first()
    if not db_group_info:
        raise HTTPException(status_code=404, detail="Group information not found")
    
    update_data = group_info.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_group_info, field, value)
    
    db.commit()
    db.refresh(db_group_info)
    return db_group_info
