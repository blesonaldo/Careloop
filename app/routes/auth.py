from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.controllers.auth_controller import AuthController
from app.schemas.user import (
    UserCreate, UserCreateResponse, UserLogin, Token, UserResponse,
    EmailVerificationRequest, EmailVerificationResponse,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse,
    ChangePasswordRequest, ChangePasswordResponse,
    SetInitialPasswordRequest
)
from app.services.auth_service import TokenService

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> int:
    """Extract user_id from the JWT token. This is a proper FastAPI dependency."""
    token_data = TokenService.get_token_data(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = token_data.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await AuthController._get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


@router.post("/signup", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await AuthController.create_user(db, user_data)


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    result = await AuthController.authenticate_user(db, login_data)
    print(f"Login response: {result}")
    return result


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    await AuthController.verify_email(db, token)

    try:
        with open("Frontend/email-verified.html", "r", encoding="utf-8") as f:
            html = f.read()
            html = html.replace('href="/create-password"', f'href="/create-password?token={token}"')
            return HTMLResponse(content=html)
    except FileNotFoundError:
        return HTMLResponse(
            content=f"<h1>Email verified successfully!</h1><p><a href='/create-password?token={token}'>Create Password</a></p>",
            status_code=200
        )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await AuthController.forgot_password(db, request)


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await AuthController.reset_password(db, request)


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await AuthController.change_password(db, user_id, request)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    return await AuthController.get_current_user(db, user_id)


@router.post("/set-initial-password")
async def set_initial_password(
    request: SetInitialPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await AuthController.set_initial_password(db, request.token, request.password)