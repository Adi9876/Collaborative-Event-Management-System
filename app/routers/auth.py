from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Any

from app.core.security import create_access_token, verify_password, get_password_hash
from app.schemas.user import UserCreate, User, Token, UserRole
from app.models.user import User as UserModel
from app.database import get_db
from app.config import settings

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=UserRole.VIEWER,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=expires_delta
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": datetime.utcnow() + expires_delta
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Any:
    try:
        # Verify the current token
        token_data = await verify_token(current_token)
        user = db.query(UserModel).filter(UserModel.username == token_data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new token
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=expires_delta
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": datetime.utcnow() + expires_delta
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout(
    current_token: str = Depends(oauth2_scheme)
) -> Any:
    # In a real application, you might want to:
    # 1. Add the token to a blacklist
    # 2. Clear any session data
    # 3. Invalidate refresh tokens
    
    # For now, we'll just return a success message
    # The client should remove the token from their storage
    return {"message": "Successfully logged out"} 