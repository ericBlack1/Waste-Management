from datetime import timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password
from app.crud.user import get_user_by_email
from app.schemas.auth import TokenData
from app.core.database import get_db
from app.models.user import User  # Add this import
from app.schemas.user import UserWithProfile

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserWithProfile:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_email(db, email=token_data.email)  # Add await here
    if user is None:
        raise credentials_exception
        
    return UserWithProfile.from_orm(user)

async def get_current_resident(
    current_user: UserWithProfile = Depends(get_current_user)
) -> UserWithProfile:
    if current_user.role != "RESIDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only residents can perform this action."
        )
    return current_user

async def get_current_collector(
    current_user: UserWithProfile = Depends(get_current_user)
) -> UserWithProfile:
    if current_user.role != "COLLECTOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only collectors can perform this action."
        )
    return current_user