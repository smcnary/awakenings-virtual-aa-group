from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.group import Resource
from app.schemas.group import Resource as ResourceSchema, ResourceCreate, ResourceUpdate

router = APIRouter()

@router.get("/", response_model=List[ResourceSchema])
async def get_resources(
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get resources, optionally filtered by category"""
    query = db.query(Resource).filter(Resource.is_active == True)
    
    if category:
        query = query.filter(Resource.category == category)
    
    return query.order_by(Resource.title).all()

@router.post("/", response_model=ResourceSchema)
async def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    """Create a new resource"""
    db_resource = Resource(**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@router.put("/{resource_id}", response_model=ResourceSchema)
async def update_resource(
    resource_id: int, 
    resource: ResourceUpdate, 
    db: Session = Depends(get_db)
):
    """Update a resource"""
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    update_data = resource.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_resource, field, value)
    
    db.commit()
    db.refresh(db_resource)
    return db_resource

@router.delete("/{resource_id}")
async def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    """Delete a resource"""
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    db.delete(db_resource)
    db.commit()
    return {"message": "Resource deleted successfully"}
