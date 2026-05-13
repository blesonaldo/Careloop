# Careloop Authentication System

A complete, production-ready authentication backend built with FastAPI and PostgreSQL.

## Features

### Core Authentication
- **User Registration** - Secure signup with email validation
- **User Login** - JWT-based authentication
- **Password Security** - Bcrypt hashing with strength validation
- **Token Management** - Secure JWT tokens with configurable expiry

### Email Verification
- **Email Verification** - Required for account activation
- **Secure Tokens** - Time-limited verification tokens (24 hours)
- **Mock Email Service** - Development-friendly email simulation
- **SendGrid Ready** - Easy production email integration

### Password Management
- **Forgot Password** - Secure password reset flow
- **Reset Tokens** - Time-limited reset tokens (1 hour)
- **Password Change** - Authenticated password updates
- **Security Validation** - Password strength requirements

### Security Features
- **JWT Authentication** - Industry-standard token-based auth
- **Token Expiry** - Configurable token lifetimes
- **Email Verification Required** - Prevents unverified access
- **Account Status** - Active/inactive user management
- **Superuser Support** - Admin privilege system

## API Endpoints

### Authentication Routes (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/signup` | Register new user | No |
| POST | `/login` | User authentication | No |
| GET | `/verify-email` | Verify email address | No |
| POST | `/forgot-password` | Send reset email | No |
| POST | `/reset-password` | Reset password | No |
| POST | `/change-password` | Change password | Yes |
| GET | `/me` | Get current user | Yes |

## Project Structure

```
app/
|-- controllers/
|   |-- auth_controller.py          # Business logic
|-- models/
|   |-- user.py                     # User SQLAlchemy model
|-- routes/
|   |-- auth.py                     # API endpoints
|-- schemas/
|   |-- user.py                     # Pydantic schemas
|-- services/
|   |-- auth_service.py             # JWT & password services
|   |-- email_service.py            # Email abstraction layer
|-- utils/
|   |-- auth.py                     # Auth middleware & dependencies
```

## Environment Configuration

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/careloop

# Authentication
SECRET_KEY=your-super-secret-key-change-in-production-please

# Email Configuration
EMAIL_PROVIDER=mock                    # or "sendgrid" for production
SENDGRID_API_KEY=                       # Required for SendGrid
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    email_verification_expires_at TIMESTAMP,
    password_reset_token VARCHAR(255),
    password_reset_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);
```

## Usage Examples

### User Registration
```bash
curl -X POST "http://localhost:8001/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### User Login
```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Protected Route
```bash
curl -X GET "http://localhost:8001/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Email Service Integration

### Mock Provider (Development)
- Logs emails to console
- Returns tokens in API responses
- Perfect for testing and development

### SendGrid Integration (Production)
Simply change `EMAIL_PROVIDER=sendgrid` and add your SendGrid API key:

```env
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.your-sendgrid-api-key
```

The email service will automatically use SendGrid without any code changes.

## Security Features

### Password Security
- **Bcrypt Hashing** - Industry-standard password hashing
- **Strength Validation** - Minimum 8 characters required
- **Secure Storage** - Never store plain text passwords

### Token Security
- **JWT Tokens** - Signed with HS256 algorithm
- **Configurable Expiry** - Default 60 minutes
- **Secure Payload** - Contains user ID and email only

### Email Security
- **Time-Limited Tokens** - 24 hours for verification, 1 hour for reset
- **Unique Tokens** - Cryptographically secure token generation
- **Token Invalidation** - Tokens cleared after use

## Middleware & Dependencies

### Authentication Dependencies
```python
from app.utils.auth import get_current_user_id, get_current_user

# Require authentication
@router.get("/protected")
async def protected_route(user_id: int = Depends(get_current_user_id)):
    return {"user_id": user_id}

# Get full user object
@router.get("/user-info")
async def user_info(current_user = Depends(get_current_user)):
    return {"user": current_user}
```

### Optional Authentication
```python
from app.utils.auth import optional_auth

@router.get("/public")
async def public_route(user_id: Optional[int] = Depends(optional_auth)):
    if user_id:
        return {"message": "Authenticated user", "user_id": user_id}
    else:
        return {"message": "Anonymous user"}
```

## Database Setup

1. **Run Migrations**
```bash
alembic upgrade head
```

2. **Create Database** (if not exists)
```bash
createdb -U postgres -h localhost -p 5432 careloop
```

## Development

### Start the Server
```bash
uvicorn main:app --reload
```

### API Documentation
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Testing Endpoints
```bash
# Test database connection
curl http://localhost:8001/test-db

# List users (for testing)
curl http://localhost:8001/users
```

## Production Deployment

### Environment Variables
```env
# Production configuration
SECRET_KEY=your-very-secure-production-secret-key
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.your-production-sendgrid-key
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/careloop
```

### Security Considerations
- Use a strong, randomly generated SECRET_KEY
- Configure proper CORS origins
- Enable HTTPS in production
- Use environment-specific database credentials
- Monitor email deliverability

## Future Enhancements

### Planned Features
- **Two-Factor Authentication** - TOTP/ SMS verification
- **OAuth Integration** - Google, GitHub, etc.
- **Rate Limiting** - Prevent brute force attacks
- **Session Management** - Multiple device support
- **Audit Logging** - Track authentication events

### Email Enhancements
- **Email Templates** - Beautiful HTML templates
- **Email Queue** - Background email processing
- **Email Analytics** - Track open/click rates
- **Multi-language Support** - Internationalized emails

## Support

This authentication system is production-ready and follows security best practices. For questions or issues, refer to the FastAPI documentation and SQLAlchemy best practices.
