from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.all_models import User, UserRole, Student, AttendanceRecord, PermissionRequest, ServiceRequest
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

def search_university_knowledge_tool(query: str, db: Session) -> List[Dict[str, Any]]:
    """Searches university RAG knowledge base."""
    return search_knowledge_base(query, db)
