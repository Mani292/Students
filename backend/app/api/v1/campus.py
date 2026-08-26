from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.all_models import (
    LibraryBook, LibraryBorrowRecord, HostelRoom, HostelComplaint,
    TransportRoute, BusPass, CampusEvent, EventRegistration,
    StudentSkillPassport, Student, User, UserRole
)
from app.schemas.schemas import (
    LibraryBookOut, LibraryBorrowRequest, LibraryBorrowOut,
    HostelRoomOut, HostelComplaintCreate, HostelComplaintOut,
    TransportRouteOut, BusPassOut,
    CampusEventOut, SkillPassportCreate, SkillPassportOut
)
from app.core.rbac import require_roles, get_current_user

router = APIRouter(prefix="/campus", tags=["Campus Services: Library, Hostel, Transport, Events and Passport"])

# --- Library Subsystem ---
@router.get("/library/books", response_model=List[LibraryBookOut])
def list_library_books(db: Session = Depends(get_db)):
    books = db.query(LibraryBook).all()
    if not books:
        default_books = [
            LibraryBook(isbn="978-0131103627", title="The C Programming Language", author="Brian W. Kernighan, Dennis M. Ritchie", category="Computer Science", total_copies=6, available_copies=5),
            LibraryBook(isbn="978-0262033848", title="Introduction to Algorithms", author="Thomas H. Cormen, Charles E. Leiserson", category="Algorithms", total_copies=8, available_copies=6),
            LibraryBook(isbn="978-0134092669", title="Operating Systems: Three Easy Pieces", author="Remzi H. Arpaci-Dusseau", category="Systems", total_copies=5, available_copies=4)
        ]
        db.add_all(default_books)
        db.commit()
        books = db.query(LibraryBook).all()
    return books

@router.post("/library/borrow", response_model=LibraryBorrowOut)
def borrow_book(
    req: LibraryBorrowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    book = db.query(LibraryBook).filter(LibraryBook.id == req.book_id).first()
    if not book or book.available_copies <= 0:
        raise HTTPException(status_code=400, detail="Book not available for borrowing")

    book.available_copies -= 1
    borrow = LibraryBorrowRecord(
        book_id=book.id,
        student_id=student.id,
        due_date=datetime.utcnow() + timedelta(days=14),
        status="BORROWED"
    )
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow

# --- Hostel Subsystem ---
@router.get("/hostel/rooms", response_model=List[HostelRoomOut])
def list_hostel_rooms(db: Session = Depends(get_db)):
    rooms = db.query(HostelRoom).all()
    if not rooms:
        defaults = [
            HostelRoom(hostel_name="Aryabhata Hall", room_number="A-101", capacity=2, occupied_count=2),
            HostelRoom(hostel_name="Aryabhata Hall", room_number="A-102", capacity=2, occupied_count=1),
            HostelRoom(hostel_name="Gargi Hall", room_number="G-201", capacity=3, occupied_count=2)
        ]
        db.add_all(defaults)
        db.commit()
        rooms = db.query(HostelRoom).all()
    return rooms

@router.post("/hostel/complaints", response_model=HostelComplaintOut)
def lodge_hostel_complaint(
    req: HostelComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    comp = HostelComplaint(
        student_id=student.id,
        category=req.category,
        description=req.description,
        status="OPEN"
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp

# --- Transport Subsystem ---
@router.get("/transport/routes", response_model=List[TransportRouteOut])
def list_transport_routes(db: Session = Depends(get_db)):
    routes = db.query(TransportRoute).all()
    if not routes:
        defaults = [
            TransportRoute(route_name="Route 1 - North Express", bus_number="BUS-01", stops=["Central Station", "Metro Hub", "Science Park", "Campus Main Gate"], schedule_time="07:30 AM / 05:30 PM"),
            TransportRoute(route_name="Route 2 - South Tech Corridor", bus_number="BUS-02", stops=["South Terminal", "City Square", "Tech Tower", "Campus Gate 2"], schedule_time="07:45 AM / 05:45 PM")
        ]
        db.add_all(defaults)
        db.commit()
        routes = db.query(TransportRoute).all()
    return routes

# --- Events and Hackathons ---
@router.get("/events", response_model=List[CampusEventOut])
def list_events(db: Session = Depends(get_db)):
    events = db.query(CampusEvent).all()
    if not events:
        defaults = [
            CampusEvent(title="Smart University Hackathon 2026", category="HACKATHON", description="48-hour build sprint focusing on AI, Cloud, and Smart Campus applications.", event_date=datetime.utcnow() + timedelta(days=10), venue="University Innovation Center", registration_open=True),
            CampusEvent(title="Hands-on RAG and LLM Deployment Workshop", category="WORKSHOP", description="Practical deep-dive into building production AI agents and guardrails.", event_date=datetime.utcnow() + timedelta(days=15), venue="Seminar Hall B", registration_open=True)
        ]
        db.add_all(defaults)
        db.commit()
        events = db.query(CampusEvent).all()
    return events

# --- Student Skill Passport ---
@router.get("/skill-passport/me", response_model=List[SkillPassportOut])
def get_my_skill_passport(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    records = db.query(StudentSkillPassport).filter(StudentSkillPassport.student_id == student.id).all()
    if not records:
        defaults = [
            StudentSkillPassport(student_id=student.id, skill_name="Python Microservices", proficiency="ADVANCED", verified_by_faculty=True, badge_title="Backend Specialist", details={"certifications": ["Certified Python Developer"], "projects": ["Smart University Ecosystem"]}),
            StudentSkillPassport(student_id=student.id, skill_name="AI / RAG Architecture", proficiency="INTERMEDIATE", verified_by_faculty=True, badge_title="AI Practitioner", details={"hackathons": ["Top 5 Finalist Campus Hack 2025"]})
        ]
        db.add_all(defaults)
        db.commit()
        records = db.query(StudentSkillPassport).filter(StudentSkillPassport.student_id == student.id).all()
    return records