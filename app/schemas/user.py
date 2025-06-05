from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .auth import RoleEnum, WasteTypeEnum

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: RoleEnum
    created_at: datetime

    class Config:
        orm_mode = True

class CollectorProfileOut(BaseModel):
    location: str
    pickup_radius_km: float
    working_hours: str
    accepted_waste_types: List[WasteTypeEnum]

    class Config:
        orm_mode = True

class UserWithProfile(UserOut):
    collector_profile: Optional[CollectorProfileOut] = None

    class Config:
        orm_mode = True