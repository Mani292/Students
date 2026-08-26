import os
import sys
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.models.all_models import User, UserRole

client = TestClient(app)

def test_admin_intelligence():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == "admin_analytics@univ.edu").first()
        if not admin_user:
            admin_user = User(
                email="admin_analytics@univ.edu",
                hashed_password="hash",
                full_name="System SuperAdmin",
                role=UserRole.SUPER_ADMIN
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        token = create_access_token(subject=admin_user.id, role=admin_user.role.value)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Test Admin Metrics
        m_res = client.get("/api/v1/admin/metrics", headers=headers)
        assert m_res.status_code == 200
        metrics = m_res.json()
        assert "avg_attendance_percentage" in metrics
        assert "total_audit_events" in metrics

        # 2. Test Department Attendance Breakdown
        d_res = client.get("/api/v1/admin/department-attendance", headers=headers)
        assert d_res.status_code == 200
        assert len(d_res.json()) >= 1

        # 3. Test Audit Stream
        a_res = client.get("/api/v1/admin/audit-stream", headers=headers)
        assert a_res.status_code == 200

        print("Admin Intelligence & Analytics tests PASSED.")
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_intelligence()