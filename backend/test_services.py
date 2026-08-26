import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.session import Base, engine, SessionLocal
from app.models.all_models import User, UserRole, Department, Student
from app.core.security import get_password_hash, create_access_token
from app.api.v1.services import router as services_router

app = FastAPI()
app.include_router(services_router, prefix="/api/v1")

def test_services_api():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    dept = Department(code="IT", name="Information Tech")
    db.add(dept)
    db.commit()

    stud_user = User(email="it_stud@univ.edu", hashed_password=get_password_hash("p"), full_name="Charlie Tech", role=UserRole.STUDENT)
    admin_user = User(email="admin_srv@univ.edu", hashed_password=get_password_hash("p"), full_name="Admin Srv", role=UserRole.ADMIN)
    db.add_all([stud_user, admin_user])
    db.commit()

    student = Student(user_id=stud_user.id, roll_number="IT001", department_id=dept.id, year=2, semester=3)
    db.add(student)
    db.commit()

    client = TestClient(app)

    stud_token = create_access_token(subject=stud_user.id, role="STUDENT")
    admin_token = create_access_token(subject=admin_user.id, role="ADMIN")

    # 1. Student submits Bonafide service request
    res = client.post(
        "/api/v1/services/request",
        json={"service_type": "BONAFIDE", "details": {"purpose": "Passport application"}},
        headers={"Authorization": f"Bearer {stud_token}"}
    )
    assert res.status_code == 200, res.text
    srv_id = res.json()["id"]
    assert res.json()["status"] == "SUBMITTED"

    # 2. Admin processes request -> APPROVED with document URL
    res = client.patch(
        f"/api/v1/services/{srv_id}/process",
        json={"status": "APPROVED", "issued_document_url": "/docs/bonafide_IT001.pdf"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "APPROVED"
    assert res.json()["issued_document_url"] == "/docs/bonafide_IT001.pdf"

    # 3. Digital ID generation
    res = client.get("/api/v1/services/digital-id/me", headers={"Authorization": f"Bearer {stud_token}"})
    assert res.status_code == 200, res.text
    dig_id = res.json()
    assert dig_id["roll_number"] == "IT001"
    v_token = dig_id["verification_token"]

    # 4. Public QR token verification endpoint
    res = client.get(f"/api/v1/services/digital-id/verify/{v_token}")
    assert res.status_code == 200, res.text
    v_data = res.json()
    assert v_data["valid"] is True
    assert v_data["student_name"] == "Charlie Tech"

    print("Digital Service Center & Digital Student ID API test PASSED.")

if __name__ == "__main__":
    test_services_api()
