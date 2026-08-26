import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import Base, engine, SessionLocal
from app.models.all_models import User, UserRole, AuditLog
from app.services.audit_service import log_audit_event

def test_audit_logging():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    user = User(
        email="auditor@univ.edu",
        hashed_password="hash",
        full_name="Audit Admin",
        role=UserRole.ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    entry = log_audit_event(
        db=db,
        action="ATTENDANCE_MODIFIED",
        resource="attendance_session_42",
        actor_id=user.id,
        details={"reason": "Manual override for medical excuse"}
    )

    assert entry.id is not None
    assert entry.action == "ATTENDANCE_MODIFIED"
    assert entry.actor_id == user.id
    assert entry.details["reason"] == "Manual override for medical excuse"

    print("Audit Logging verification PASSED.")

if __name__ == "__main__":
    test_audit_logging()
