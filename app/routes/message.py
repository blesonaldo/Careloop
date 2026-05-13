from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.routes.auth import get_current_user_id
from app.services.openai_service import openai_service

router = APIRouter(prefix="/api/messages", tags=["messages"])

class MessageRequest(BaseModel):
    customer_id: int
    message_type: str = "follow_up"  # follow_up, sales, etc.
    product: Optional[str] = None  # For sales messages

class MessageResponse(BaseModel):
    message: str
    success: bool

@router.post("/generate", response_model=MessageResponse)
async def generate_message(
    request: MessageRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Generate an AI-powered message for a customer"""
    try:
        # Get customer details
        from app.controllers.customer_controller import CustomerController
        customer = await CustomerController.get_customer_by_id(db, request.customer_id, user_id)
        
        # Convert customer to dict for OpenAI service
        customer_dict = {
            'id': customer.id,
            'name': customer.name,
            'phone_number': customer.phone_number,
            'email': customer.email,
            'customer_type': customer.customer_type,
            'has_purchased': customer.has_purchased,
            'created_at': customer.created_at
        }
        
        # Get user details
        from app.controllers.auth_controller import AuthController
        user = await AuthController._get_user_by_id(db, user_id)
        user_name = user.full_name or user.email.split('@')[0]
        user_business = user.business_name or "Your Business"
        
        # Generate message based on type
        if request.message_type == "sales" and request.product:
            message = await openai_service.generate_sales_message(
                customer=customer_dict,
                product=request.product,
                user_name=user_name,
                user_business=user_business
            )
        else:
            message = await openai_service.generate_follow_up_message(
                customer=customer_dict,
                user_name=user_name,
                user_business=user_business
            )
        
        return MessageResponse(
            message=message,
            success=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate message: {str(e)}"
        )
