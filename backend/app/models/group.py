from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class GroupInfo(Base):
    __tablename__ = "group_info"
    
    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(255), nullable=False)
    description = Column(Text)
    meeting_time = Column(String(100))
    meeting_link = Column(String(500))
    phone_number = Column(String(20))
    meeting_id = Column(String(100))
    contact_email = Column(String(255))
    facebook_group = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TrustedServant(Base):
    __tablename__ = "trusted_servants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text)
    meeting_link = Column(String(500))
    phone_number = Column(String(20))
    is_recurring = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(500))
    download_url = Column(String(500))
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
