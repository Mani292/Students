from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.rbac import require_roles
from app.db.session import get_db
from app.models.all_models import (
    AttendanceRecord,
    AttendanceStatus,
    AuditLog,
    PermissionRequest,
    ServiceRequest,
    ServiceRequestStatus,
    User,
    UserRole,
)

router = APIRouter(prefix="/admin", tags=["Administration & Analytics"])


@router.get("/overview")
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.HOD])),
) -> Dict[str, Any]:
    total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
    total_faculty = db.query(User).filter(User.role.in_([UserRole.FACULTY, UserRole.HOD])).count()
    attendance_total = db.query(AttendanceRecord).count()
    attendance_present = db.query(AttendanceRecord).filter(AttendanceRecord.status == AttendanceStatus.PRESENT).count()
    attendance_percentage = round((attendance_present / attendance_total) * 100, 1) if attendance_total else 0.0
    approved_services = db.query(ServiceRequest).filter(ServiceRequest.status == ServiceRequestStatus.APPROVED).count()
    audit_events = db.query(AuditLog).count()
    pending_permissions = db.query(PermissionRequest).filter(
        PermissionRequest.status.not_in(["APPROVED", "REJECTED"])
    ).count()

    logs: List[Dict[str, Any]] = []
    for entry in db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10).all():
        logs.append({
            "action": entry.action,
            "resource": entry.resource,
            "timestamp": entry.timestamp,
            "actor_id": entry.actor_id,
            "details": entry.details or {},
        })

    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "attendance_percentage": attendance_percentage,
        "approved_services": approved_services,
        "audit_events": audit_events,
        "pending_permissions": pending_permissions,
        "recent_audit_logs": logs,
    }

@router.get("/mongodb-status")
async def check_mongodb_status():
    from app.db.mongodb import mongo_client, mongo_db
    try:
        ping = await mongo_db.command("ping")
        cols = await mongo_db.list_collection_names()
        return {
            "status": "CONNECTED",
            "cluster": "traffic-cluster.vj7wtnf.mongodb.net",
            "database": "smart_university",
            "ping": ping,
            "collections": cols
        }
    except Exception as err:
        return {
            "status": "ERROR",
            "error": str(err)
        }
