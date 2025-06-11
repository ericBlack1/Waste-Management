from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_async_db
from app.schemas.collector import *
from app.crud.collector import *

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/collectors", tags=["collectors"])

@router.get("/", response_model=List[SimpleCollectorResponse])
async def get_all_collectors(
    location: Optional[str] = Query(None, description="Filter by location"),
    waste_type: Optional[str] = Query(None, description="Filter by waste type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all collectors - simplified endpoint with no relations"""
    try:
        logger.info("Fetching all collectors (simplified)")
        logger.info(f"Filters: location={location}, waste_type={waste_type}, limit={limit}, offset={offset}")
        
        # Get collectors with optional filters
        collectors = await get_collectors_with_optional_filters(
            db=db,
            location=location,
            waste_type=waste_type,
            limit=limit,
            offset=offset
        )
        
        logger.info(f"Retrieved {len(collectors)} collectors from database")
        
        if not collectors:
            logger.info("No collectors found")
            return []
        
        # Convert to response models
        collector_responses = []
        for collector in collectors:
            try:
                response = SimpleCollectorResponse(
                    id=collector.id,
                    user_id=collector.user_id,
                    location=collector.location,
                    price_min=collector.price_min,
                    price_max=collector.price_max,
                    working_days=collector.working_days,
                    waste_types=collector.waste_types,
                    quantity_accepted=getattr(collector, 'quantity_accepted', []),
                    whatsapp_number=getattr(collector, 'whatsapp_number', None),
                    average_rating=getattr(collector, 'average_rating', 0.0)
                )
                
                collector_responses.append(response)
                logger.debug(f"Processed collector {collector.id}")
                
            except Exception as e:
                logger.error(f"Error processing collector {collector.id}: {str(e)}")
                # Continue with other collectors instead of failing entirely
                continue
        
        logger.info(f"Successfully processed {len(collector_responses)} collectors")
        return collector_responses
        
    except Exception as e:
        logger.error(f"Error in get_all_collectors: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch collectors"
        )

@router.get("/raw", response_model=List[dict])
async def get_collectors_raw(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db)
):
    """Get collectors as raw dictionary - for debugging"""
    try:
        logger.info("Fetching collectors as raw data")
        
        collectors = await get_all_collectors_simple(db)
        
        # Convert to simple dictionaries
        raw_collectors = []
        for collector in collectors[offset:offset+limit]:
            try:
                raw_data = {
                    "id": str(collector.id) if collector.id else None,
                    "user_id": collector.user_id,
                    "location": collector.location,
                    "price_min": collector.price_min,
                    "price_max": collector.price_max,
                    "working_days": collector.working_days,
                    "working_days_type": str(type(collector.working_days)),
                    "waste_types": collector.waste_types,
                    "waste_types_type": str(type(collector.waste_types)),
                    "quantity_accepted": getattr(collector, 'quantity_accepted', None),
                    "whatsapp_number": getattr(collector, 'whatsapp_number', None),
                    "average_rating": getattr(collector, 'average_rating', 0.0),
                }
                raw_collectors.append(raw_data)
            except Exception as e:
                logger.error(f"Error processing raw collector {collector.id}: {str(e)}")
                continue
        
        return raw_collectors
        
    except Exception as e:
        logger.error(f"Error in get_collectors_raw: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
 
@router.get("/{collector_id}", response_model=SimpleCollectorResponse)
async def get_collector_by_id(
    collector_id: Union[UUID, int],
    db: AsyncSession = Depends(get_async_db)
):
    """Get single collector by ID - simplified"""
    try:
        logger.info(f"Fetching collector by ID: {collector_id}")
        
        collector = await get_collector_by_id_simple(db, collector_id)
        if not collector:
            raise HTTPException(status_code=404, detail="Collector not found")
        
        response = SimpleCollectorResponse(
            id=collector.id,
            user_id=collector.user_id,
            location=collector.location,
            price_min=collector.price_min,
            price_max=collector.price_max,
            working_days=collector.working_days,
            waste_types=collector.waste_types,
            quantity_accepted=getattr(collector, 'quantity_accepted', []),
            whatsapp_number=getattr(collector, 'whatsapp_number', None),
            average_rating=getattr(collector, 'average_rating', 0.0)
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collector by ID: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to get collector"
        )
