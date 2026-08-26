from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from app.models.all_models import UserRole, AttendanceStatus, PermissionStatus, ServiceType, ServiceRequestStatus, NotificationPriority

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DepartmentCreate(BaseModel):
    code: str
    name: str

class DepartmentOut(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    code: str
    title: str
    department_id: int
    credits: int = 3

class CourseOut(BaseModel):
    id: int
    code: str
    title: str
    department_id: int
    credits: int

    class Config:
        from_attributes = True

class ClassSessionCreate(BaseModel):
    course_id: int
    faculty_id: int
    academic_year: str
    semester: int
    room_number: str

class ClassSessionOut(BaseModel):
    id: int
    course_id: int
    faculty_id: int
    academic_year: str
    semester: int
    room_number: str

    class Config:
        from_attributes = True
