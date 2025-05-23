from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from datetime import datetime

from app.core.security import oauth2_scheme, verify_token
from app.database import get_db
from app.models.user import User
from app.models.event import Event, EventVersion
from app.models.permission import EventPermission, Role
from app.schemas.event import (
    EventCreate, EventUpdate, Event as EventSchema,
    EventPermissionCreate, EventPermission as EventPermissionSchema,
    EventVersion as EventVersionSchema, EventDiff
)

router = APIRouter()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        token_data = await verify_token(token)
        user = db.query(User).filter(User.username == token_data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def check_permission(db: Session, event_id: int, user_id: int, required_role: Role) -> bool:
    permission = db.query(EventPermission).filter(
        EventPermission.event_id == event_id,
        EventPermission.user_id == user_id
    ).first()
    
    if not permission:
        return False
    
    role_hierarchy = {Role.OWNER: 3, Role.EDITOR: 2, Role.VIEWER: 1}
    return role_hierarchy[permission.role] >= role_hierarchy[required_role]

@router.post("/", response_model=EventSchema)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    db_event = Event(**event.dict(), owner_id=current_user.id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Create initial version with serialized datetime objects
    event_data = event.dict()
    event_data['start_time'] = event_data['start_time'].isoformat()
    event_data['end_time'] = event_data['end_time'].isoformat()
    
    version = EventVersion(
        event_id=db_event.id,
        version_number=1,
        data=event_data,
        created_by=current_user.id
    )
    db.add(version)
    db.commit()
    
    return db_event

@router.get("/", response_model=List[EventSchema])
def list_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    events = db.query(Event).filter(
        (Event.owner_id == current_user.id) |  # User is owner
        (Event.id.in_(
            db.query(EventPermission.event_id).filter(
                EventPermission.user_id == current_user.id
            )
        ))  # User has permissions
    ).offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=EventSchema)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if not check_permission(db, event_id, current_user.id, Role.VIEWER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event

@router.put("/{event_id}", response_model=EventSchema)
def update_event(
    event_id: int,
    event_update: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if not check_permission(db, event_id, current_user.id, Role.EDITOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Create new version
    current_version = db.query(EventVersion).filter(
        EventVersion.event_id == event_id
    ).order_by(EventVersion.version_number.desc()).first()
    
    new_version_number = current_version.version_number + 1
    new_data = {**db_event.__dict__, **event_update.dict(exclude_unset=True)}
    new_data.pop('_sa_instance_state', None)
    
    # Serialize datetime objects
    if 'start_time' in new_data and isinstance(new_data['start_time'], datetime):
        new_data['start_time'] = new_data['start_time'].isoformat()
    if 'end_time' in new_data and isinstance(new_data['end_time'], datetime):
        new_data['end_time'] = new_data['end_time'].isoformat()
    if 'created_at' in new_data and isinstance(new_data['created_at'], datetime):
        new_data['created_at'] = new_data['created_at'].isoformat()
    if 'updated_at' in new_data and isinstance(new_data['updated_at'], datetime):
        new_data['updated_at'] = new_data['updated_at'].isoformat()
    
    version = EventVersion(
        event_id=event_id,
        version_number=new_version_number,
        data=new_data,
        created_by=current_user.id
    )
    db.add(version)
    
    # Update event
    for field, value in event_update.dict(exclude_unset=True).items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    if not check_permission(db, event_id, current_user.id, Role.OWNER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(db_event)
    db.commit()

@router.post("/{event_id}/share", response_model=EventPermissionSchema)
def share_event(
    event_id: int,
    permission: EventPermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if not check_permission(db, event_id, current_user.id, Role.OWNER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_permission = EventPermission(
        event_id=event_id,
        user_id=permission.user_id,
        role=permission.role
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

@router.get("/{event_id}/history", response_model=List[EventVersionSchema])
def get_event_history(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if not check_permission(db, event_id, current_user.id, Role.VIEWER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    versions = db.query(EventVersion).filter(
        EventVersion.event_id == event_id
    ).order_by(EventVersion.version_number.desc()).all()
    return versions

@router.get("/{event_id}/diff/{version1}/{version2}", response_model=List[EventDiff])
def get_version_diff(
    event_id: int,
    version1: int,
    version2: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if not check_permission(db, event_id, current_user.id, Role.VIEWER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    v1 = db.query(EventVersion).filter(
        EventVersion.event_id == event_id,
        EventVersion.version_number == version1
    ).first()
    v2 = db.query(EventVersion).filter(
        EventVersion.event_id == event_id,
        EventVersion.version_number == version2
    ).first()
    
    if not v1 or not v2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    diffs = []
    for key in v1.data.keys():
        if v1.data[key] != v2.data[key]:
            diffs.append(EventDiff(
                field=key,
                old_value=v1.data[key],
                new_value=v2.data[key]
            ))
    
    return diffs 