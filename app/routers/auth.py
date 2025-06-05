from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.crud.user import create_collector_profile, create_user, get_user_by_email
from app.dependencies import get_current_user
from app.schemas.auth import Token, UserCreate, CollectorProfileCreate, UserLogin
from app.schemas.user import UserOut, UserWithProfile

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    created_user = create_user(db, user=user)
    return created_user

@router.post("/register/collector", response_model=UserWithProfile)
def register_collector(
    user: UserCreate,
    profile: CollectorProfileCreate,
    db: Session = Depends(get_db)
):
    if user.role != "COLLECTOR":
        raise HTTPException(
            status_code=400,
            detail="Role must be COLLECTOR for this registration endpoint"
        )
    
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    created_user = create_user(db, user=user)
    
    created_profile = create_collector_profile(db, profile=profile, user_id=created_user.id)
    
    db.refresh(created_user)
    
    return {
        "id": created_user.id,
        "full_name": created_user.full_name,
        "email": created_user.email,
        "role": created_user.role,
        "created_at": created_user.created_at,
        "collector_profile": {
            "location": created_profile.location,
            "pickup_radius_km": created_profile.pickup_radius_km,
            "working_hours": created_profile.working_hours,
            "accepted_waste_types": created_profile.accepted_waste_types
        }
    }

@router.get("/me", response_model=UserWithProfile)
async def read_users_me(current_user: UserWithProfile = Depends(get_current_user)):
    return current_user