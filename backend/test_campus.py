import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.session import Base, engine, SessionLocal
from app.models.all_models import (
    User, UserRole, Department, Student, LibraryBook, TransportRoute, CampusEvent, HostelComplaint
)
from app.core.security import get_password_hash, create_access_token
from app.api.v1.campus import router as campus_router

app = FastAPI()
app.include_router(campus_router, prefix="/api/v1")

def test_campus_api():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    dept = db.query(Department).filter(Department.code == "CS_CAMPUS").first()
    if not dept:
        dept = Department(code="CS_CAMPUS", name="Computer Science Campus")
        db.add(dept)
        db.commit()

    user = db.query(User).filter(User.email == "campus_student@univ.edu").first()
    if not user:
        user = User(email="campus_student@univ.edu", hashed_password=get_password_hash("pass"), full_name="Campus Student", role=UserRole.STUDENT)
        db.add(user)
        db.commit()

    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        student = Student(user_id=user.id, roll_number="CAMPUS001", department_id=dept.id, skills=["Python", "FastAPI"])
        db.add(student)
        db.commit()

    # Seed book, transport, event
    if not db.query(LibraryBook).filter(LibraryBook.isbn == "978-0131103627").first():
        book = LibraryBook(isbn="978-0131103627", title="The C Programming Language", author="Kernighan & Ritchie", category="Computer Science", total_copies=5, available_copies=3)
        db.add(book)

    if not db.query(TransportRoute).filter(TransportRoute.bus_number == "BUS-101").first():
        route = TransportRoute(route_name="North Campus Shuttle", bus_number="BUS-101", pickup_points=["Central Library", "Main Gate"], departure_time="08:00 AM")
        db.add(route)

    if not db.query(CampusEvent).filter(CampusEvent.title == "Smart Hackathon 2025").first():
        event = CampusEvent(title="Smart Hackathon 2025", description="24-Hour AI Coding Competition", category="Hackathon", event_date=datetime.utcnow(), location="Auditorium A", organizer="Computer Society")
        db.add(event)

    db.commit()

    client = TestClient(app)
    token = create_access_token(subject=user.id, role="STUDENT")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test Library Books List
    res = client.get("/api/v1/campus/library/books")
    assert res.status_code == 200, res.text
    assert len(res.json()) >= 1

    # 2. Test Transport Routes
    res = client.get("/api/v1/campus/transport/routes")
    assert res.status_code == 200, res.text
    assert len(res.json()) >= 1

    # 3. Test Campus Events
    res = client.get("/api/v1/campus/events")
    assert res.status_code == 200, res.text
    assert len(res.json()) >= 1

    # 4. Test Hostel Complaint
    res = client.post(
        "/api/v1/campus/hostel/complaints",
        json={"room_number": "B-304", "issue_type": "Plumbing", "description": "Water leak in bathroom"},
        headers=headers
    )
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "OPEN"

    # 5. Test Student Skill Passport
    res = client.get("/api/v1/campus/passport/me", headers=headers)
    assert res.status_code == 200, res.text
    assert "verified_skills" in res.json()

    print("Campus Ecosystem REST API test PASSED.")

if __name__ == "__main__":
    test_campus_api()
