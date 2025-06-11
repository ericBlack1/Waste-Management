from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash
from app.models.user import User
from app.models.collector import CollectorProfile
from app.schemas.auth import UserCreate, CollectorProfileCreate

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = (
        select(User)
        .options(selectinload(User.collector_profile))
        .where(User.email == email)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_collector_profile(db: AsyncSession, profile: CollectorProfileCreate, user_id: int):
    db_profile = CollectorProfile(
        user_id=user_id,
        location=profile.location,
        pickup_radius_km=profile.pickup_radius_km,
        working_hours=profile.working_hours,
        waste_types=profile.accepted_waste_types
    )
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)
    return db_profile