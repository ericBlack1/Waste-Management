from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator

class RoleEnum(str, Enum):
    RESIDENT = "RESIDENT"
    COLLECTOR = "COLLECTOR"

class WasteTypeEnum(str, Enum):
    PLASTIC = "PLASTIC"
    ELECTRONIC = "ELECTRONIC"
    ORGANIC = "ORGANIC"

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
    pickup_radius_km: float = Field(..., gt=0)
    working_hours: str = Field(..., min_length=5, max_length=100)
    accepted_waste_types: List[WasteTypeEnum]