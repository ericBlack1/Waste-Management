from enum import Enum
from uuid import UUID
from sqlalchemy import Column, String, Integer, Float, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import ENUM, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base

class WasteTypeEnum(str, Enum):
    PLASTIC = "PLASTIC"
    ORGANIC = "ORGANIC"
    ELECTRONIC = "ELECTRONIC"
    HAZARDOUS = "HAZARDOUS"
    GENERAL = "GENERAL"

class QuantityEnum(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
 
class CollectorStatusEnum(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"

class CollectorProfile(Base):
    __tablename__ = "collector_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    location = Column(String, nullable=False, index=True)
    price_min = Column(Integer, nullable=False)
    price_max = Column(Integer, nullable=False)
    working_days = Column(ARRAY(String), nullable=False)
    waste_types = Column(ARRAY(ENUM(WasteTypeEnum)), nullable=False, index=True)
    quantity_accepted = Column(ARRAY(ENUM(QuantityEnum)), nullable=False)
    whatsapp_number = Column(String, nullable=True)
    average_rating = Column(Float, default=0.0)
    status = Column(ENUM(CollectorStatusEnum), nullable=False, default=CollectorStatusEnum.OFFLINE, index=True)
    
    user = relationship("User", back_populates="collector_profile")