from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.all_models import PermissionStatus

class PermissionApplyRequest(BaseModel):
    reason: str
    start_date: datetime
    end_date: datetime
    proof_url: Optional[str] = None

class PermissionActionRequest(BaseModel):
    action: str # "APPROVE", "REJECT", "FORWARD_HOD"
    comments: Optional[str] = None

class PermissionOut(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    reason: str
    start_date: datetime
    end_date: datetime
    proof_url: Optional[str] = None
    comments: Optional[str] = None
    faculty_comment: Optional[str] = None
    hod_comment: Optional[str] = None
    status: PermissionStatus
    created_at: datetime

    class Config:
        from_attributes = True
