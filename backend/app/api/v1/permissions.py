from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import PermissionRequest, PermissionStatus, User, UserRole, Student, Notification, NotificationPriority
from app.schemas.permission_schemas import PermissionApplyRequest, PermissionActionRequest, PermissionOut
from app.core.rbac import require_roles, get_current_user
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/permissions", tags=["Multi-Tier Permission & Leave Management Workflow"])

def _build_permission_out(perm: PermissionRequest, db: Session) -> PermissionOut:
    student = db.query(Student).filter(Student.id == perm.student_id).first()
    user = db.query(User).filter(User.id == student.user_id).first() if student else None

    return PermissionOut(
        id=perm.id,
        student_id=perm.student_id,
        roll_number=student.roll_number if student else "N/A",
        student_name=user.full_name if user else "Unknown Student",
        reason=perm.reason,
        start_date=perm.start_date,
        end_date=perm.end_date,
        proof_url=perm.proof_url,
        comments=perm.comments,
        faculty_comment=perm.faculty_comment,
        hod_comment=perm.hod_comment,
        status=perm.status,
        created_at=perm.created_at
    )

@router.post("/apply", response_model=PermissionOut)
def apply_permission(
    req: PermissionApplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    permission = PermissionRequest(
        student_id=student.id,
        reason=req.reason,
        start_date=req.start_date,
        end_date=req.end_date,
        proof_url=req.proof_url,
        status=PermissionStatus.PENDING
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)

    # Notify faculty members with Roll Number for attendance marking
    faculty_users = db.query(User).filter(User.role.in_([UserRole.FACULTY, UserRole.HOD])).all()
    for f in faculty_users:
        notif = Notification(
            user_id=f.id,
            title=f"Leave Request: Roll No {student.roll_number}",
            message=f"Student {current_user.full_name} (Roll No: {student.roll_number}) submitted leave request for {req.reason}. Update attendance roll records accordingly.",
            category="PERMISSION",
            priority=NotificationPriority.ACTION_REQUIRED
        )
        db.add(notif)
    db.commit()

    log_audit_event(db, "PERMISSION_APPLIED", f"permission_{permission.id}", current_user.id)
    return _build_permission_out(permission, db)

@router.get("/my-requests", response_model=List[PermissionOut])
def get_my_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    perms = db.query(PermissionRequest).filter(PermissionRequest.student_id == student.id).all()
    return [_build_permission_out(p, db) for p in perms]

@router.get("/pending", response_model=List[PermissionOut])
def get_pending_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.HOD, UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    if current_user.role == UserRole.FACULTY:
        perms = db.query(PermissionRequest).filter(PermissionRequest.status.in_([PermissionStatus.PENDING, PermissionStatus.FACULTY_REVIEW])).all()
    elif current_user.role == UserRole.HOD:
        perms = db.query(PermissionRequest).filter(PermissionRequest.status.in_([PermissionStatus.FACULTY_REVIEW, PermissionStatus.HOD_REVIEW])).all()
    else:
        perms = db.query(PermissionRequest).filter(PermissionRequest.status != PermissionStatus.APPROVED).all()
    return [_build_permission_out(p, db) for p in perms]

@router.post("/{permission_id}/action", response_model=PermissionOut)
def update_permission_status(
    permission_id: int,
    req: PermissionActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.HOD, UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    permission = db.query(PermissionRequest).filter(PermissionRequest.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission request not found")

    if req.action == "APPROVE":
        if current_user.role == UserRole.FACULTY:
            # Multi-tier escalation: Faculty -> HOD Review
            permission.status = PermissionStatus.HOD_REVIEW
        else:
            permission.status = PermissionStatus.APPROVED
    elif req.action == "REJECT":
        permission.status = PermissionStatus.REJECTED
    elif req.action == "FORWARD":
        permission.status = PermissionStatus.HOD_REVIEW

    if req.comments:
        existing_comments = permission.comments or ""
        permission.comments = f"{existing_comments}\n[{current_user.role.value}] {req.comments}".strip()

    db.commit()
    db.refresh(permission)

    log_audit_event(db, f"PERMISSION_{req.action}", f"permission_{permission.id}", current_user.id, {"new_status": permission.status.value})
    return _build_permission_out(permission, db)
