import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.db.session import engine, Base
from app.models.all_models import User, Department, Student, Faculty, Course, ClassSession, Enrollment, AttendanceSession, AttendanceRecord, AttendanceAnomaly, PermissionRequest, ServiceRequest, Notification, KnowledgeDocument, AuditLog

def test_db_init():
    print("Testing database table creation...")
    Base.metadata.create_all(bind=engine)
    tables = Base.metadata.tables.keys()
    print(f"Created {len(tables)} tables: {list(tables)}")
    assert len(tables) >= 15, "Expected at least 15 tables created."
    print("Database models verification PASSED.")

if __name__ == "__main__":
    test_db_init()
