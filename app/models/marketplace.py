from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class ListingStatusEnum(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    CANCELLED = "CANCELLED"

class Listing(Base):
    __tablename__ = "marketplace_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    collector_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Set when a collector reserves/buys
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    waste_type = Column(SQLEnum("PLASTIC", "ORGANIC", "ELECTRONIC", "HAZARDOUS", "GENERAL", name="wastetypeenum"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(SQLEnum("SMALL", "MEDIUM", "LARGE", name="quantityenum"), nullable=False)
    location = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=False)
    status = Column(SQLEnum(ListingStatusEnum), nullable=False, default=ListingStatusEnum.AVAILABLE, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    reserved_at = Column(DateTime(timezone=True), nullable=True)
    sold_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    resident = relationship("User", foreign_keys=[resident_id], backref="listings_as_resident")
    collector = relationship("User", foreign_keys=[collector_id], backref="listings_as_collector") 