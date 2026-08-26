from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.all_models import (
    LibraryBook, LibraryBorrowRecord, HostelRoom, HostelComplaint,
    TransportRoute, CampusEvent, EventRegistration, StudentSkillPassport,
    User, UserRole, Student
)
from app.core.rbac import require_roles, get_current_user

router = APIRouter(prefix="/campus", tags=["Campus Services Ecosystem"])

# --- Library Schemas & Endpoints ---

class BookOut(BaseModel):
    id: int
    isbn: str
    title: str
    author: str
    category: str
    total_copies: int
    available_copies: int

    class Config:
        from_attributes = True

@router.get("/library/books", response_model=List[BookOut])
def list_library_books(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LibraryBook)
    if category:
        query = query.filter(LibraryBook.category.ilike(f"%{category}%"))
    return query.all()

# --- Hostel Schemas & Endpoints ---

class ComplaintCreateRequest(BaseModel):
    room_number: str
    issue_type: str
    description: str

class ComplaintOut(BaseModel):
    id: int
    student_id: int
    room_number: str
    issue_type: str
    description: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/hostel/complaints", response_model=ComplaintOut)
def submit_hostel_complaint(
    req: ComplaintCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    complaint = HostelComplaint(
        student_id=student.id,
        room_number=req.room_number,
        issue_type=req.issue_type,
        description=req.description,
        status="OPEN"
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint

# --- Transport Schemas & Endpoints ---

class TransportRouteOut(BaseModel):
    id: int
    route_name: str
    bus_number: str
    driver_contact: Optional[str]
    pickup_points: List[str]
    departure_time: str

    class Config:
        from_attributes = True

@router.get("/transport/routes", response_model=List[TransportRouteOut])
def list_transport_routes(db: Session = Depends(get_db)):
    return db.query(TransportRoute).all()

# --- Events Schemas & Endpoints ---

class EventOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    event_date: datetime
    location: str
    organizer: str

    class Config:
        from_attributes = True

@router.get("/events", response_model=List[EventOut])
def list_campus_events(db: Session = Depends(get_db)):
    return db.query(CampusEvent).all()

# --- Student Skill Passport ---

class SkillPassportOut(BaseModel):
    student_id: int
    verified_skills: List[str]
    certifications: List[str]
    achievements: List[str]
    projects_count: int

    class Config:
        from_attributes = True

@router.get("/passport/me", response_model=SkillPassportOut)
def get_my_skill_passport(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    passport = db.query(StudentSkillPassport).filter(StudentSkillPassport.student_id == student.id).first()
    if not passport:
        passport = StudentSkillPassport(
            student_id=student.id,
            verified_skills=student.skills or ["Python", "FastAPI"],
            certifications=["University Python Foundations"],
            achievements=["Dean's List Semester 1"],
            projects_count=3
        )
        db.add(passport)
        db.commit()
        db.refresh(passport)

    return passport
