import asyncio
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Now import email service after environment is loaded
from app.services.email_service import email_service

async def test_sendgrid():
    """Test SendGrid email sending."""
    
    print("Testing SendGrid email configuration...")
    print(f"EMAIL_PROVIDER: {os.getenv('EMAIL_PROVIDER')}")
    print(f"SENDGRID_API_KEY: {os.getenv('SENDGRID_API_KEY')[:20]}...")
    print(f"SENDGRID_FROM_EMAIL: {os.getenv('SENDGRID_FROM_EMAIL')}")
    
    # Test sending an email
    try:
        result = await email_service.send_verification_email(
            to_email="test@example.com",
            verification_token="test-token-123",
            verification_link="http://localhost:8001/api/v1/auth/verify-email?token=test-token-123"
        )
        
        print("\nEmail sending result:")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Provider: {result.get('provider')}")
        
        if result.get('email_id'):
            print(f"Email ID: {result.get('email_id')}")
            
        if result.get('error'):
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_sendgrid())
