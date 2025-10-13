from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from app.db.database import get_db
from app.models.group import Meeting
from app.schemas.group import Meeting as MeetingSchema, MeetingCreate, MeetingUpdate

router = APIRouter()

@router.get("/", response_model=List[MeetingSchema])
async def get_meetings(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Get meetings, optionally filtered by date range"""
    query = db.query(Meeting)
    
    if start_date:
        query = query.filter(Meeting.date >= start_date)
    if end_date:
        query = query.filter(Meeting.date <= end_date)
    
    return query.order_by(Meeting.date).all()

@router.post("/", response_model=MeetingSchema)
async def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    """Create a new meeting"""
    db_meeting = Meeting(**meeting.dict())
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

@router.put("/{meeting_id}", response_model=MeetingSchema)
async def update_meeting(
    meeting_id: int, 
    meeting: MeetingUpdate, 
    db: Session = Depends(get_db)
):
    """Update a meeting"""
    db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    update_data = meeting.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_meeting, field, value)
    
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Delete a meeting"""
    db_meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    db.delete(db_meeting)
    db.commit()
    return {"message": "Meeting deleted successfully"}
