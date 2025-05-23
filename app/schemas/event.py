from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.permission import Role

class EventBase(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[Dict[str, Any]] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None

class EventInDB(EventBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Event(EventInDB):
    pass

class EventPermissionCreate(BaseModel):
    user_id: int
    role: Role

class EventPermission(EventPermissionCreate):
    id: int
    event_id: int

    class Config:
        from_attributes = True

class EventVersion(BaseModel):
    id: int
    event_id: int
    version_number: int
    data: Dict[str, Any]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class EventDiff(BaseModel):
    field: str
    old_value: Any
    new_value: Any 