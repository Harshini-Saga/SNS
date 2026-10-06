import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()


SMTP_SERVER = "www.smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('sender_email')
SENDER_PASSKEY = os.getenv('passkey')

def sendEmail(to_email:str, subject:str, body:str):
    msg=MIMEMultipart()
    msg['FROM'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body,'plain'))
    try:
        server = smtplib.SMTP(host = SMTP_SERVER, port = SMTP_PORT)
        server.starttls() # server start
        server.login(user=SENDER_EMAIL,password=SENDER_PASSKEY)
        server.sendmail(SENDER_EMAIL,to_email,msg.as_string())
        server.quit() # close server
        return True,"Email Send to Registered Mail"
    except Exception as e:
        return False,f"Something wrong in utils.py-sendEmail():{e}"
class EmailTemplates:
    @staticmethod
    def registerEmailTemplate(otp:int, username:str="Dear"):
        template = f"""Hello {username},
        Thanks for choosing SNS app to manage your files and notes
        
        Your OTP:{otp}
        
        If you are not registering to this app, simple ignore this email and 
        dont share OTP with any one.
        
        Thank you
        
        Best wishes,
        SNS Management"""
        return template

