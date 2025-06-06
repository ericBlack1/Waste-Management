from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import CollectorProfileLegacy, User
from app.schemas.auth import UserCreate, CollectorProfileCreate

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_collector_profile(db: Session, profile: CollectorProfileCreate, user_id: int):
    db_profile = CollectorProfileLegacy(
        user_id=user_id,
        location=profile.location,
        pickup_radius_km=profile.pickup_radius_km,
        working_hours=profile.working_hours,
        accepted_waste_types=profile.accepted_waste_types
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile