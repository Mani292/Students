from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import PermissionRequest, PermissionStatus, User, UserRole, Student, Faculty, Notification, NotificationPriority
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
        student_roll_number=student.roll_number if student else "N/A",
        student_name=user.full_name if user else "Unknown Student",
        reason=perm.reason,
        start_date=perm.start_date,
        end_date=perm.end_date,
        proof_url=perm.proof_url,
        comments=perm.comments,
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
        status=PermissionStatus.HOD_REVIEW
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)

    # HOD reviews first; faculty receives the roll number only after approval.
    hod_users = db.query(User).filter(User.role == UserRole.HOD).all()
    for f in hod_users:
        notif = Notification(
            user_id=f.id,
            title="Permission request requires HOD review",
            message=f"Student {current_user.full_name} submitted a permission request for {req.reason}.",
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
    if current_user.role in [UserRole.FACULTY, UserRole.HOD]:
        faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
        if not faculty:
            raise HTTPException(status_code=403, detail="Staff department profile not found")
        status_filter = PermissionStatus.APPROVED if current_user.role == UserRole.FACULTY else PermissionStatus.HOD_REVIEW
        perms = db.query(PermissionRequest).join(Student).filter(
            PermissionRequest.status == status_filter,
            Student.department_id == faculty.department_id,
        ).all()
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
    student = db.query(Student).filter(Student.id == permission.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    if req.action == "APPROVE":
        if current_user.role == UserRole.FACULTY:
            raise HTTPException(status_code=403, detail="Faculty review is available after HOD approval")
        if current_user.role == UserRole.HOD and permission.status != PermissionStatus.HOD_REVIEW:
            raise HTTPException(status_code=409, detail="Only requests awaiting HOD review can be approved")
        permission.status = PermissionStatus.APPROVED
        faculty_users = db.query(Faculty).filter(Faculty.department_id == student.department_id).all()
        for faculty_user in faculty_users:
            db.add(Notification(
            user_id=faculty_user.user_id,
                title=f"Approved permission: Roll No {student.roll_number}",
                message=f"HOD approved permission for student roll number {student.roll_number}. Update attendance records as needed.",
                category="PERMISSION",
                priority=NotificationPriority.ACTION_REQUIRED,
            ))
    elif req.action == "REJECT":
        if current_user.role == UserRole.FACULTY:
            raise HTTPException(status_code=403, detail="Faculty cannot modify permission decisions")
        if current_user.role == UserRole.HOD and permission.status != PermissionStatus.HOD_REVIEW:
            raise HTTPException(status_code=409, detail="Only requests awaiting HOD review can be rejected")
        permission.status = PermissionStatus.REJECTED
    elif req.action == "FORWARD":
        raise HTTPException(status_code=400, detail="Requests are submitted directly to HOD review")

    if req.comments:
        existing_comments = permission.comments or ""
        permission.comments = f"{existing_comments}\n[{current_user.role.value}] {req.comments}".strip()

    db.commit()
    db.refresh(permission)

    log_audit_event(db, f"PERMISSION_{req.action}", f"permission_{permission.id}", current_user.id, {"new_status": permission.status.value})
    return _build_permission_out(permission, db)
