import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Remove test db if exists
if os.path.exists("smart_university.db"):
    try:
        os.remove("smart_university.db")
    except Exception:
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
