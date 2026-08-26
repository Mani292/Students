import os
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.models.all_models import User, UserRole, Student, Department

client = TestClient(app)

def test_campus_services():
    db = SessionLocal()
    try:
        # Create student test user if needed
        student_user = db.query(User).filter(User.email == "campus_student@univ.edu").first()
        if not student_user:
            student_user = User(
                email="campus_student@univ.edu",
                hashed_password="hash",
                full_name="Campus Student",
                role=UserRole.STUDENT
            )
            db.add(student_user)
            db.commit()
            db.refresh(student_user)

            dept = db.query(Department).first()
            if not dept:
                dept = Department(code="CS", name="Computer Science")
                db.add(dept)
                db.commit()
                db.refresh(dept)

            stu = Student(
                user_id=student_user.id,
                roll_number="CAMPUS001",
                department_id=dept.id,
                year=2,
                semester=3,
                cgpa=3.9
            )
            db.add(stu)
            db.commit()
            db.refresh(stu)

        token = create_access_token(subject=student_user.id, role=student_user.role.value)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Test Library Books List
        res = client.get("/api/v1/campus/library/books", headers=headers)
        assert res.status_code == 200
        books = res.json()
        assert len(books) >= 1
        book_id = books[0]["id"]

        # 2. Test Borrow Book
        b_res = client.post("/api/v1/campus/library/borrow", json={"book_id": book_id}, headers=headers)
        assert b_res.status_code == 200
        assert b_res.json()["status"] == "BORROWED"

        # 3. Test Hostel Rooms & Complaint
        h_res = client.get("/api/v1/campus/hostel/rooms", headers=headers)
        assert h_res.status_code == 200
        assert len(h_res.json()) >= 1

        c_res = client.post("/api/v1/campus/hostel/complaints", json={"category": "PLUMBING", "description": "Sink leakage"}, headers=headers)
        assert c_res.status_code == 200
        assert c_res.json()["status"] == "OPEN"

        # 4. Test Transport Routes
        t_res = client.get("/api/v1/campus/transport/routes", headers=headers)
        assert t_res.status_code == 200
        assert len(t_res.json()) >= 1

        # 5. Test Events
        e_res = client.get("/api/v1/campus/events", headers=headers)
        assert e_res.status_code == 200
        assert len(e_res.json()) >= 1

        # 6. Test Skill Passport
        p_res = client.get("/api/v1/campus/skill-passport/me", headers=headers)
        assert p_res.status_code == 200
        assert len(p_res.json()) >= 1

        print("Campus Services (Library, Hostel, Transport, Events & Passport) tests PASSED.")
    finally:
        db.close()

if __name__ == "__main__":
    test_campus_services()