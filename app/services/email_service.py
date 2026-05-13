from typing import Optional
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Debug: Print all environment variables that start with SENDGRID
        print("Available SENDGRID environment variables:")
        for key, value in os.environ.items():
            if key.startswith("SENDGRID"):
                print(f"  {key}: {'*' * (len(value) - 4) + value[-4:] if value else 'None'}")
        
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@careloop.com")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "Careloop")
        
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY not found in environment variables")
        else:
            logger.info("SendGrid API key loaded successfully")
    
    async def send_verification_email(self, email: str, token: str) -> bool:
        """Send email verification email"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(email),
                subject="Verify your Careloop account",
                html_content=self._get_verification_email_template(token)
            )
            
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Verification email sent to {email}")
                return True
            else:
                logger.error(f"Failed to send verification email: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False
    
    async def send_password_reset_email(self, email: str, token: str) -> bool:
        """Send password reset email"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(email),
                subject="Reset your Careloop password",
                html_content=self._get_password_reset_email_template(token)
            )
            
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Password reset email sent to {email}")
                return True
            else:
                logger.error(f"Failed to send password reset email: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return False
    
    async def send_welcome_email(self, email: str, name: str) -> bool:
        """Send welcome email"""
        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(email),
                subject="Welcome to Careloop!",
                html_content=self._get_welcome_email_template(name)
            )
            
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            if response.status_code == 202:
                logger.info(f"Welcome email sent to {email}")
                return True
            else:
                logger.error(f"Failed to send welcome email: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False
    
    def _get_verification_email_template(self, token: str) -> str:
        """Get HTML template for verification email"""
        verification_url = f"http://localhost:8001/verify-email?token={token}"
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Careloop Account</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; border: 1px solid #e9ecef;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2c3e50; margin-bottom: 10px; font-size: 24px;">Careloop CRM</h1>
                    <p style="color: #6c757d; margin: 0; font-size: 16px;">Customer Relationship Management</p>
                </div>
                
                <h2 style="color: #2c3e50; margin-bottom: 20px; font-size: 20px;">Verify Your Email Address</h2>
                
                <p style="color: #495057; line-height: 1.6; margin-bottom: 25px;">
                    Thank you for registering with Careloop! To complete your registration and activate your account, please verify your email address by clicking the button below.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 600; font-size: 16px;">Verify Email Address</a>
                </div>
                
                <div style="background: #e9ecef; padding: 15px; border-radius: 6px; margin: 25px 0;">
                    <p style="color: #495057; font-size: 14px; margin: 0 0 10px 0;">
                        <strong>Alternative:</strong> If the button above doesn't work, you can copy and paste this link into your browser:
                    </p>
                    <p style="color: #007bff; word-break: break-all; font-size: 12px; margin: 0;">{verification_url}</p>
                </div>
                
                <div style="border-top: 1px solid #dee2e6; margin-top: 30px; padding-top: 20px;">
                    <p style="color: #6c757d; font-size: 12px; margin: 0 0 10px 0;">
                        <strong>Important:</strong> This verification link will expire in 24 hours for security reasons.
                    </p>
                    <p style="color: #6c757d; font-size: 12px; margin: 0;">
                        If you didn't create an account with Careloop, please ignore this email or contact our support team.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 25px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; font-size: 12px; margin: 0;">
                        © 2026 Careloop CRM. All rights reserved.
                    </p>
                    <p style="color: #6c757d; font-size: 12px; margin: 5px 0 0 0;">
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_password_reset_email_template(self, token: str) -> str:
        """Get HTML template for password reset email"""
        reset_url = f"http://localhost:8001/reset-password?token={token}"
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reset Your Password</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #3333FF; margin-bottom: 20px;">Reset Your Password</h1>
                <p style="color: #666; line-height: 1.6;">We received a request to reset your password. Click the button below to create a new password.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background: #3333FF; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
                </div>
                
                <p style="color: #666; font-size: 14px;">If the button above doesn't work, you can copy and paste this link into your browser:</p>
                <p style="color: #3333FF; word-break: break-all; font-size: 12px;">{reset_url}</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">This link will expire in 1 hour. If you didn't request a password reset, please ignore this email.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_welcome_email_template(self, name: str) -> str:
        """Get HTML template for welcome email"""
        dashboard_url = "http://localhost:3001/Frontend/careloop-dashboard.html"
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Welcome to Careloop!</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #3333FF; margin-bottom: 20px;">Welcome to Careloop, {name}! 👋</h1>
                <p style="color: #666; line-height: 1.6;">Thank you for joining Careloop! Your account has been successfully created and you're ready to start managing your customer relationships more efficiently.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin-bottom: 15px;">What's next?</h3>
                    <ul style="color: #666; line-height: 1.8;">
                        <li>Add your first customers to get started</li>
                        <li>Set up follow-up reminders</li>
                        <li>Track sales and revenue</li>
                        <li>Generate detailed reports</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{dashboard_url}" style="background: #3333FF; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Go to Dashboard</a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">If you have any questions, feel free to reach out to our support team.</p>
            </div>
        </body>
        </html>
        """

# Create a singleton instance
email_service = EmailService()
