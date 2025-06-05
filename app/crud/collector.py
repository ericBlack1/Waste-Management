from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from uuid import UUID
from app.models.collector import CollectorProfile
from app.schemas.collector import CollectorSearchParams

async def get_collectors(
    db: AsyncSession, 
    search_params: CollectorSearchParams
) -> List[CollectorProfile]:
    query = select(CollectorProfile).join(CollectorProfile.user)
    
    if search_params.name:
        query = query.where(CollectorProfile.user.name.ilike(f"%{search_params.name}%"))
    if search_params.location:
        query = query.where(CollectorProfile.location.ilike(f"%{search_params.location}%"))
    if search_params.waste_type:
        query = query.where(CollectorProfile.waste_types.any(search_params.waste_type))
    if search_params.min_price:
        query = query.where(CollectorProfile.price_max >= search_params.min_price)
    if search_params.max_price:
        query = query.where(CollectorProfile.price_min <= search_params.max_price)
    
    query = query.offset(search_params.offset).limit(search_params.limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_collector_by_id(
    db: AsyncSession, 
    collector_id: UUID
) -> Optional[CollectorProfile]:
    result = await db.execute(
        select(CollectorProfile)
        .where(CollectorProfile.id == collector_id)
    )
    return result.scalar_one_or_none()