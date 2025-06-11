from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.collector import WasteTypeEnum, QuantityEnum
from .auth import RoleEnum

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    full_name: str
    email: str
    role: RoleEnum
    created_at: datetime

class CollectorProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    location: str
    price_min: int
    price_max: int
    working_days: List[str]
    waste_types: List[WasteTypeEnum]
    quantity_accepted: List[QuantityEnum]
    whatsapp_number: Optional[str]
    average_rating: float

class UserWithProfile(UserOut):
    model_config = ConfigDict(from_attributes=True)
    
    collector_profile: Optional[CollectorProfileOut] = None