import sys
import os
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.session import Base, engine, SessionLocal
from app.models.all_models import User, UserRole, Department, Course, ClassSession, Faculty, Student, Enrollment
from app.core.security import get_password_hash, create_access_token
from app.api.v1.attendance import router as attendance_router
from app.services.attendance_security import generate_totp_code

app = FastAPI()
app.include_router(attendance_router, prefix="/api/v1")

def test_attendance_api():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    uid = uuid.uuid4().hex[:6]
    dept = Department(code=f"ECE_{uid}", name="Electronics")
    db.add(dept)
    db.commit()

    faculty_user = User(email=f"fac_{uid}@univ.edu", hashed_password=get_password_hash("pass"), full_name="Prof John", role=UserRole.FACULTY)
    student_user1 = User(email=f"stud1_{uid}@univ.edu", hashed_password=get_password_hash("pass"), full_name="Alice", role=UserRole.STUDENT)
    student_user2 = User(email=f"stud2_{uid}@univ.edu", hashed_password=get_password_hash("pass"), full_name="Bob", role=UserRole.STUDENT)
    student_user3 = User(email=f"stud3_{uid}@univ.edu", hashed_password=get_password_hash("pass"), full_name="Cara", role=UserRole.STUDENT)
    db.add_all([faculty_user, student_user1, student_user2, student_user3])
    db.commit()
    db.refresh(faculty_user)
    db.refresh(student_user1)
    db.refresh(student_user2)
    db.refresh(student_user3)

    faculty = Faculty(user_id=faculty_user.id, employee_id=f"EMP_{uid}", department_id=dept.id, designation="Professor")
    student1 = Student(user_id=student_user1.id, roll_number=f"STU1_{uid}", department_id=dept.id)
    student2 = Student(user_id=student_user2.id, roll_number=f"STU2_{uid}", department_id=dept.id)
    student3 = Student(user_id=student_user3.id, roll_number=f"STU3_{uid}", department_id=dept.id)
    db.add_all([faculty, student1, student2, student3])
    db.commit()

    course = Course(code=f"EC_{uid}", title="Signals & Systems", department_id=dept.id)
    db.add(course)
    db.commit()

    cls_sess = ClassSession(course_id=course.id, faculty_id=faculty.id, academic_year="2024-2025", semester=1, room_number="301")
    db.add(cls_sess)
    db.commit()

    db.add_all([
        Enrollment(student_id=student1.id, class_id=cls_sess.id),
        Enrollment(student_id=student2.id, class_id=cls_sess.id),
    ])
    db.commit()

    client = TestClient(app)

    fac_token = create_access_token(subject=faculty_user.id, role="FACULTY")
    stud1_token = create_access_token(subject=student_user1.id, role="STUDENT")
    stud2_token = create_access_token(subject=student_user2.id, role="STUDENT")
    stud3_token = create_access_token(subject=student_user3.id, role="STUDENT")

    res = client.post("/api/v1/attendance/session/start", json={"class_id": cls_sess.id, "duration_minutes": 30}, headers={"Authorization": f"Bearer {fac_token}"})
    assert res.status_code == 200, res.text
    session_data = res.json()
    session_token = session_data["session_token"]
    totp_secret = session_data["totp_secret"]

    current_totp = generate_totp_code(totp_secret)
    res = client.post("/api/v1/attendance/record", json={"session_token": session_token, "totp_code": current_totp, "device_fingerprint": f"device-C-{uid}"}, headers={"Authorization": f"Bearer {stud3_token}"})
    assert res.status_code == 403, res.text

    res = client.post("/api/v1/attendance/record", json={"session_token": session_token, "totp_code": current_totp, "device_fingerprint": f"device-A-{uid}"}, headers={"Authorization": f"Bearer {stud1_token}"})
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "PRESENT"

    res = client.post("/api/v1/attendance/record", json={"session_token": session_token, "totp_code": current_totp, "device_fingerprint": f"device-A-{uid}"}, headers={"Authorization": f"Bearer {stud2_token}"})
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "FLAGGED"

    res = client.get("/api/v1/attendance/anomalies", headers={"Authorization": f"Bearer {fac_token}"})
    assert res.status_code == 200
    anomalies = res.json()
    assert len(anomalies) >= 1

    print("Smart Anti-Proxy Attendance Engine API test PASSED.")

if __name__ == "__main__":
    test_attendance_api()
