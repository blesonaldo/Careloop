import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

gmail_user = os.getenv("GMAIL_USER")
gmail_password = os.getenv("GMAIL_APP_PASSWORD")

print(f"User: {gmail_user}")
print(f"Password loaded: {'Yes' if gmail_password else 'NO - CHECK YOUR .env'}")

try:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Careloop SMTP Test"
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    msg.attach(MIMEText("<h1>SMTP is working!</h1>", "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, gmail_user, msg.as_string())

    print("SUCCESS — check your inbox!")

except smtplib.SMTPAuthenticationError:
    print("FAILED — wrong credentials. Use a Gmail App Password, not your real password")
except Exception as e:
    print(f"FAILED — {e}")
