from fastapi.testclient import TestClient
import uuid
from app.main import app
from app.core.security import get_password_hash
from app.models.all_models import User, UserRole
from app.db.session import SessionLocal

client = TestClient(app)

def test_auth_login_and_refresh():
    db = SessionLocal()
    email = "auth_test_user@univ.edu"
    existing = db.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            email=email,
            hashed_password=get_password_hash("password123"),
            full_name="Auth Test Student",
            role=UserRole.STUDENT,
            is_active=True
        )
        db.add(user)
        db.commit()

    # Test login
    res = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "STUDENT"

    # Test refresh
    refresh_token = data["refresh_token"]
    res_refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res_refresh.status_code == 200
    refreshed_data = res_refresh.json()
    assert "access_token" in refreshed_data

    # Test bad login
    res_bad = client.post("/api/v1/auth/login", json={"email": email, "password": "wrongpassword"})
    assert res_bad.status_code == 401

    registration_email = f"new_student_{uuid.uuid4().hex[:8]}@univ.edu"
    registration = client.post("/api/v1/auth/register", json={
        "email": registration_email,
        "password": "securepass123",
        "full_name": "New Student",
        "roll_number": f"NEW{uuid.uuid4().hex[:8]}",
        "department_code": "CSE",
    })
    assert registration.status_code == 201, registration.text
    assert registration.json()["role"] == "STUDENT"

    duplicate = client.post("/api/v1/auth/register", json={
        "email": registration_email,
        "password": "securepass123",
        "full_name": "Another Student",
        "roll_number": f"OTHER{uuid.uuid4().hex[:8]}",
        "department_code": "CSE",
    })
    assert duplicate.status_code == 409

if __name__ == "__main__":
    test_auth_login_and_refresh()
    print("Auth router test PASSED!")
