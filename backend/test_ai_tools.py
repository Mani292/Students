import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import Base, engine, SessionLocal
from app.models.all_models import User, UserRole, Student, Department
from app.services.ai_tools import get_student_profile_tool, get_attendance_summary_tool, search_university_knowledge_tool

def test_ai_tools():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    dept = Department(code="CIVIL", name="Civil Eng")
    db.add(dept)
    db.commit()

    user = User(email="civil_stud@univ.edu", hashed_password="h", full_name="Dan Builder", role=UserRole.STUDENT)
    db.add(user)
    db.commit()

    student = Student(user_id=user.id, roll_number="CIV001", department_id=dept.id, cgpa=3.8, skills=["AutoCAD", "Structural Analysis"])
    db.add(student)
    db.commit()

    # Test profile tool scoping
    profile = get_student_profile_tool(user, db)
    assert profile["roll_number"] == "CIV001"
    assert "AutoCAD" in profile["skills"]

    # Test attendance scoping
    att = get_attendance_summary_tool(user, db)
    assert att["attendance_percentage"] == 100.0

    print("Permission-Aware AI Tools test PASSED.")

if __name__ == "__main__":
    test_ai_tools()
