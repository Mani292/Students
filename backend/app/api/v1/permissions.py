from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import PermissionRequest, PermissionStatus, User, UserRole, Student
from app.schemas.permission_schemas import PermissionApplyRequest, PermissionActionRequest, PermissionOut
from app.core.rbac import require_roles, get_current_user
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/permissions", tags=["Multi-Tier Permission & Leave Management Workflow"])

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

    log_audit_event(db, "PERMISSION_APPLIED", f"permission_{permission.id}", current_user.id)
    return permission

@router.get("/my-requests", response_model=List[PermissionOut])
def get_my_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    return db.query(PermissionRequest).filter(PermissionRequest.student_id == student.id).all()

@router.get("/pending", response_model=List[PermissionOut])
def get_pending_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.HOD, UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    if current_user.role == UserRole.FACULTY:
        return db.query(PermissionRequest).filter(PermissionRequest.status.in_([PermissionStatus.PENDING, PermissionStatus.FACULTY_REVIEW])).all()
    elif current_user.role == UserRole.HOD:
        return db.query(PermissionRequest).filter(PermissionRequest.status.in_([PermissionStatus.FACULTY_REVIEW, PermissionStatus.HOD_REVIEW])).all()
    else:
        return db.query(PermissionRequest).filter(PermissionRequest.status != PermissionStatus.APPROVED).all()

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
    return permission
