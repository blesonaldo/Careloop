from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import (
    UserCreate, UserCreateResponse, UserLogin, Token, UserResponse,
    UserUpdate,  # <-- added for profile update
    EmailVerificationRequest, EmailVerificationResponse,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse,
    ChangePasswordRequest, ChangePasswordResponse,
    SetInitialPasswordRequest
)
from app.services.auth_service import TokenService, PasswordService, TokenGeneratorService
from app.services.email_service import email_service


class AuthController:
    """Controller for authentication operations."""
    
    @staticmethod
    async def create_user(
        db: AsyncSession, 
        user_data: UserCreate
    ) -> UserCreateResponse:
        """Create a new user account."""
        
        try:
            # Check if user already exists
            existing_user = await AuthController._get_user_by_email(db, user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
            # Handle password (optional for initial signup)
            hashed_password = None
            if user_data.password:
                # Validate password strength
                if not PasswordService.validate_password_strength(user_data.password):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Password must be at least 8 characters long"
                    )
                # Hash password
                hashed_password = PasswordService.hash_password(user_data.password)
            
            # Create user
            db_user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                business_name=user_data.business_name,
                phone=user_data.phone,
                hashed_password=hashed_password,
                is_email_verified=False,
                is_active=True
            )
            
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            
            # Generate verification token
            verification_token = TokenGeneratorService.generate_verification_token()
            verification_expires = datetime.utcnow() + timedelta(hours=24)
            
            # Update user with verification token
            db_user.email_verification_token = verification_token
            db_user.email_verification_expires_at = verification_expires
            await db.commit()
            
            # Send verification email
            try:
                await email_service.send_verification_email(user_data.email, verification_token)
            except Exception as e:
                # Log email error but don't fail registration
                print(f"Failed to send verification email: {e}")
                print(f"Verification token for manual testing: {verification_token}")
            
            return UserCreateResponse(
                message="User created successfully. Please check your email for verification.",
                user=UserResponse(
                    id=db_user.id,
                    email=db_user.email,
                    full_name=db_user.full_name,
                    business_name=db_user.business_name,
                    phone=db_user.phone,
                    is_active=db_user.is_active,
                    created_at=db_user.created_at
                ),
                verification_token=verification_token
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Database error in create_user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        login_data: UserLogin
    ) -> Token:
        """Authenticate user and return access token."""
        
        user = await AuthController._get_user_by_email(db, login_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not user.is_email_verified:
            raise HTTPException(status_code=401, detail="Email not verified")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account deactivated")
        
        if not PasswordService.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        
        user.last_login_at = datetime.utcnow()
        
        
        await db.commit()
        
        await db.refresh(user)
        
        access_token_expires = timedelta(minutes=60)
        access_token = TokenService.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                business_name=user.business_name,
                phone=user.phone,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,      # ✅ Now safe
                last_login_at=user.last_login_at # ✅ Now safe
            )
        )
    
    @staticmethod
    async def verify_email(
        db: AsyncSession, 
        token: str
    ) -> dict:
        """Verify user email (but keep token for password creation)."""
        
        result = await db.execute(
            select(User).where(User.email_verification_token == token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        if user.email_verification_expires_at and user.email_verification_expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired"
            )
        
        # Mark email as verified but DO NOT clear the token yet
        # (we need it for password creation)
        user.is_email_verified = True
        await db.commit()
        
        return {"message": "Email verified successfully"}
    
    @staticmethod
    async def forgot_password(
        db: AsyncSession, 
        request: ForgotPasswordRequest
    ) -> ForgotPasswordResponse:
        """Send password reset email."""
        
        user = await AuthController._get_user_by_email(db, request.email)
        if not user:
            return ForgotPasswordResponse(
                message="If an account with this email exists, a password reset link has been sent."
            )
        
        reset_token = TokenGeneratorService.generate_password_reset_token()
        reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        user.password_reset_token = reset_token
        user.password_reset_expires_at = reset_expires
        await db.commit()
        
        reset_link = f"http://localhost:8001/reset-password?token={reset_token}"
        await email_service.send_password_reset_email(
            user.email,
            reset_token,
            reset_link
        )
        
        return ForgotPasswordResponse(
            message="If an account with this email exists, a password reset link has been sent."
        )
    
    @staticmethod
    async def reset_password(
        db: AsyncSession, 
        request: ResetPasswordRequest
    ) -> ResetPasswordResponse:
        """Reset user password (forgot password flow)."""
        
        result = await db.execute(
            select(User).where(User.password_reset_token == request.token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        if user.password_reset_expires_at and user.password_reset_expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        
        if not PasswordService.validate_password_strength(request.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        user.hashed_password = PasswordService.hash_password(request.new_password)
        user.password_reset_token = None
        user.password_reset_expires_at = None
        await db.commit()
        
        return ResetPasswordResponse(message="Password reset successfully")
    
    @staticmethod
    async def change_password(
        db: AsyncSession, 
        user_id: int, 
        request: ChangePasswordRequest
    ) -> ChangePasswordResponse:
        """Change user password."""
        
        user = await AuthController._get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not PasswordService.verify_password(request.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        if not PasswordService.validate_password_strength(request.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        user.hashed_password = PasswordService.hash_password(request.new_password)
        await db.commit()
        
        return ChangePasswordResponse(message="Password changed successfully")
    
    @staticmethod
    async def set_initial_password(
        db: AsyncSession,
        token: str,
        password: str
    ) -> dict:
        """Set password for a user who signed up without one, using the email verification token."""
        
        result = await db.execute(
            select(User).where(User.email_verification_token == token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        if user.email_verification_expires_at and user.email_verification_expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired"
            )
        
        if not PasswordService.validate_password_strength(password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain upper/lowercase and a number"
            )
        
        user.hashed_password = PasswordService.hash_password(password)
        # Ensure email is verified (in case it wasn't already)
        user.is_email_verified = True
        # Clear the verification token now that password is set
        user.email_verification_token = None
        user.email_verification_expires_at = None
        await db.commit()
        
        return {"message": "Password created successfully. You can now log in."}
    
    @staticmethod
    async def get_current_user(
        db: AsyncSession, 
        user_id: int
    ) -> UserResponse:
        """Get current user information."""
        
        user = await AuthController._get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            business_name=user.business_name,
            phone=user.phone,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at    # requires column in model
        )
    
    # ========== NEW METHODS FOR PROFILE MANAGEMENT ==========
    
    @staticmethod
    async def update_user_profile(
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate
    ) -> UserResponse:
        """Update user profile information (full_name, business_name, phone, is_active)."""
        user = await AuthController._get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update only fields that are provided (not None)
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.business_name is not None:
            user.business_name = user_data.business_name
        if user_data.phone is not None:
            user.phone = user_data.phone
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            business_name=user.business_name,
            phone=user.phone,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )
    
    @staticmethod
    async def update_user_avatar(
        db: AsyncSession,
        user_id: int,
        avatar_url: str
    ) -> dict:
        """Update user avatar (store base64 or URL)."""
        user = await AuthController._get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Ensure your User model has an 'avatar' column (String or Text)
        user.avatar = avatar_url
        user.updated_at = datetime.utcnow()
        await db.commit()
        
        return {"message": "Avatar updated successfully", "avatar": avatar_url}
    
    # ========== HELPER METHODS ==========
    
    @staticmethod
    async def _get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def _get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()