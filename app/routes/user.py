from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.controllers.auth_controller import AuthController
from app.schemas.user import UserResponse, UserUpdate
from app.routes.auth import get_current_user_id

router = APIRouter(prefix="/user", tags=["user"])
security = HTTPBearer()


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get current user profile information."""
    user_id = await get_current_user_id(credentials, db)
    return await AuthController.get_current_user(db, user_id)


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update current user profile information."""
    user_id = await get_current_user_id(credentials, db)
    return await AuthController.update_user_profile(db, user_id, user_data)


@router.put("/avatar")
async def update_user_avatar(
    avatar_data: dict,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update user avatar image."""
    user_id = await get_current_user_id(credentials, db)
    
    # Extract avatar base64 data
    avatar_url = avatar_data.get("avatar")
    if not avatar_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar data is required"
        )
    
    return await AuthController.update_user_avatar(db, user_id, avatar_url)
