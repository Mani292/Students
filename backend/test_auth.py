from fastapi.testclient import TestClient
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

if __name__ == "__main__":
    test_auth_login_and_refresh()
    print("Auth router test PASSED!")
