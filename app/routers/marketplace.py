from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import os
from app.core.database import get_async_db
from app.schemas.marketplace import (
    ListingCreate, ListingResponse, ListingSummary, ListingSearchParams, ListingUpdate
)
from app.crud.marketplace import (
    create_listing, get_listing, get_listings, update_listing_status
)
from app.models.marketplace import ListingStatusEnum
from app.models.collector import WasteTypeEnum, QuantityEnum
from app.dependencies import get_current_user, get_current_collector, get_current_resident
from app.schemas.user import UserOut

router = APIRouter(prefix="/marketplace/listings", tags=["marketplace"])

# Ensure uploads directory exists (e.g. in the project root)
os.makedirs("uploads", exist_ok=True)

@router.post("/", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_marketplace_listing(
    title: str = Query(...),
    description: Optional[str] = Query(None),
    waste_type: WasteTypeEnum = Query(...),
    price: float = Query(..., gt=0),
    quantity: str = Query(...),
    location: str = Query(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: UserOut = Depends(get_current_resident)
):
    # Convert the quantity string to QuantityEnum
    quantity_map = {
        "small": QuantityEnum.SMALL, 
        "medium": QuantityEnum.MEDIUM, 
        "large": QuantityEnum.LARGE
    }
    quantity_enum = quantity_map.get(quantity.lower())
    
    # Validate quantity input
    if quantity_enum is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid quantity '{quantity}'. Must be one of: small, medium, large"
        )
    
    # Save the uploaded image
    image_filename = f"{current_user.id}_{image.filename}"
    image_path = os.path.join("uploads", image_filename)
    with open(image_path, "wb") as f:
         f.write(await image.read())
    image_url = f"/uploads/{image_filename}"

    # Create a ListingCreate instance
    listing_in = ListingCreate(
        title=title,
        description=description,
        waste_type=waste_type,
        price=price,
        quantity=quantity_enum,  # Pass the enum directly, not its value
        location=location,
        image_url=image_url
    )
    
    db_listing = await create_listing(db, listing_in, resident_id=current_user.id)
    return ListingResponse(
        **db_listing.__dict__,
        resident_name=current_user.full_name,
        collector_name=None
    )

@router.get("/", response_model=List[ListingSummary])
async def get_all_listings(
    db: AsyncSession = Depends(get_async_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    params = ListingSearchParams(limit=limit, offset=offset, status=ListingStatusEnum.AVAILABLE)
    listings = await get_listings(db, params)
    return [
        ListingSummary(
            **listing.__dict__,
            resident_name=listing.resident.full_name
        ) for listing in listings
    ]

@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing_by_id(
    listing_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    listing = await get_listing(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingResponse(
        **listing.__dict__,
        resident_name=listing.resident.full_name,
        collector_name=listing.collector.full_name if listing.collector else None
    )

@router.get("/search", response_model=List[ListingSummary])
async def search_listings(
    waste_type: Optional[WasteTypeEnum] = Query(None),
    location: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    params = ListingSearchParams(
        waste_type=waste_type,
        location=location,
        min_price=min_price,
        max_price=max_price,
        status=ListingStatusEnum.AVAILABLE,
        limit=limit,
        offset=offset
    )
    listings = await get_listings(db, params)
    return [
        ListingSummary(
            **listing.__dict__,
            resident_name=listing.resident.full_name
        ) for listing in listings
    ]

@router.patch("/{listing_id}/status", response_model=ListingResponse)
async def update_listing_status_endpoint(
    listing_id: int,
    new_status: ListingStatusEnum,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserOut = Depends(get_current_collector)
):
    listing = await update_listing_status(db, listing_id, new_status, collector_id=current_user.id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingResponse(
        **listing.__dict__,
        resident_name=listing.resident.full_name,
        collector_name=listing.collector.full_name if listing.collector else None
    ) 