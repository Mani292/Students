from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.all_models import Notification, NotificationPriority, User, UserRole
from app.schemas.notification_schemas import NotificationCreate, NotificationOut
from app.core.rbac import require_roles, get_current_user

router = APIRouter(prefix="/notifications", tags=["Smart In-App Notification Service"])

@router.post("/", response_model=NotificationOut)
def send_notification(
    notif_in: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.FACULTY, UserRole.HOD]))
):
    notif = Notification(
        user_id=notif_in.user_id,
        title=notif_in.title,
        message=notif_in.message,
        category=notif_in.category,
        priority=notif_in.priority
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

@router.get("/me", response_model=List[NotificationOut])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()

@router.patch("/{notif_id}/read", response_model=NotificationOut)
def mark_notification_as_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == current_user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif
