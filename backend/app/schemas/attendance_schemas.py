from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.all_models import AttendanceStatus

class SessionStartRequest(BaseModel):
    class_id: int
    duration_minutes: int = Field(default=45, ge=1, le=180)

class SessionOut(BaseModel):
    session_id: int
    class_id: int
    session_token: str
    totp_secret: str
    current_totp_code: str
    start_time: datetime
    end_time: datetime
    is_active: bool

class AttendanceSubmitRequest(BaseModel):
    session_token: str
    totp_code: str
    device_fingerprint: str = Field(min_length=8, max_length=256)
    ip_address: Optional[str] = "127.0.0.1"

class AttendanceRecordOut(BaseModel):
    id: int
    session_id: int
    student_id: int
    timestamp: datetime
    status: AttendanceStatus

    class Config:
        from_attributes = True

class AttendanceAnomalyOut(BaseModel):
    id: int
    record_id: int
    reason: str
    severity: str
    is_resolved: bool

    class Config:
        from_attributes = True
