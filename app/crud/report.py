from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.report import IllegalDumpReport
from app.schemas.report import ReportCreate, ReportStatusEnum

async def create_report(db: AsyncSession, report: ReportCreate, user_id: int, image_url: str):
    db_report = IllegalDumpReport(
        user_id=user_id,
        image_url=image_url,
        location=report.location,
        description=report.description,
        waste_type=report.waste_type,
        severity=report.severity,
        status=ReportStatusEnum.PENDING  # Set initial status
    )
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report

async def get_user_reports(db: AsyncSession, user_id: int, status: str = None):
    query = select(IllegalDumpReport).where(IllegalDumpReport.user_id == user_id)
    if status:
        query = query.where(IllegalDumpReport.status == status)
    result = await db.execute(query)
    return result.scalars().all()

async def get_report_by_id(db: AsyncSession, report_id: int, user_id: int = None):
    query = select(IllegalDumpReport).where(IllegalDumpReport.id == report_id)
    if user_id:
        query = query.where(IllegalDumpReport.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_report_status(db: AsyncSession, report_id: int, status: ReportStatusEnum):
    query = select(IllegalDumpReport).where(IllegalDumpReport.id == report_id)
    result = await db.execute(query)
    db_report = result.scalar_one_or_none()
    
    if not db_report:
        return None
        
    db_report.status = status
    await db.commit()
    await db.refresh(db_report)
    return db_report