from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.marketplace import ListingStatusEnum
from app.models.collector import WasteTypeEnum, QuantityEnum

class ListingBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    waste_type: WasteTypeEnum
    price: float = Field(..., gt=0)
    quantity: QuantityEnum
    location: str = Field(..., min_length=2, max_length=100)

class ListingCreate(ListingBase):
    image_url: str = Field(..., min_length=1)

class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[ListingStatusEnum] = None

class ListingResponse(ListingBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    resident_id: int
    collector_id: Optional[int] = None
    image_url: str
    status: ListingStatusEnum
    created_at: datetime
    updated_at: datetime
    reserved_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None
    resident_name: str
    collector_name: Optional[str] = None

class ListingSearchParams(BaseModel):
    waste_type: Optional[WasteTypeEnum] = None
    location: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    status: Optional[ListingStatusEnum] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class ListingSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    waste_type: WasteTypeEnum
    price: float
    quantity: QuantityEnum
    location: str
    image_url: str
    status: ListingStatusEnum
    created_at: datetime
    resident_name: str 