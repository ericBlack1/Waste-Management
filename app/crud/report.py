from sqlalchemy.orm import Session
from app.models.report import IllegalDumpReport
from app.schemas.report import ReportCreate, ReportStatusEnum

def create_report(db: Session, report: ReportCreate, user_id: int, image_url: str):
    db_report = IllegalDumpReport(
        user_id=user_id,
        image_url=image_url,
        location=report.location,
        description=report.description,
        waste_type=report.waste_type,
        severity=report.severity
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_user_reports(db: Session, user_id: int, status: str = None):
    query = db.query(IllegalDumpReport).filter(IllegalDumpReport.user_id == user_id)
    if status:
        query = query.filter(IllegalDumpReport.status == status)
    return query.all()

def get_report_by_id(db: Session, report_id: int, user_id: int = None):
    query = db.query(IllegalDumpReport)
    if user_id:
        query = query.filter(IllegalDumpReport.user_id == user_id)
    return query.filter(IllegalDumpReport.id == report_id).first()

def update_report_status(db: Session, report_id: int, status: ReportStatusEnum):
    db_report = db.query(IllegalDumpReport).filter(IllegalDumpReport.id == report_id).first()
    if not db_report:
        return None
    db_report.status = status
    db.commit()
    db.refresh(db_report)
    return db_report