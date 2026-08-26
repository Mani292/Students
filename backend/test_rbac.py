import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import Base, engine, SessionLocal
from app.models.all_models import User, UserRole
from app.core.security import get_password_hash, create_access_token
from app.core.rbac import get_current_user, require_roles

app = FastAPI()

@app.get("/api/v1/student-only")
def student_only_route(current_user: User = Depends(require_roles([UserRole.STUDENT]))):
    return {"message": f"Hello Student {current_user.full_name}"}

@app.get("/api/v1/faculty-admin-only")
def faculty_admin_route(current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.ADMIN, UserRole.SUPER_ADMIN]))):
    return {"message": f"Hello Staff {current_user.full_name}"}

def test_rbac():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed users
    db.query(User).delete()
    db.commit()

    student_user = User(
        email="student@univ.edu",
        hashed_password=get_password_hash("pass123"),
        full_name="John Student",
        role=UserRole.STUDENT
    )
    faculty_user = User(
        email="faculty@univ.edu",
        hashed_password=get_password_hash("pass123"),
        full_name="Dr. Smith",
        role=UserRole.FACULTY
    )
    db.add_all([student_user, faculty_user])
    db.commit()
    db.refresh(student_user)
    db.refresh(faculty_user)

    client = TestClient(app)

    student_token = create_access_token(subject=student_user.id, role="STUDENT")
    faculty_token = create_access_token(subject=faculty_user.id, role="FACULTY")

    # Student accessing student route -> 200
    res = client.get("/api/v1/student-only", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200, res.text
    print("Student allowed on student route: PASSED")

    # Student accessing faculty route -> 403
    res = client.get("/api/v1/faculty-admin-only", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 403, res.text
    print("Student blocked on faculty route: PASSED")

    # Faculty accessing faculty route -> 200
    res = client.get("/api/v1/faculty-admin-only", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200, res.text
    print("Faculty allowed on faculty route: PASSED")

if __name__ == "__main__":
    test_rbac()
