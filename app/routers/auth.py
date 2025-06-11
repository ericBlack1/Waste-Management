from datetime import timedelta
from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.crud.user import create_collector_profile, create_user, get_user_by_email
from app.dependencies import get_current_user
from app.schemas.auth import Token, UserCreate, CollectorProfileCreate, UserLogin
from app.schemas.user import UserOut, UserWithProfile
from app.models.user import User
from app.models.collector import CollectorProfile, WasteTypeEnum, QuantityEnum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Background task function
async def log_registration_event(email: str):
    """Background task to log registration events"""
    logger.info(f"Background task: User registration logged for {email}")

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Login attempt for email: {form_data.username}")
    
    try:
        # Normalize email for consistency
        email = form_data.username.strip().lower()
        user = await get_user_by_email(db, email)
        logger.info(f"User lookup result: {'Found' if user else 'Not found'}")
        
        if not user:
            logger.warning(f"No user found with email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Log password verification attempt (without exposing the actual password)
        password_valid = verify_password(form_data.password, user.password_hash)
        logger.info(f"Password verification result: {'Valid' if password_valid else 'Invalid'}")
        
        if not password_valid:
            logger.warning(f"Invalid password for user: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        logger.info(f"Successful login for user: {email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again."
        )

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with enhanced validation and error handling.
    """
    try:
        # Normalize email (trim whitespace and convert to lowercase)
        normalized_email = user.email.strip().lower()
        
        # Check if email exists using a direct query for better control
        stmt = select(User).where(User.email.ilike(normalized_email))
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Email already registered",
                    "code": "EMAIL_EXISTS",
                    "email": normalized_email
                }
            )
        
        # Create new user with normalized email
        # Remove password from user_data and use password_hash instead
        user_data = user.dict(exclude={'password', 'confirm_password'})
        user_data["email"] = normalized_email
        user_data["password_hash"] = get_password_hash(user.password)
        
        try:
            new_user = User(**user_data)
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            # Log successful registration
            logger.info(f"Successfully registered new user: {normalized_email}")
            
            # Add background task for any post-registration processing if needed
            background_tasks.add_task(log_registration_event, normalized_email)
            
            # Fix: Use model_validate instead of from_orm for Pydantic v2
            return UserOut.model_validate(new_user)
            
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error during user registration: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during registration. Please try again."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

@router.post("/register/collector", response_model=UserWithProfile, status_code=status.HTTP_201_CREATED)
async def register_collector(
    user: UserCreate,
    profile: CollectorProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new collector with their profile.
    """
    try:
        logger.info(f"Starting collector registration for email: {user.email}")
        
        if user.role != "COLLECTOR":
            logger.warning(f"Invalid role for collector registration: {user.role}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be COLLECTOR for this registration endpoint"
            )
        
        # Normalize email (trim whitespace and convert to lowercase)
        normalized_email = user.email.strip().lower()
        logger.info(f"Normalized email: {normalized_email}")
        
        # Check if email exists using a direct query for better control
        stmt = select(User).where(User.email.ilike(normalized_email))
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            logger.warning(f"Collector registration attempt with existing email: {normalized_email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Email already registered",
                    "code": "EMAIL_EXISTS",
                    "email": normalized_email
                }
            )
        
        # Create new user with normalized email
        user_data = user.dict(exclude={'password', 'confirm_password'})
        user_data["email"] = normalized_email
        user_data["password_hash"] = get_password_hash(user.password)
        
        try:
            logger.info("Creating new user...")
            # Create user
            new_user = User(**user_data)
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            logger.info(f"User created successfully with ID: {new_user.id}")
            
            logger.info("Creating collector profile...")
            # Create collector profile
            db_profile = CollectorProfile(
                user_id=new_user.id,
                location=profile.location,
                price_min=profile.price_min,
                price_max=profile.price_max,
                working_days=profile.working_days,
                waste_types=profile.waste_types,
                quantity_accepted=profile.quantity_accepted,
                whatsapp_number=profile.whatsapp_number
            )
            db.add(db_profile)
            await db.commit()
            await db.refresh(db_profile)
            logger.info(f"Collector profile created successfully for user ID: {new_user.id}")
            
            # FIXED: Explicitly load the user with the collector profile relationship
            # This prevents the greenlet error by eager loading the relationship
            stmt = select(User).options(selectinload(User.collector_profile)).where(User.id == new_user.id)
            result = await db.execute(stmt)
            new_user_with_profile = result.scalar_one()
            logger.info("User loaded with collector profile")
            
            # Convert to response model
            try:
                # Use model_validate for Pydantic v2 compatibility
                response = UserWithProfile.model_validate(new_user_with_profile)
                logger.info("Successfully converted user to response model")
                return response
            except Exception as e:
                logger.error(f"Error converting user to response model: {str(e)}")
                # Fallback to manual construction if model_validate fails
                logger.info("Attempting manual response construction as fallback")
                
                response_data = {
                    "id": new_user.id,
                    "email": new_user.email,
                    "username": new_user.username,
                    "role": new_user.role,
                    "is_active": new_user.is_active,
                    "created_at": new_user.created_at,
                    "updated_at": new_user.updated_at,
                    "collector_profile": {
                        "id": db_profile.id,
                        "location": db_profile.location,
                        "price_min": db_profile.price_min,
                        "price_max": db_profile.price_max,
                        "working_days": db_profile.working_days,
                        "waste_types": db_profile.waste_types,
                        "quantity_accepted": db_profile.quantity_accepted,
                        "whatsapp_number": db_profile.whatsapp_number,
                        "created_at": db_profile.created_at,
                        "updated_at": db_profile.updated_at
                    }
                }
                
                response = UserWithProfile(**response_data)
                logger.info("Successfully created response using manual construction")
                return response
            
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Database error during collector registration: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during collector registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

@router.get("/me", response_model=UserWithProfile)
async def read_users_me(current_user: UserWithProfile = Depends(get_current_user)):
    """
    Get current user information including collector profile if it exists.
    """
    try:
        # The current_user is already loaded with the collector_profile relationship
        # thanks to the selectinload in get_user_by_email
        return current_user
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user profile"
        )