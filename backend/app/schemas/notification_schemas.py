from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.all_models import NotificationPriority

class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    category: Optional[str] = "SYSTEM"
    priority: Optional[NotificationPriority] = NotificationPriority.INFORMATIONAL

class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    category: str
    priority: NotificationPriority
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
