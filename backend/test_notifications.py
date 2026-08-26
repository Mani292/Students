import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.session import Base, engine, SessionLocal
from app.models.all_models import User, UserRole, Notification
from app.core.security import get_password_hash, create_access_token
from app.api.v1.notifications import router as notifications_router

app = FastAPI()
app.include_router(notifications_router, prefix="/api/v1")

def test_notifications_api():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    user1 = User(email="n_user1@univ.edu", hashed_password=get_password_hash("p"), full_name="User One", role=UserRole.STUDENT)
    admin = User(email="n_admin@univ.edu", hashed_password=get_password_hash("p"), full_name="Admin", role=UserRole.ADMIN)
    db.add_all([user1, admin])
    db.commit()

    client = TestClient(app)

    u1_token = create_access_token(subject=user1.id, role="STUDENT")
    admin_token = create_access_token(subject=admin.id, role="ADMIN")

    # 1. Admin sends notification to user1
    res = client.post(
        "/api/v1/notifications/",
        json={"user_id": user1.id, "title": "Attendance Shortage Alert", "message": "Your attendance in CS101 is below 75%", "priority": "CRITICAL", "category": "ATTENDANCE"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200, res.text
    n_id = res.json()["id"]

    # 2. User1 reads notifications
    res = client.get("/api/v1/notifications/me", headers={"Authorization": f"Bearer {u1_token}"})
    assert res.status_code == 200, res.text
    notifs = res.json()
    assert len(notifs) >= 1
    assert notifs[0]["is_read"] is False

    # 3. Mark as read
    res = client.patch(f"/api/v1/notifications/{n_id}/read", headers={"Authorization": f"Bearer {u1_token}"})
    assert res.status_code == 200
    assert res.json()["is_read"] is True

    print("Smart In-App Notification Service API test PASSED.")

if __name__ == "__main__":
    test_notifications_api()
