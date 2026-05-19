from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationCreate(BaseModel):
    type: str
    title: str
    names: Optional[str] = None

class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    names: Optional[str] = None
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
