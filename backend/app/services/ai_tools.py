from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.all_models import (
    User, UserRole, Student, AttendanceRecord, PermissionRequest, ServiceRequest,
    Enrollment, ClassSession, Course, Assignment, CampusEvent, LibraryBook
)
from app.services.rag_engine import search_knowledge_base

def get_student_profile_tool(user: User, db: Session) -> Dict[str, Any]:
    """Retrieves student profile for the authenticated user only."""
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        return {"error": "No student profile found for user"}
    return {
        "full_name": user.full_name,
        "email": user.email,
        "roll_number": student.roll_number,
        "department": student.department.name if student.department else "N/A",
        "year": student.year,
        "semester": student.semester,
        "cgpa": student.cgpa,
        "skills": student.skills or []
    }

def get_attendance_summary_tool(user: User, db: Session) -> Dict[str, Any]:
    """Retrieves attendance summary for the authenticated student only."""
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        return {"error": "User is not a student"}
    records = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student.id).all()
    total = len(records)
    present = sum(1 for r in records if r.status == "PRESENT")
    pct = (present / total * 100.0) if total > 0 else 100.0
    return {
        "total_classes": total,
        "classes_attended": present,
        "attendance_percentage": round(pct, 1),
        "status": "SAFE" if pct >= 75.0 else "SHORTAGE_WARNING"
    }

def get_permission_status_tool(user: User, db: Session) -> List[Dict[str, Any]]:
    """Retrieves leave & permission requests for the authenticated user."""
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        return []
    reqs = db.query(PermissionRequest).filter(PermissionRequest.student_id == student.id).all()
    return [{
        "id": r.id,
        "reason": r.reason,
        "status": r.status.value,
        "created_at": r.created_at.strftime("%Y-%m-%d")
    } for r in reqs]

def get_timetable_tool(user: User, db: Session) -> List[Dict[str, Any]]:
    """Retrieves today's timetable/classes for the enrolled student."""
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        return []
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student.id).all()
    results = []
    for e in enrollments:
        cls = e.class_session
        if cls:
            results.append({
                "class_id": cls.id,
                "course_code": cls.course.code if cls.course else "CS101",
                "course_title": cls.course.title if cls.course else "Core Subject",
                "room": cls.room_number,
                "semester": cls.semester
            })
    return results

def get_assignments_tool(user: User, db: Session) -> List[Dict[str, Any]]:
    """Retrieves active assignments for enrolled classes."""
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        return []
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student.id).all()
    class_ids = [e.class_id for e in enrollments]
    assignments = db.query(Assignment).filter(Assignment.class_id.in_(class_ids)).all() if class_ids else []
    return [{
        "id": a.id,
        "title": a.title,
        "description": a.description,
        "due_date": a.due_date.strftime("%Y-%m-%d"),
        "max_marks": a.max_marks
    } for a in assignments]

def get_service_requests_tool(user: User, db: Session) -> List[Dict[str, Any]]:
    """Retrieves service center requests for the authenticated student."""
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        return []
    reqs = db.query(ServiceRequest).filter(ServiceRequest.student_id == student.id).all()
    return [{
        "id": s.id,
        "service_type": s.service_type.value,
        "status": s.status.value,
        "verification_token": s.verification_token
    } for s in reqs]

def get_campus_events_tool(db: Session) -> List[Dict[str, Any]]:
    """Retrieves upcoming campus events and hackathons."""
    events = db.query(CampusEvent).all()
    return [{
        "id": ev.id,
        "title": ev.title,
        "category": ev.category,
        "event_date": ev.event_date.strftime("%Y-%m-%d"),
        "venue": ev.venue
    } for ev in events]

def get_library_books_tool(query: str, db: Session) -> List[Dict[str, Any]]:
    """Searches library catalog for books."""
    books = db.query(LibraryBook).filter(
        (LibraryBook.title.ilike(f"%{query}%")) | (LibraryBook.author.ilike(f"%{query}%"))
    ).all()
    return [{
        "id": b.id,
        "title": b.title,
        "author": b.author,
        "category": b.category,
        "available_copies": b.available_copies
    } for b in books]

def search_university_knowledge_tool(query: str, db: Session) -> List[Dict[str, Any]]:
    """Searches university RAG knowledge base."""
    return search_knowledge_base(query, db)
