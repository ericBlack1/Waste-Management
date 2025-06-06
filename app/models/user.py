from enum import Enum
from sqlalchemy import ARRAY, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class RoleEnum(str, Enum):
    RESIDENT = "RESIDENT"
    COLLECTOR = "COLLECTOR"

class WasteTypeEnum(str, Enum):
    PLASTIC = "PLASTIC"
    ELECTRONIC = "ELECTRONIC"
    ORGANIC = "ORGANIC"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(ENUM(RoleEnum), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Add relationship to collector profile
    collector_profile = relationship("CollectorProfile", backref="user", uselist=False)

class CollectorProfileLegacy(Base):
    __tablename__ = "collector_profiles_legacy"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    location = Column(String, nullable=False)
    pickup_radius_km = Column(Float, nullable=False)
    working_hours = Column(String, nullable=False)
    accepted_waste_types = Column(ARRAY(ENUM(WasteTypeEnum)), nullable=False)


__all__ = ["User", "CollectorProfile", "RoleEnum", "WasteTypeEnum"]