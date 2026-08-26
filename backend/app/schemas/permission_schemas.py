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
    action: str # "APPROVE", "REJECT", "FORWARD"
    comments: Optional[str] = None

class PermissionOut(BaseModel):
    id: int
    student_id: int
    student_roll_number: Optional[str] = None
    student_name: Optional[str] = None
    reason: str
    start_date: datetime
    end_date: datetime
    proof_url: Optional[str]
    comments: Optional[str]
    status: PermissionStatus
    created_at: datetime

    class Config:
        from_attributes = True
