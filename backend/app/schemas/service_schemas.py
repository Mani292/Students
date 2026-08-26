from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.all_models import ServiceType, ServiceRequestStatus

class ServiceCreateRequest(BaseModel):
    service_type: ServiceType
    details: Dict[str, Any] = {}

class ServiceProcessRequest(BaseModel):
    status: ServiceRequestStatus
    issued_document_url: Optional[str] = None

class ServiceOut(BaseModel):
    id: int
    student_id: int
    service_type: ServiceType
    details: Dict[str, Any]
    status: ServiceRequestStatus
    issued_document_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class DigitalIDOut(BaseModel):
    full_name: str
    roll_number: str
    department_name: str
    year: int
    semester: int
    verification_token: str

class DigitalIDVerificationOut(BaseModel):
    valid: bool
    student_name: str
    roll_number: str
    department: str
    year: int
    status: str
