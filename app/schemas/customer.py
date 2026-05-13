from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.customer import CustomerType


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    phone_number: str = Field(..., min_length=10, max_length=20, description="WhatsApp phone number")
    email: str = Field(..., description="Customer email")
    date_of_birth: Optional[datetime] = Field(None, description="Customer date of birth")
    customer_type: CustomerType = Field(CustomerType.NEW, description="Customer type")


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Customer name")
    phone_number: Optional[str] = Field(None, min_length=10, max_length=20, description="WhatsApp phone number")
    email: Optional[str] = Field(None, description="Customer email")
    date_of_birth: Optional[datetime] = Field(None, description="Customer date of birth")
    customer_type: Optional[CustomerType] = Field(None, description="Customer type")
    has_purchased: Optional[bool] = Field(None, description="Whether customer has made a purchase")


class CustomerResponse(CustomerBase):
    id: int
    has_purchased: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    customers: List[CustomerResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
