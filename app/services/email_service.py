import os
from dotenv import load_dotenv
import pathlib
import os as _os
load_dotenv(dotenv_path=_os.path.join(_os.getcwd(), ".env"), override=True)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        print(f"CWD: {os.getcwd()}")
        print(f"ENV FILE EXISTS: {os.path.exists(os.path.join(os.getcwd(), '.env'))}")
        print(f"GMAIL_USER RAW: {os.getenv('GMAIL_USER')}")
        self.gmail_user = os.getenv("GMAIL_USER")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "Careloop")
        if not self.gmail_user or not self.gmail_password:
            print("WARNING: Gmail credentials not found")
        else:
            print("Gmail SMTP loaded successfully")

    def _send(self, to_email: str, subject: str, html: str) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.gmail_user}>"
            msg["To"] = to_email
            msg.attach(MIMEText(html, "html"))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.gmail_user, self.gmail_password)
                server.sendmail(self.gmail_user, to_email, msg.as_string())
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    async def send_verification_email(self, email: str, token: str, base_url: str = "http://localhost:8001") -> bool:
        html = self._get_verification_email_template(token, base_url)
        return self._send(email, "Verify your Careloop account", html)

    async def send_password_reset_email(self, email: str, token: str, base_url: str = "http://localhost:8001") -> bool:
        html = self._get_password_reset_email_template(token, base_url)
        return self._send(email, "Reset your Careloop password", html)

    async def send_welcome_email(self, email: str, name: str) -> bool:
        html = self._get_welcome_email_template(name)
        return self._send(email, "Welcome to Careloop!", html)

    def _get_verification_email_template(self, token: str, base_url: str = "http://localhost:8001") -> str:
        """Get HTML template for verification email"""
        verification_url = f"{base_url}/verify-email?token={token}"
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
    
    def _get_password_reset_email_template(self, token: str, base_url: str = "http://localhost:8001") -> str:
        """Get HTML template for password reset email"""
        reset_url = f"{base_url}/reset-password?token={token}"
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
