import os
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Keep the suite isolated from the development database and any running server.
test_db = Path(__file__).resolve().parent / "test_suite.db"
os.environ["DATABASE_URL"] = f"sqlite:///{test_db}"
try:
    test_db.unlink()
except FileNotFoundError:
    pass

import test_models
import test_security
import test_rbac
import test_audit
import test_academic
import test_attendance
import test_permissions
import test_services
import test_notifications
import test_rag
import test_ai_tools
import test_ai_api
import test_career_api

def run_all():
    print("Running suite of backend integration tests...")
    test_models.test_db_init()
    test_security.test_security()
    test_rbac.test_rbac()
    test_audit.test_audit_logging()
    test_academic.test_academic_api()
    test_attendance.test_attendance_api()
    test_permissions.test_permissions_api()
    test_services.test_services_api()
    test_notifications.test_notifications_api()
    test_rag.test_rag_engine()
    test_ai_tools.test_ai_tools()
    test_ai_api.test_ai_api()
    test_career_api.test_career_api()

    import test_campus
    test_campus.test_campus_api()
    print("ALL INTEGRATION TESTS SUCCEEDED PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_all()
