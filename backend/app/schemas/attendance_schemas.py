from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.all_models import AttendanceStatus

class SessionStartRequest(BaseModel):
    class_id: int
    duration_minutes: int = 45
    allowed_latitude: Optional[float] = None
    allowed_longitude: Optional[float] = None
    radius_meters: Optional[float] = 150.0

class SessionOut(BaseModel):
    session_id: int
    class_id: int
    session_token: str
    totp_secret: str
    current_totp_code: str
    start_time: datetime
    end_time: datetime
    is_active: bool
    allowed_latitude: Optional[float] = None
    allowed_longitude: Optional[float] = None
    radius_meters: Optional[float] = 150.0

class AttendanceSubmitRequest(BaseModel):
    session_token: str
    totp_code: str
    device_fingerprint: str
    ip_address: Optional[str] = "127.0.0.1"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AttendanceRecordOut(BaseModel):
    id: int
    session_id: int
    student_id: int
    timestamp: datetime
    device_fingerprint: Optional[str] = None
    status: AttendanceStatus

    class Config:
        from_attributes = True

class AttendanceAnomalyOut(BaseModel):
    id: int
    record_id: int
    reason: str
    severity: str
    is_resolved: bool
    resolution_notes: Optional[str] = None

    class Config:
        from_attributes = True

class AnomalyResolveRequest(BaseModel):
    anomaly_id: int
    resolution_notes: str
    new_status: AttendanceStatus = AttendanceStatus.PRESENT

class AttendanceSummaryOut(BaseModel):
    total_classes: int
    classes_attended: int
    attendance_percentage: float
    status: str
    shortage_warning: bool
