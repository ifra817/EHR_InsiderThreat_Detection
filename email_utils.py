import smtplib
import random
from email.message import EmailMessage

# Store last sent OTP globally (or save in DB/session if production)
last_otp_sent = None  

def generate_otp():
    otp=''
    for i in range(6):
        otp+= str(random.randint(0,9))
    print(otp)
    return otp

def send_otp_email(receiver_email, otp):
    sender_email = "ehrsystem123@gmail.com"  # Use a real sender
    sender_password = 'agjxfunioqitctuo'

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
            print("smtp login successfull")
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

