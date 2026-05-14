from .customer import Customer
from .base import Base

# Try to import User if it exists, otherwise create a placeholder
try:
    from .user import User
except ImportError:
    # Create a basic User model if it doesn't exist
    from sqlalchemy import Column, Integer, String, DateTime, Boolean
    from sqlalchemy.sql import func
    from .base import Base
    
    class User(Base):
        __tablename__ = "users"
        
        id = Column(Integer, primary_key=True, index=True)
        email = Column(String, unique=True, index=True, nullable=False)
        full_name = Column(String, nullable=False)
        business_name = Column(String, nullable=True)
        phone = Column(String, nullable=True)
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())

__all__ = ["Customer", "User", "Base", "Notification"]
