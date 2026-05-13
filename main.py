from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, Response
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from app.database import get_db, init_db
from app.models import Customer, User
from app.routes import auth, user, customer, message
from fastapi import APIRouter
from app.schemas.user import UserResponse, ResetPasswordRequest, SetInitialPasswordRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.controllers.auth_controller import AuthController
import os

# Ensure all models are imported for database initialization
from app.models import *

app = FastAPI(
    title="Careloop API",
    description="Customer Relationship Management API for Small Businesses",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
from app.database import engine
from app.models.user import User
from app.models.base import Base

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        # For SQLite, run sync create_all within async context
        await conn.run_sync(Base.metadata.create_all)



@app.get("/api/auth/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    result = await AuthController.verify_email(db, token)
    return result
# Create main router for unified routing
main_router = APIRouter()

# Frontend page routes
@main_router.get("/", response_class=HTMLResponse)
async def serve_signup():
    """Serve the signup page as the default route."""
    try:
        with open("Frontend/careloop-signup.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Careloop</h1><p>Signup page not found</p>", status_code=404)

@main_router.get("/login", response_class=HTMLResponse)
async def serve_login_page():
    """Serve the login page."""
    try:
        with open("Frontend/careloop-login.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Login page not found</h1>", status_code=404)

@main_router.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard_page():
    """Serve the dashboard page."""
    try:
        with open("Frontend/careloop-dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard page not found</h1>", status_code=404)

@main_router.get("/reports", response_class=HTMLResponse)
async def serve_reports_page():
    """Serve the reports page."""
    try:
        with open("Frontend/careloop-reports.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Reports page not found</h1>", status_code=404)

@main_router.get("/forgot-password", response_class=HTMLResponse)
async def serve_forgot_password_page():
    """Serve the forgot password page."""
    try:
        with open("Frontend/forgot-password.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Forgot password page not found</h1>", status_code=404)

@main_router.get("/reset-password", response_class=HTMLResponse)
async def serve_reset_password_page():
    """Serve the reset password page."""
    try:
        with open("Frontend/reset-password.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Reset password page not found</h1>", status_code=404)

@main_router.get("/create-password", response_class=HTMLResponse)
async def serve_create_password_page():
    """Serve the create password page."""
    try:
        with open("Frontend/create-password.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Create password page not found</h1>", status_code=404)

# Mount static files directory
app.mount("/assets", StaticFiles(directory="Frontend/assets"), name="assets")

# Include the main router for frontend routes
app.include_router(main_router)

# Include API routes
app.include_router(auth.router, prefix="/api")

# Add direct route for email verification (without /api prefix)
@app.get("/verify-email")
async def verify_email_redirect(token: str, db: AsyncSession = Depends(get_db)):
    """Verify user email address and redirect to email-verified page."""
    from app.controllers.auth_controller import AuthController
    await AuthController.verify_email(db, token)
    
    # Serve the email-verified.html file with token injected
    try:
        with open("Frontend/email-verified.html", "r", encoding="utf-8") as f:
            html = f.read()
            print(f"Original HTML contains create-password link: {'href="/create-password"' in html}")
            # Replace the create-password link with token
            html = html.replace('href="/create-password"', f'href="/create-password?token={token}"')
            print(f"After replacement HTML contains token: {'token=' in html}")
            return HTMLResponse(content=html)
    except FileNotFoundError:
        return HTMLResponse(content=f"<h1>Email verified successfully!</h1><p><a href='/create-password?token={token}'>Create Password</a></p>", status_code=200)

# Add favicon route to prevent 404 error
@app.get("/favicon.ico")
async def favicon():
    """Return favicon."""
    try:
        with open("Frontend/favicon.ico", "rb") as f:
            return Response(content=f.read(), media_type="image/x-icon")
    except FileNotFoundError:
        # Return a simple 1x1 pixel favicon
        return Response(content=b"", media_type="image/x-icon")

# Add direct route for reset password (without router prefix)
@app.get("/reset-password")
async def reset_password_page():
    """Serve the reset password page."""
    try:
        with open("Frontend/reset-password.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Reset password page not found</h1>", status_code=404)

# Add direct POST route for password reset (without router prefix)
@app.post("/reset-password")
async def reset_password_submit(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset user password."""
    from app.schemas.user import ResetPasswordRequest
    from app.controllers.auth_controller import AuthController
    return await AuthController.reset_password(db, request)

# Add direct route for signup success page (without router prefix)
@app.get("/signup-success", response_class=HTMLResponse)
async def serve_signup_success_page():
    """Serve the signup success page."""
    try:
        with open("Frontend/signup-success.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)

# Add direct route for set-initial-password (without router prefix)
@app.post("/set-initial-password")
async def set_initial_password_submit(request: SetInitialPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Set initial password after email verification."""
    from app.schemas.user import SetInitialPasswordRequest
    from app.controllers.auth_controller import AuthController
    return await AuthController.set_initial_password(db, request.token, request.password)

app.include_router(user.router, prefix="/api")
app.include_router(customer.router)
app.include_router(message.router)


@app.get("/careloop-signup.html", response_class=HTMLResponse)
async def serve_signup_page():
    """Serve the signup page."""
    try:
        with open("Frontend/careloop-signup.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)

@app.get("/careloop-login.html", response_class=HTMLResponse)
async def serve_login_page():
    """Serve the login page."""
    try:
        with open("Frontend/careloop-login.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)

@app.get("/careloop-dashboard.html", response_class=HTMLResponse)
async def serve_dashboard_page():
    """Serve the dashboard page."""
    try:
        with open("Frontend/careloop-dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)

@app.get("/forgot-password.html", response_class=HTMLResponse)
async def serve_forgot_password_page():
    """Serve the forgot password page."""
    try:
        with open("Frontend/forgot-password.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)

@app.get("/reset-password.html", response_class=HTMLResponse)
async def serve_reset_password_page():
    """Serve the reset password page."""
    try:
        with open("Frontend/reset-password.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)

@app.get("/create-password.html", response_class=HTMLResponse)
async def serve_create_password_page():
    """Serve the create password page."""
    try:
        with open("Frontend/create-password.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)

@app.get("/customers.html", response_class=HTMLResponse)
async def serve_customers_page():
    """Serve the customers page."""
    try:
        with open("Frontend/customers.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page not found</h1>", status_code=404)

@app.get("/api")
async def api_root():
    return {
        "message": "Careloop API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/test-db")
async def test_database():
    """Test database connection."""
    try:
        async for db in get_db():
            result = await db.execute(select(Customer).limit(1))
            customers = result.scalars().all()
            
            result = await db.execute(select(User).limit(1))
            users = result.scalars().all()
            
            return {
                "status": "connected", 
                "customer_count": len(customers),
                "user_count": len(users),
                "message": "Database connection successful!"
            }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "message": "Database connection failed"
        }

@app.get("/customers")
async def get_customers():
    """Get all customers."""
    try:
        async for db in get_db():
            result = await db.execute(select(Customer))
            customers = result.scalars().all()
            return {"customers": [{"id": c.id, "name": c.name, "email": c.email} for c in customers]}
    except Exception as e:
        return {"error": str(e)}

@app.get("/users")
async def get_users():
    """Get all users (for testing)."""
    try:
        async for db in get_db():
            result = await db.execute(select(User))
            users = result.scalars().all()
            return {"users": [{"id": u.id, "email": u.email, "is_verified": u.is_email_verified} for u in users]}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
