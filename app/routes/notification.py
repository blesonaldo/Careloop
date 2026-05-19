from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user_id
from app.models.notification import Notification
from app.rate_limit import RateLimitedRouter

router = RateLimitedRouter(prefix="/api/notifications", tags=["notifications"], limit="30/minute")

class NotificationCreate(BaseModel):
    type: str
    title: str
    names: Optional[str] = None

class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    names: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("", response_model=list[NotificationResponse])
async def get_notifications(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    return result.scalars().all()

@router.post("", response_model=NotificationResponse)
async def create_notification(
    request: Request,
    data: NotificationCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    notif = Notification(user_id=user_id, type=data.type, title=data.title, names=data.names)
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return notif

@router.put("/mark-all-read")
async def mark_all_read(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id)
        .values(is_read=True)
    )
    await db.commit()
    return {"success": True}
