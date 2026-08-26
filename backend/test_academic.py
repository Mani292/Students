import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.session import Base, engine, SessionLocal
from app.models.all_models import User, UserRole, Department, Course
from app.core.security import get_password_hash, create_access_token
from app.api.v1.academic import router as academic_router

app = FastAPI()
app.include_router(academic_router, prefix="/api/v1")

def test_academic_api():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed admin user
    db.query(User).filter(User.email == "admin@univ.edu").delete()
    db.commit()

    admin_user = User(
        email="admin@univ.edu",
        hashed_password=get_password_hash("admin123"),
        full_name="System Admin",
        role=UserRole.ADMIN
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    admin_token = create_access_token(subject=admin_user.id, role="ADMIN")
    client = TestClient(app)

    # 1. Create Department
    res = client.post(
        "/api/v1/academic/departments",
        json={"code": "CSE", "name": "Computer Science & Engineering"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200, res.text
    dept_id = res.json()["id"]

    # 2. List Departments
    res = client.get("/api/v1/academic/departments")
    assert res.status_code == 200
    assert len(res.json()) >= 1

    # 3. Create Course
    res = client.post(
        "/api/v1/academic/courses",
        json={"code": "CS101", "title": "Database Management Systems", "department_id": dept_id, "credits": 4},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200, res.text
    assert res.json()["code"] == "CS101"

    print("Academic & Roster Management API test PASSED.")

if __name__ == "__main__":
    test_academic_api()
