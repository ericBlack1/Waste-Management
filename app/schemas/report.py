from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

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

class ReportBase(BaseModel):
    location: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    waste_type: WasteTypeEnum
    severity: SeverityLevelEnum

class ReportCreate(ReportBase):
    pass

class ReportOut(ReportBase):
    id: int
    user_id: int
    image_url: str
    status: ReportStatusEnum
    created_at: datetime

    class Config:
        orm_mode = True

class ReportList(BaseModel):
    reports: list[ReportOut]
    count: int

class ReportStatusUpdate(BaseModel):
    status: ReportStatusEnum