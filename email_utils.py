import smtplib
import random
from email.message import EmailMessage

# Store last sent OTP globally (or save in DB/session if production)
last_otp_sent = None  

def generate_otp():
    return random.randint(100000, 999999)  # 6-digit OTP

def send_otp_email(receiver_email, otp):
    sender_email = "ehrsystem123@example.com"  # Use a real sender
    sender_password = "agjxfunioqitctuo"

    subject = "Your OTP Code for EHR Authentication"
    body = f"Your OTP code is: {otp}"

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email
    message.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False
