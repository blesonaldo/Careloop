from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleListResponse, SaleResponse

class SaleController:

    @staticmethod
    async def create_sale(db: AsyncSession, user_id: int, data: SaleCreate) -> SaleResponse:
        sale = Sale(
            user_id=user_id,
            customer_id=data.customer_id,
            amount=data.amount,
            currency=data.currency,
            product=data.product,
            date=data.date or datetime.utcnow()
        )
        db.add(sale)
        await db.commit()
        await db.refresh(sale)
        return SaleResponse.model_validate(sale)

    @staticmethod
    async def get_sales(db: AsyncSession, user_id: int) -> SaleListResponse:
        result = await db.execute(
            select(Sale)
            .where(Sale.user_id == user_id)
            .order_by(Sale.date.desc())
        )
        sales = result.scalars().all()
        total = await db.execute(
            select(func.count()).where(Sale.user_id == user_id)
        )
        return SaleListResponse(items=sales, total=total.scalar())

    @staticmethod
    async def delete_sale(db: AsyncSession, sale_id: int, user_id: int) -> None:
        result = await db.execute(
            select(Sale).where(Sale.id == sale_id, Sale.user_id == user_id)
        )
        sale = result.scalar_one_or_none()
        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
        await db.delete(sale)
        await db.commit()
