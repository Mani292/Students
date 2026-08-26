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

# Academic Assignments
class AssignmentCreate(BaseModel):
    class_id: int
    title: str
    description: str
    due_date: datetime
    max_marks: int = 100

class AssignmentOut(BaseModel):
    id: int
    class_id: int
    title: str
    description: str
    due_date: datetime
    max_marks: int
    created_at: datetime

    class Config:
        from_attributes = True

class AssignmentSubmissionCreate(BaseModel):
    assignment_id: int
    submission_text: str
    attachment_url: Optional[str] = None

class AssignmentSubmissionOut(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    submission_text: Optional[str]
    attachment_url: Optional[str]
    submitted_at: datetime
    marks_obtained: Optional[float]
    faculty_feedback: Optional[str]

    class Config:
        from_attributes = True

# Campus: Library
class LibraryBookOut(BaseModel):
    id: int
    isbn: str
    title: str
    author: str
    category: str
    total_copies: int
    available_copies: int

    class Config:
        from_attributes = True

class LibraryBorrowRequest(BaseModel):
    book_id: int

class LibraryBorrowOut(BaseModel):
    id: int
    book_id: int
    student_id: int
    borrowed_at: datetime
    due_date: datetime
    returned_at: Optional[datetime]
    fine_amount: float
    status: str

    class Config:
        from_attributes = True

# Campus: Hostel
class HostelRoomOut(BaseModel):
    id: int
    hostel_name: str
    room_number: str
    capacity: int
    occupied_count: int

    class Config:
        from_attributes = True

class HostelComplaintCreate(BaseModel):
    category: str
    description: str

class HostelComplaintOut(BaseModel):
    id: int
    student_id: int
    category: str
    description: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Campus: Transport
class TransportRouteOut(BaseModel):
    id: int
    route_name: str
    bus_number: str
    stops: List[str]
    schedule_time: str

    class Config:
        from_attributes = True

class BusPassOut(BaseModel):
    id: int
    student_id: int
    route_id: int
    pass_number: str
    valid_until: datetime
    is_active: bool

    class Config:
        from_attributes = True

# Campus: Events & Clubs
class CampusEventOut(BaseModel):
    id: int
    title: str
    category: str
    description: str
    event_date: datetime
    venue: str
    registration_open: bool

    class Config:
        from_attributes = True

# Campus: Skill Passport
class SkillPassportCreate(BaseModel):
    skill_name: str
    proficiency: str = "INTERMEDIATE"
    badge_title: Optional[str] = None
    details: Optional[dict] = {}

class SkillPassportOut(BaseModel):
    id: int
    student_id: int
    skill_name: str
    proficiency: str
    verified_by_faculty: bool
    badge_title: Optional[str]
    details: dict

    class Config:
        from_attributes = True
