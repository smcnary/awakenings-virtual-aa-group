from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.group import TrustedServant
from app.schemas.group import TrustedServant as TrustedServantSchema, TrustedServantCreate, TrustedServantUpdate

router = APIRouter()

@router.get("/", response_model=List[TrustedServantSchema])
async def get_trusted_servants(db: Session = Depends(get_db)):
    """Get all trusted servants"""
    return db.query(TrustedServant).filter(TrustedServant.is_active == True).all()

@router.post("/", response_model=TrustedServantSchema)
async def create_trusted_servant(servant: TrustedServantCreate, db: Session = Depends(get_db)):
    """Create a new trusted servant"""
    db_servant = TrustedServant(**servant.dict())
    db.add(db_servant)
    db.commit()
    db.refresh(db_servant)
    return db_servant

@router.put("/{servant_id}", response_model=TrustedServantSchema)
async def update_trusted_servant(
    servant_id: int, 
    servant: TrustedServantUpdate, 
    db: Session = Depends(get_db)
):
    """Update a trusted servant"""
    db_servant = db.query(TrustedServant).filter(TrustedServant.id == servant_id).first()
    if not db_servant:
        raise HTTPException(status_code=404, detail="Trusted servant not found")
    
    update_data = servant.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_servant, field, value)
    
    db.commit()
    db.refresh(db_servant)
    return db_servant

@router.delete("/{servant_id}")
async def delete_trusted_servant(servant_id: int, db: Session = Depends(get_db)):
    """Delete a trusted servant"""
    db_servant = db.query(TrustedServant).filter(TrustedServant.id == servant_id).first()
    if not db_servant:
        raise HTTPException(status_code=404, detail="Trusted servant not found")
    
    db.delete(db_servant)
    db.commit()
    return {"message": "Trusted servant deleted successfully"}
