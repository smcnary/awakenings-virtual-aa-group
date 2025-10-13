from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class GroupInfoBase(BaseModel):
    group_name: str
    description: Optional[str] = None
    meeting_time: Optional[str] = None
    meeting_link: Optional[str] = None
    phone_number: Optional[str] = None
    meeting_id: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    facebook_group: Optional[str] = None

class GroupInfoCreate(GroupInfoBase):
    pass

class GroupInfoUpdate(BaseModel):
    group_name: Optional[str] = None
    description: Optional[str] = None
    meeting_time: Optional[str] = None
    meeting_link: Optional[str] = None
    phone_number: Optional[str] = None
    meeting_id: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    facebook_group: Optional[str] = None

class GroupInfo(GroupInfoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TrustedServantBase(BaseModel):
    name: str
    position: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True

class TrustedServantCreate(TrustedServantBase):
    pass

class TrustedServantUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class TrustedServant(TrustedServantBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MeetingBase(BaseModel):
    title: str
    date: datetime
    description: Optional[str] = None
    meeting_link: Optional[str] = None
    phone_number: Optional[str] = None
    is_recurring: bool = True

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    meeting_link: Optional[str] = None
    phone_number: Optional[str] = None
    is_recurring: Optional[bool] = None

class Meeting(MeetingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class Resource(ResourceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
