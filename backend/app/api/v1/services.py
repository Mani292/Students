from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import ServiceRequest, ServiceRequestStatus, User, UserRole, Student
from app.schemas.service_schemas import (
    ServiceCreateRequest, ServiceProcessRequest, ServiceOut, DigitalIDOut, DigitalIDVerificationOut
)
from app.core.rbac import require_roles, get_current_user
from app.core.security import create_access_token, decode_token
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/services", tags=["Digital Service Center & Digital Student ID"])

def _build_service_out(srv: ServiceRequest, db: Session) -> ServiceOut:
    student = db.query(Student).filter(Student.id == srv.student_id).first()
    user = db.query(User).filter(User.id == student.user_id).first() if student else None

    return ServiceOut(
        id=srv.id,
        student_id=srv.student_id,
        student_name=user.full_name if user else "Unknown Student",
        roll_number=student.roll_number if student else "N/A",
        service_type=srv.service_type,
        details=srv.details or {},
        status=srv.status,
        issued_document_url=srv.issued_document_url,
        verification_token=srv.verification_token,
        created_at=srv.created_at
    )

@router.post("/request", response_model=ServiceOut)
def create_service_request(
    req: ServiceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    import secrets
    v_token = f"DOC-{secrets.token_hex(6).upper()}"
    srv = ServiceRequest(
        student_id=student.id,
        service_type=req.service_type,
        details=req.details,
        status=ServiceRequestStatus.SUBMITTED,
        verification_token=v_token
    )
    db.add(srv)
    db.commit()
    db.refresh(srv)

    log_audit_event(db, "SERVICE_REQUESTED", f"service_{srv.id}", current_user.id)
    return _build_service_out(srv, db)

@router.get("/my-requests", response_model=List[ServiceOut])
def get_my_service_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    srvs = db.query(ServiceRequest).filter(ServiceRequest.student_id == student.id).all()
    return [_build_service_out(s, db) for s in srvs]

@router.get("/all-requests", response_model=List[ServiceOut])
def get_all_service_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.HOD]))
):
    srvs = db.query(ServiceRequest).all()
    return [_build_service_out(s, db) for s in srvs]

@router.patch("/{service_id}/process", response_model=ServiceOut)
def process_service_request(
    service_id: int,
    req: ServiceProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.HOD]))
):
    srv = db.query(ServiceRequest).filter(ServiceRequest.id == service_id).first()
    if not srv:
        raise HTTPException(status_code=404, detail="Service request not found")

    srv.status = req.status
    if req.issued_document_url:
        srv.issued_document_url = req.issued_document_url
    elif req.status == ServiceRequestStatus.APPROVED and not srv.issued_document_url:
        srv.issued_document_url = f"/api/v1/services/verify-document/{srv.verification_token}"

    db.commit()
    db.refresh(srv)

    log_audit_event(db, "SERVICE_PROCESSED", f"service_{srv.id}", current_user.id, {"status": req.status.value})
    return _build_service_out(srv, db)

# Digital Student ID Endpoints
@router.get("/digital-id/me", response_model=DigitalIDOut)
def get_my_digital_id(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    dept_name = student.department.name if student.department else "Computer Science"
    verification_token = create_access_token(subject=student.id, role="DIGITAL_ID_VERIFY")
    qr_data = f"SMART_UNIV:ID:{student.roll_number}:{verification_token[:20]}"

    return DigitalIDOut(
        full_name=current_user.full_name,
        roll_number=student.roll_number,
        department_name=dept_name,
        year=student.year,
        semester=student.semester,
        email=current_user.email,
        cgpa=student.cgpa or 3.8,
        verification_token=verification_token,
        qr_data=qr_data
    )

@router.get("/digital-id/verify/{token}", response_model=DigitalIDVerificationOut)
def verify_digital_id(token: str, db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload or payload.get("role") != "DIGITAL_ID_VERIFY":
        return DigitalIDVerificationOut(
            valid=False, student_name="N/A", roll_number="N/A", department="N/A", year=0, status="INVALID_OR_EXPIRED"
        )
    student_id = int(payload.get("sub"))
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student or not student.user.is_active:
        return DigitalIDVerificationOut(
            valid=False, student_name="N/A", roll_number="N/A", department="N/A", year=0, status="STUDENT_INACTIVE"
        )

    return DigitalIDVerificationOut(
        valid=True,
        student_name=student.user.full_name,
        roll_number=student.roll_number,
        department=student.department.name if student.department else "Computer Science",
        year=student.year,
        status="ACTIVE_VERIFIED",
        issued_at=datetime.utcnow()
    )
