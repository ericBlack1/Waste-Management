from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

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

class CollectorProfileBase(BaseModel):
    location: str
    price_min: int
    price_max: int
    working_days: List[str]
    waste_types: List[WasteTypeEnum]
    quantity_accepted: List[QuantityEnum]
    whatsapp_number: Optional[str] = None

class CollectorProfileResponse(CollectorProfileBase):
    id: UUID
    user_id: UUID
    average_rating: float
    user_name: str

class CollectorSummary(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    average_rating: float
    price_min: int
    price_max: int
    working_days: List[str]
    waste_types: List[WasteTypeEnum]
    location: str

class CollectorSearchParams(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    waste_type: Optional[WasteTypeEnum] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    limit: int = 10
    offset: int = 0