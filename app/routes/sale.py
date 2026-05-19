from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user_id
from app.controllers.sale_controller import SaleController
from app.controllers.auth_controller import AuthController
from app.schemas.sale import SaleCreate, SaleListResponse, SaleResponse, UserPreferencesUpdate
from app.rate_limit import RateLimitedRouter

router = RateLimitedRouter(prefix="/api/sales", tags=["sales"], limit="30/minute", redirect_slashes=False)

@router.post("", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
async def create_sale(
    request: Request,
    data: SaleCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await SaleController.create_sale(db, user_id, data)

@router.get("", response_model=SaleListResponse)
async def get_sales(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await SaleController.get_sales(db, user_id)

@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(
    request: Request,
    sale_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    await SaleController.delete_sale(db, sale_id, user_id)

@router.put("/preferences")
async def update_preferences(
    request: Request,
    data: UserPreferencesUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    user = await AuthController._get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if data.preferred_currency:
        user.preferred_currency = data.preferred_currency
    await db.commit()
    return {"message": "Preferences updated", "preferred_currency": user.preferred_currency}
