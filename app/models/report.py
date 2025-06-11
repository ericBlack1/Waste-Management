from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base

class WasteTypeEnum(str, Enum):
    PLASTIC = "PLASTIC"
    ORGANIC = "ORGANIC"
    ELECTRONIC = "ELECTRONIC"

class SeverityLevelEnum(str, Enum):
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    RISKING = "RISKING"
    DANGEROUS = "DANGEROUS"

class ReportStatusEnum(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class IllegalDumpReport(Base):
    __tablename__ = "illegal_dump_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    image_url = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(String, nullable=True)
    waste_type = Column(SQLEnum(WasteTypeEnum), nullable=False)
    severity = Column(SQLEnum(SeverityLevelEnum), nullable=False)
    status = Column(SQLEnum(ReportStatusEnum), default=ReportStatusEnum.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)