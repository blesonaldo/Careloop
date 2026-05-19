from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.controllers.auth_controller import AuthController
from app.schemas.user import UserResponse, UserUpdate
from app.dependencies import get_current_user_id
from app.rate_limit import RateLimitedRouter

router = RateLimitedRouter(prefix="/user", tags=["user"], limit="20/minute")

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await AuthController.get_current_user(db, user_id)

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    request: Request,
    user_data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await AuthController.update_user_profile(db, user_id, user_data)

@router.put("/avatar")
async def update_user_avatar(
    request: Request,
    avatar_data: dict,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    avatar_url = avatar_data.get("avatar")
    if not avatar_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar data is required"
        )
    return await AuthController.update_user_avatar(db, user_id, avatar_url)
