from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog

async def log_action(
    db: AsyncSession,
    action: str,
    resource: str,
    user_id: Optional[int] = None,
    resource_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    detail: Optional[str] = None
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        ip_address=ip_address,
        detail=detail
    )
    db.add(log)
    await db.commit()
