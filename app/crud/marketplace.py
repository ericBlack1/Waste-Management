from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.marketplace import Listing, ListingStatusEnum
from app.schemas.marketplace import ListingCreate, ListingUpdate, ListingSearchParams

async def create_listing(db: AsyncSession, listing: ListingCreate, resident_id: int) -> Listing:
    db_listing = Listing(
        resident_id=resident_id,
        title=listing.title,
        description=listing.description,
        waste_type=listing.waste_type,
        price=listing.price,
        quantity=listing.quantity,
        location=listing.location,
        image_url=listing.image_url,
        status=ListingStatusEnum.AVAILABLE
    )
    db.add(db_listing)
    await db.commit()
    await db.refresh(db_listing)
    return db_listing

async def get_listing(db: AsyncSession, listing_id: int) -> Optional[Listing]:
    result = await db.execute(
        select(Listing)
        .options(selectinload(Listing.resident), selectinload(Listing.collector))
        .where(Listing.id == listing_id)
    )
    return result.scalar_one_or_none()

async def get_listings(
    db: AsyncSession,
    search_params: ListingSearchParams,
    include_sold: bool = False
) -> List[Listing]:
    query = select(Listing).options(
        selectinload(Listing.resident),
        selectinload(Listing.collector)
    )
    
    # Build filters
    filters = []
    
    if search_params.waste_type:
        filters.append(Listing.waste_type == search_params.waste_type)
    
    if search_params.location:
        filters.append(Listing.location.ilike(f"%{search_params.location}%"))
    
    if search_params.min_price is not None:
        filters.append(Listing.price >= search_params.min_price)
    
    if search_params.max_price is not None:
        filters.append(Listing.price <= search_params.max_price)
    
    if search_params.status:
        filters.append(Listing.status == search_params.status)
    elif not include_sold:
        filters.append(Listing.status != ListingStatusEnum.SOLD)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Add pagination
    query = query.offset(search_params.offset).limit(search_params.limit)
    
    # Order by creation date (newest first)
    query = query.order_by(Listing.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_listing_status(
    db: AsyncSession,
    listing_id: int,
    new_status: ListingStatusEnum,
    collector_id: Optional[int] = None
) -> Optional[Listing]:
    listing = await get_listing(db, listing_id)
    if not listing:
        return None
    
    listing.status = new_status
    listing.updated_at = datetime.utcnow()
    
    if new_status == ListingStatusEnum.RESERVED:
        listing.collector_id = collector_id
        listing.reserved_at = datetime.utcnow()
    elif new_status == ListingStatusEnum.SOLD:
        listing.collector_id = collector_id
        listing.sold_at = datetime.utcnow()
    elif new_status == ListingStatusEnum.AVAILABLE:
        listing.collector_id = None
        listing.reserved_at = None
        listing.sold_at = None
    
    await db.commit()
    await db.refresh(listing)
    return listing

async def update_listing(
    db: AsyncSession,
    listing_id: int,
    listing_update: ListingUpdate
) -> Optional[Listing]:
    listing = await get_listing(db, listing_id)
    if not listing:
        return None
    
    update_data = listing_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(listing, field, value)
    
    listing.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(listing)
    return listing

async def get_user_listings(
    db: AsyncSession,
    user_id: int,
    include_sold: bool = False
) -> List[Listing]:
    query = select(Listing).options(
        selectinload(Listing.resident),
        selectinload(Listing.collector)
    ).where(Listing.resident_id == user_id)
    
    if not include_sold:
        query = query.where(Listing.status != ListingStatusEnum.SOLD)
    
    query = query.order_by(Listing.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_collector_reservations(
    db: AsyncSession,
    collector_id: int
) -> List[Listing]:
    query = select(Listing).options(
        selectinload(Listing.resident),
        selectinload(Listing.collector)
    ).where(
        and_(
            Listing.collector_id == collector_id,
            or_(
                Listing.status == ListingStatusEnum.RESERVED,
                Listing.status == ListingStatusEnum.SOLD
            )
        )
    ).order_by(Listing.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all() 