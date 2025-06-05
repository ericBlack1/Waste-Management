from enum import Enum
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Float, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ENUM, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base

class WasteTypeEnum(str, Enum):
    ORGANIC = "organic"
    RECYCLABLE = "recyclable"
    ELECTRONIC = "electronic"
    HAZARDOUS = "hazardous"
    GENERAL = "general"

class QuantityEnum(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class CollectorProfile(Base):
    __tablename__ = "collector_profiles"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    location = Column(String, nullable=False, index=True)
    price_min = Column(Integer, nullable=False)
    price_max = Column(Integer, nullable=False)
    working_days = Column(ARRAY(String), nullable=False)
    waste_types = Column(ARRAY(ENUM(WasteTypeEnum)), nullable=False, index=True)
    quantity_accepted = Column(ARRAY(ENUM(QuantityEnum)), nullable=False)
    whatsapp_number = Column(String, nullable=True)
    average_rating = Column(Float, default=0.0)
    
    user = relationship("User", back_populates="collector_profile")