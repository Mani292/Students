import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.session import Base, engine, SessionLocal
from app.models.all_models import User, UserRole, Department, Student, Faculty, PermissionStatus
from app.core.security import get_password_hash, create_access_token
from app.api.v1.permissions import router as permissions_router

app = FastAPI()
app.include_router(permissions_router, prefix="/api/v1")

def test_permissions_api():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    dept = db.query(Department).filter(Department.code == "MECH_PERM").first()
    if not dept:
        dept = Department(code="MECH_PERM", name="Mechanical Eng Perm")
        db.add(dept)
        db.commit()

    stud_user = db.query(User).filter(User.email == "mech_student_perm@univ.edu").first()
    if not stud_user:
        stud_user = User(email="mech_student_perm@univ.edu", hashed_password=get_password_hash("p"), full_name="Bob Mechanic", role=UserRole.STUDENT)
        db.add(stud_user)
        db.commit()

    fac_user = db.query(User).filter(User.email == "mech_faculty_perm@univ.edu").first()
    if not fac_user:
        fac_user = User(email="mech_faculty_perm@univ.edu", hashed_password=get_password_hash("p"), full_name="Dr. Mech", role=UserRole.FACULTY)
        db.add(fac_user)
        db.commit()

    hod_user = db.query(User).filter(User.email == "mech_hod_perm@univ.edu").first()
    if not hod_user:
        hod_user = User(email="mech_hod_perm@univ.edu", hashed_password=get_password_hash("p"), full_name="HOD Mech", role=UserRole.HOD)
        db.add(hod_user)
        db.commit()

    student = db.query(Student).filter(Student.user_id == stud_user.id).first()
    if not student:
        student = Student(user_id=stud_user.id, roll_number="MECHPERM001", department_id=dept.id)
        db.add(student)
        db.commit()

    faculty = db.query(Faculty).filter(Faculty.user_id == fac_user.id).first()
    if not faculty:
        faculty = Faculty(user_id=fac_user.id, employee_id="EMPMECHPERM1", department_id=dept.id, designation="Assoc Prof")
        db.add(faculty)
        db.commit()

    client = TestClient(app)

    stud_token = create_access_token(subject=stud_user.id, role="STUDENT")
    fac_token = create_access_token(subject=fac_user.id, role="FACULTY")
    hod_token = create_access_token(subject=hod_user.id, role="HOD")

    # 1. Student applies for leave
    now = datetime.utcnow()
    res = client.post(
        "/api/v1/permissions/apply",
        json={"reason": "Medical leave for fever", "start_date": now.isoformat(), "end_date": (now + timedelta(days=2)).isoformat()},
        headers={"Authorization": f"Bearer {stud_token}"}
    )
    assert res.status_code == 200, res.text
    perm_id = res.json()["id"]
    assert res.json()["status"] == "PENDING"
    assert res.json()["student_roll_number"] == "MECHPERM001"
    assert res.json()["student_name"] == "Bob Mechanic"

    # 2. Faculty reviews and approves (escalating to HOD_REVIEW)
    res = client.post(
        f"/api/v1/permissions/{perm_id}/action",
        json={"action": "APPROVE", "comments": "Medical certificate verified"},
        headers={"Authorization": f"Bearer {fac_token}"}
    )
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "HOD_REVIEW"

    # 3. HOD approves final request
    res = client.post(
        f"/api/v1/permissions/{perm_id}/action",
        json={"action": "APPROVE", "comments": "Final approval granted"},
        headers={"Authorization": f"Bearer {hod_token}"}
    )
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "APPROVED"

    print("Multi-Tier Permission & Leave Management Workflow API test PASSED.")

if __name__ == "__main__":
    test_permissions_api()
