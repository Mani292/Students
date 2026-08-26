from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.all_models import AuditLog, User

def log_audit_event(
    db: Session,
    action: str,
    resource: str,
    actor_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Creates an immutable record of sensitive user or system actions.
    """
    audit_entry = AuditLog(
        actor_id=actor_id,
        action=action,
        resource=resource,
        details=details or {}
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry
