from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user_id
from app.services.openai_service import openai_service
from app.rate_limit import RateLimitedRouter

router = RateLimitedRouter(prefix="/api/messages", tags=["messages"], limit="30/minute")

class MessageRequest(BaseModel):
    customer_id: int
    message_type: str = "follow_up"
    product: Optional[str] = None

class MessageResponse(BaseModel):
    message: str
    success: bool

@router.post("/generate", response_model=MessageResponse)
async def generate_message(
    request: Request,
    body: MessageRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        from app.controllers.customer_controller import CustomerController
        customer = await CustomerController.get_customer_by_id(db, body.customer_id, user_id)

        customer_dict = {
            'id': customer.id,
            'name': customer.name,
            'phone_number': customer.phone_number,
            'email': customer.email,
            'customer_type': customer.customer_type,
            'has_purchased': customer.has_purchased,
            'created_at': customer.created_at
        }

        from app.controllers.auth_controller import AuthController
        user = await AuthController._get_user_by_id(db, user_id)
        user_name = user.full_name or user.email.split("@")[0]
        user_business = user.business_name or "Your Business"

        if body.message_type == "sales" and body.product:
            message = await openai_service.generate_sales_message(
                customer=customer_dict, product=body.product,
                user_name=user_name, user_business=user_business
            )
        else:
            message = await openai_service.generate_follow_up_message(
                customer=customer_dict, user_name=user_name, user_business=user_business
            )

        return MessageResponse(message=message, success=True)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate message: {str(e)}")
