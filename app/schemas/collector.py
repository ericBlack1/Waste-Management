from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, field_validator, ConfigDict
from uuid import UUID
import json

class WasteTypeEnum(str, Enum):
    PLASTIC = "PLASTIC"
    ORGANIC = "ORGANIC"
    ELECTRONIC = "ELECTRONIC"
    HAZARDOUS = "HAZARDOUS"
    GENERAL = "GENERAL"

class QuantityEnum(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class CollectorStatusEnum(str, Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"

class CollectorProfileBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    location: str
    price_min: int
    price_max: int
    working_days: List[str]
    waste_types: List[WasteTypeEnum]
    quantity_accepted: List[QuantityEnum]
    whatsapp_number: Optional[str] = None
    status: CollectorStatusEnum = CollectorStatusEnum.OFFLINE
    
    @field_validator('working_days', mode='before')
    @classmethod
    def parse_working_days(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                # Try JSON parsing first
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                # Fallback to comma-separated
                return [day.strip() for day in v.split(',') if day.strip()]
        return []
     
    @field_validator('waste_types', mode='before')
    @classmethod
    def parse_waste_types(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                # Try JSON parsing first
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                # Fallback to comma-separated
                return [wt.strip() for wt in v.split(',') if wt.strip()]
        return []
    
    @field_validator('quantity_accepted', mode='before')
    @classmethod
    def parse_quantity_accepted(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                # Try JSON parsing first
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                # Fallback to comma-separated
                return [q.strip() for q in v.split(',') if q.strip()]
        return []

class CollectorProfileCreate(CollectorProfileBase):
    pass

class CollectorProfileUpdate(CollectorProfileBase):
    location: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    working_days: Optional[List[str]] = None
    waste_types: Optional[List[WasteTypeEnum]] = None
    quantity_accepted: Optional[List[QuantityEnum]] = None
    status: Optional[CollectorStatusEnum] = None

class CollectorProfileResponse(CollectorProfileBase):
    id: UUID  # Keep UUID for collector ID if that's what you're using
    user_id: int  # Changed to int for user ID
    average_rating: float = 0.0
    user_name: str = "Unknown"

class CollectorSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    id: UUID  # Keep UUID for collector ID if that's what you're using
    user_id: int  # Changed to int for user ID
    name: str = "Unknown"
    average_rating: float = 0.0
    price_min: int
    price_max: int
    working_days: List[str]
    waste_types: List[WasteTypeEnum]
    location: str
    status: CollectorStatusEnum
    
    @field_validator('working_days', mode='before')
    @classmethod
    def parse_working_days(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [day.strip() for day in v.split(',') if day.strip()]
        return []
    
    @field_validator('waste_types', mode='before')
    @classmethod
    def parse_waste_types(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [wt.strip() for wt in v.split(',') if wt.strip()]
        return []

class SimpleCollectorResponse(BaseModel):
    """Simplified response model with no relations"""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    id: Union[UUID, int]  # Flexible to handle both UUID and int
    user_id: int  # Assuming user_id is int based on your issue
    location: str
    price_min: int
    price_max: int
    working_days: List[str] = []
    waste_types: List[str] = []  # Simplified to just strings
    quantity_accepted: List[str] = []
    whatsapp_number: Optional[str] = None
    average_rating: float = 0.0
    
    @field_validator('working_days', mode='before')
    @classmethod
    def parse_working_days(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [day.strip() for day in v.split(',') if day.strip()]
        return []
    
    @field_validator('waste_types', mode='before')
    @classmethod
    def parse_waste_types(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [wt.strip() for wt in v.split(',') if wt.strip()]
        return []
    
    @field_validator('quantity_accepted', mode='before')
    @classmethod
    def parse_quantity_accepted(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [q.strip() for q in v.split(',') if q.strip()]
        return []

class CollectorSearchParams(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    waste_type: Optional[WasteTypeEnum] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    status: Optional[CollectorStatusEnum] = None
    limit: int = 10
    offset: int = 0
