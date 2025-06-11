from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from app.models.collector import WasteTypeEnum, QuantityEnum, CollectorStatusEnum

class RoleEnum(str, Enum):
    RESIDENT = "RESIDENT"
    COLLECTOR = "COLLECTOR"

class WasteTypeEnum(str, Enum):
    PLASTIC = "PLASTIC"
    ORGANIC = "ORGANIC"
    ELECTRONIC = "ELECTRONIC"
    HAZARDOUS = "HAZARDOUS"
    GENERAL = "GENERAL"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(...)
    role: RoleEnum

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

class CollectorProfileCreate(BaseModel):
    location: str = Field(..., min_length=2, max_length=100)
    price_min: int = Field(..., gt=0)
    price_max: int = Field(..., gt=0)
    working_days: List[str] = Field(..., min_items=1)
    waste_types: List[WasteTypeEnum] = Field(..., min_items=1)
    quantity_accepted: List[QuantityEnum] = Field(..., min_items=1)
    whatsapp_number: Optional[str] = Field(None, min_length=10, max_length=15)
    status: CollectorStatusEnum = Field(default=CollectorStatusEnum.OFFLINE)

    @validator('price_max')
    def price_max_greater_than_min(cls, v, values, **kwargs):
        if 'price_min' in values and v <= values['price_min']:
            raise ValueError('price_max must be greater than price_min')
        return v