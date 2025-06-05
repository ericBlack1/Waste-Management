from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.report import IllegalDumpReport
from app.schemas.report import ReportCreate, ReportOut, ReportList, ReportStatusUpdate
from app.schemas.user import UserOut
from app.crud.report import (
    create_report,
    get_user_reports,
    get_report_by_id,
    update_report_status
)
from app.core.file_handling import save_uploaded_file
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/dumping", response_model=ReportOut)
async def create_dumping_report(
    image: UploadFile = File(...),
    location: str = Form(...),
    description: Optional[str] = Form(None),
    waste_type: str = Form(...),
    severity: str = Form(...),
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    try:
        # Save the uploaded file
        filename, image_url = save_uploaded_file(image)
        
        # Create report data
        report_data = ReportCreate(
            location=location,
            description=description,
            waste_type=waste_type,
            severity=severity
        )
        
        # Create report in database
        db_report = create_report(db, report_data, current_user.id, image_url)
        return db_report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/dumping/mine", response_model=ReportList)
def get_my_reports(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    reports = get_user_reports(db, current_user.id, status)
    return {"reports": reports, "count": len(reports)}

@router.get("/dumping/{report_id}", response_model=ReportOut)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    report = get_report_by_id(db, report_id, current_user.id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    return report

@router.patch("/dumping/{report_id}/status", response_model=ReportOut)
def update_report_status(
    report_id: int,
    status_update: ReportStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Note: Using User model directly
):
    # First get the report without user filter to check ownership
    db_report = db.query(IllegalDumpReport).filter(IllegalDumpReport.id == report_id).first()
    
    if not db_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if current user is the report owner
    if db_report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reports"
        )
    
    # Update the status
    db_report.status = status_update.status
    db.commit()
    db.refresh(db_report)
    return db_report