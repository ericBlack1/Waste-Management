from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
import logging

# Assuming these imports exist in your project
from app.models.collector import CollectorProfile
from app.models.user import User
from app.schemas.collector import *

logger = logging.getLogger(__name__)
 
async def get_all_collectors_simple(db: AsyncSession) -> List:  # Replace with CollectorProfile
    """Get all collectors without any relations or complex filtering"""
    
    try:
        logger.info("Fetching all collectors (simple)")
        
        # Simple query - no joins, no relations, just raw collector data
        stmt = select(CollectorProfile)
        result = await db.execute(stmt)
        collectors = result.scalars().all()
        
        logger.info(f"Retrieved {len(collectors)} collectors")
        return collectors
        
    except Exception as e:
        logger.error(f"Error in get_all_collectors_simple: {str(e)}", exc_info=True)
        raise

async def get_collectors_with_optional_filters(
    db: AsyncSession, 
    location: Optional[str] = None,
    waste_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List:  # Replace with CollectorProfile
    """Get collectors with optional simple filters, no relations"""
    
    try:
        logger.info("Fetching collectors with optional filters")
        
        # Start with base query
        stmt = select(CollectorProfile)
        
        # Apply simple filters if provided
        if location:
            stmt = stmt.where(CollectorProfile.location.ilike(f"%{location}%"))
            logger.info(f"Applied location filter: {location}")
        
        if waste_type:
            # Simple contains check - adjust based on your database structure
            stmt = stmt.where(CollectorProfile.waste_types.contains([waste_type]))
            logger.info(f"Applied waste_type filter: {waste_type}")
        
        # Add limit and offset
        stmt = stmt.limit(limit).offset(offset)
        
        result = await db.execute(stmt)
        collectors = result.scalars().all()
        
        logger.info(f"Retrieved {len(collectors)} collectors with filters")
        return collectors
        
    except Exception as e:
        logger.error(f"Error in get_collectors_with_optional_filters: {str(e)}", exc_info=True)
        raise

async def get_collector_by_id_simple(db: AsyncSession, collector_id) -> Optional:  # collector_id can be UUID or int
    """Get single collector by ID without relations"""
    
    try:
        logger.info(f"Getting collector by ID: {collector_id}")
        
        stmt = select(CollectorProfile).where(CollectorProfile.id == collector_id)
        result = await db.execute(stmt)
        collector = result.scalar_one_or_none()
        
        if collector:
            logger.info(f"Found collector: {collector_id}")
        else:
            logger.warning(f"Collector not found: {collector_id}")
        
        return collector
        
    except Exception as e:
        logger.error(f"Error in get_collector_by_id_simple: {str(e)}", exc_info=True)
        raise

async def get_collector_by_id(db: AsyncSession, collector_id: UUID) -> Optional:  # Replace with CollectorProfile
    """Get collector by ID with improved error handling"""
    
    try:
        logger.info(f"Getting collector by ID: {collector_id}")
        
        stmt = (
            select(CollectorProfile)
            .options(joinedload(CollectorProfile.user))
            .where(CollectorProfile.id == collector_id)
        )
        
        result = await db.execute(stmt)
        collector = result.unique().scalar_one_or_none()
        
        if collector:
            logger.info(f"Found collector: {collector_id}")
        else:
            logger.warning(f"Collector not found: {collector_id}")
        
        return collector
        
    except Exception as e:
        logger.error(f"Error in get_collector_by_id: {str(e)}", exc_info=True)
        raise

async def check_database_health(db: AsyncSession) -> dict:
    """Health check for database and collector data"""
    
    try:
        # Count collectors
        count_stmt = select(func.count(CollectorProfile.id))
        count_result = await db.execute(count_stmt)
        total_collectors = count_result.scalar()
        
        # Count users
        user_count_stmt = select(func.count(User.id))
        user_count_result = await db.execute(user_count_stmt)
        total_users = user_count_result.scalar()
        
        # Check for orphaned collectors (collectors without users)
        orphaned_stmt = (
            select(func.count(CollectorProfile.id))
            .outerjoin(User, CollectorProfile.user_id == User.id)
            .where(User.id.is_(None))
        )
        orphaned_result = await db.execute(orphaned_stmt)
        orphaned_collectors = orphaned_result.scalar()
        
        # Sample some data types to verify schema
        sample_stmt = select(CollectorProfile).limit(1)
        sample_result = await db.execute(sample_stmt)
        sample_collector = sample_result.scalar_one_or_none()
        
        data_types_info = {}
        if sample_collector:
            data_types_info = {
                "collector_id_type": type(sample_collector.id).__name__,
                "user_id_type": type(sample_collector.user_id).__name__,
                "working_days_type": type(sample_collector.working_days).__name__,
                "waste_types_type": type(sample_collector.waste_types).__name__,
            }
        
        return {
            "status": "healthy",
            "total_collectors": total_collectors,
            "total_users": total_users,
            "orphaned_collectors": orphaned_collectors,
            "data_types": data_types_info,
            "health_check": "passed"
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "health_check": "failed"
        }
