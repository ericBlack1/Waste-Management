from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, add_pagination, paginate
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.schemas.collector import (
    CollectorProfileResponse,
    CollectorSummary,
    WasteTypeEnum,
    CollectorSearchParams
)
from app.crud.collector import get_collectors, get_collector_by_id

router = APIRouter(prefix="/collectors", tags=["collectors"])

@router.get("/", response_model=List[CollectorSummary])
async def search_collectors(
    name: Optional[str] = Query(None, min_length=2),
    location: Optional[str] = Query(None, min_length=2),
    waste_type: Optional[WasteTypeEnum] = None,
    min_price: Optional[int] = Query(None, ge=0),
    max_price: Optional[int] = Query(None, ge=0),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    search_params = CollectorSearchParams(
        name=name,
        location=location,
        waste_type=waste_type,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset
    )
    
    collectors = await get_collectors(db, search_params)
    
    return [
        CollectorSummary(
            id=collector.id,
            user_id=collector.user_id,
            name=collector.user.name,
            average_rating=collector.average_rating,
            price_min=collector.price_min,
            price_max=collector.price_max,
            working_days=collector.working_days,
            waste_types=collector.waste_types,
            location=collector.location
        )
        for collector in collectors
    ]

@router.get("/{collector_id}", response_model=CollectorProfileResponse)
async def get_collector_profile(
    collector_id: UUID,
    db: AsyncSession = Depends(get_async_db)
):
    collector = await get_collector_by_id(db, collector_id)
    if not collector:
        raise HTTPException(status_code=404, detail="Collector not found")
    
    return CollectorProfileResponse(
        id=collector.id,
        user_id=collector.user_id,
        user_name=collector.user.name,
        location=collector.location,
        price_min=collector.price_min,
        price_max=collector.price_max,
        working_days=collector.working_days,
        waste_types=collector.waste_types,
        quantity_accepted=collector.quantity_accepted,
        whatsapp_number=collector.whatsapp_number,
        average_rating=collector.average_rating
    )

add_pagination(router)