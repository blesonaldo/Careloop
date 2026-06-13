import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.gmail_user = os.getenv("GMAIL_USER")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        self.from_name = os.getenv("MAIL_FROM_NAME", "Careloop")

        if not self.gmail_user or not self.gmail_password:
            logger.warning("WARNING: GMAIL_USER or GMAIL_APP_PASSWORD not set in .env")
        else:
            logger.info(f"Gmail SMTP loaded for {self.gmail_user}")

    def _send(self, to_email: str, subject: str, html: str) -> bool:
    if not self.gmail_user or not self.gmail_password:
        print("ERROR: Gmail credentials not configured")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Careloop <{self.gmail_user}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html"))

        print(f"Attempting to send email to {to_email}...")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.sendmail(self.gmail_user, to_email, msg.as_string())

        print(f"SUCCESS: Email sent to {to_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP AUTH FAILED: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP ERROR: {e}")
        return False
    except Exception as e:
        print(f"EMAIL ERROR: {e}")
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
                    Thank you for registering with Careloop! Click the button below to verify your email and activate your account.
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background: #3333FF; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 600; font-size: 16px;">Verify Email Address</a>
                </div>
                <div style="background: #e9ecef; padding: 15px; border-radius: 6px; margin: 25px 0;">
                    <p style="color: #495057; font-size: 14px; margin: 0 0 10px 0;">
                        <strong>Alternative:</strong> Copy and paste this link into your browser:
                    </p>
                    <p style="color: #3333FF; word-break: break-all; font-size: 12px; margin: 0;">{verification_url}</p>
                </div>
                <p style="color: #6c757d; font-size: 12px;">This link expires in 24 hours. If you didn't sign up, please ignore this email.</p>
                <div style="text-align: center; margin-top: 25px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; font-size: 12px; margin: 0;">© 2026 Careloop CRM. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _get_password_reset_email_template(self, token: str, base_url: str = "http://localhost:8001") -> str:
        reset_url = f"{base_url}/reset-password?token={token}"
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Reset Your Password</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #3333FF; margin-bottom: 20px;">Reset Your Password</h1>
                <p style="color: #666; line-height: 1.6;">We received a request to reset your password. Click the button below to create a new password.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background: #3333FF; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
                </div>
                <p style="color: #666; font-size: 14px;">Or copy this link: <span style="color: #3333FF;">{reset_url}</span></p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">This link expires in 1 hour. If you didn't request this, ignore this email.</p>
            </div>
        </body>
        </html>
        """

    def _get_welcome_email_template(self, name: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Welcome to Careloop!</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h1 style="color: #3333FF; margin-bottom: 20px;">Welcome to Careloop, {name}! 👋</h1>
                <p style="color: #666; line-height: 1.6;">Your account is ready. Start managing your customer relationships today.</p>
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin-bottom: 15px;">What's next?</h3>
                    <ul style="color: #666; line-height: 1.8;">
                        <li>Add your first customers to get started</li>
                        <li>Set up follow-up reminders</li>
                        <li>Track sales and revenue</li>
                        <li>Generate detailed reports</li>
                    </ul>
                </div>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">If you have any questions, reach out to our support team.</p>
            </div>
        </body>
        </html>
        """

# Singleton instance
email_service = EmailService()
