from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import secrets

from app.db.session import get_db
from app.models.all_models import (
    AttendanceSession, AttendanceRecord, AttendanceAnomaly, AttendanceStatus,
    User, UserRole, Faculty, Student, ClassSession, Enrollment
)
from app.schemas.attendance_schemas import (
    SessionStartRequest, SessionOut, AttendanceSubmitRequest, AttendanceRecordOut, AttendanceAnomalyOut
)
from app.core.rbac import require_roles, get_current_user
from app.services.attendance_security import generate_session_token, generate_totp_code, verify_totp_code
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/attendance", tags=["Smart Anti-Proxy Attendance Engine"])

@router.post("/session/start", response_model=SessionOut)
def start_attendance_session(
    req: SessionStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.HOD, UserRole.ADMIN]))
):
    faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
    if not faculty and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=400, detail="User is not registered as faculty")

    class_obj = db.query(ClassSession).filter(ClassSession.id == req.class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class session not found")

    # Deactivate existing sessions for class
    active_sessions = db.query(AttendanceSession).filter(
        AttendanceSession.class_id == req.class_id,
        AttendanceSession.is_active == True
    ).all()
    for s in active_sessions:
        s.is_active = False

    session_token = generate_session_token()
    totp_secret = secrets.token_hex(8)
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=req.duration_minutes)

    session_obj = AttendanceSession(
        class_id=req.class_id,
        faculty_id=faculty.id if faculty else 1,
        session_token=session_token,
        totp_secret=totp_secret,
        start_time=start_time,
        end_time=end_time,
        is_active=True
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)

    log_audit_event(db, "ATTENDANCE_SESSION_STARTED", f"session_{session_obj.id}", current_user.id)

    current_totp = generate_totp_code(totp_secret)
    return SessionOut(
        session_id=session_obj.id,
        class_id=session_obj.class_id,
        session_token=session_obj.session_token,
        totp_secret=session_obj.totp_secret,
        current_totp_code=current_totp,
        start_time=session_obj.start_time,
        end_time=session_obj.end_time,
        is_active=session_obj.is_active
    )

@router.post("/record", response_model=AttendanceRecordOut)
def record_attendance(
    req: AttendanceSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT]))
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student profile not found")

    session_obj = db.query(AttendanceSession).filter(
        AttendanceSession.session_token == req.session_token,
        AttendanceSession.is_active == True
    ).first()

    if not session_obj:
        raise HTTPException(status_code=400, detail="Invalid or expired attendance session")

    if datetime.utcnow() > session_obj.end_time:
        session_obj.is_active = False
        db.commit()
        raise HTTPException(status_code=400, detail="Attendance session time has expired")

    # Anti-Proxy Verification 1: TOTP Code Check
    if not verify_totp_code(session_obj.totp_secret, req.totp_code):
        raise HTTPException(status_code=400, detail="Invalid or expired dynamic TOTP code")

    # Anti-Proxy Verification 2: Duplicate Student Submission
    existing_record = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session_obj.id,
        AttendanceRecord.student_id == student.id
    ).first()
    if existing_record:
        raise HTTPException(status_code=400, detail="Attendance already recorded for this session")

    # Anti-Proxy Verification 3: Duplicate Device Fingerprint Detection (Flag Anomaly)
    duplicate_device = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session_obj.id,
        AttendanceRecord.device_fingerprint == req.device_fingerprint
    ).first()

    status_val = AttendanceStatus.PRESENT
    if duplicate_device:
        status_val = AttendanceStatus.FLAGGED

    record = AttendanceRecord(
        session_id=session_obj.id,
        student_id=student.id,
        device_fingerprint=req.device_fingerprint,
        ip_address=req.ip_address,
        status=status_val
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    if duplicate_device:
        anomaly = AttendanceAnomaly(
            record_id=record.id,
            reason=f"Duplicate device fingerprint detected ({req.device_fingerprint}) matching student ID {duplicate_device.student_id}",
            severity="HIGH"
        )
        db.add(anomaly)
        db.commit()

    log_audit_event(db, "ATTENDANCE_RECORDED", f"record_{record.id}", current_user.id, {"status": status_val.value})
    return record

@router.get("/anomalies", response_model=List[AttendanceAnomalyOut])
def list_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.FACULTY, UserRole.HOD, UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    return db.query(AttendanceAnomaly).all()
