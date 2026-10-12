import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import bcrypt
load_dotenv()


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('sender_email')
SENDER_PASSKEY = os.getenv('passkey')


#generate hashpasswod
def generateHashPassword(password:str):
    hash_password=bcrypt.hashpw(password=password.encode('utf-8'),salt=bcrypt.gensalt(4))
    return hash_password
#validate hash password
def validateHashPassword(password:str,hash_password:str):
    status=bcrypt.checkpw(password=password.encode('utf-8'),hashed_password=hash_password.encode('utf-8'))
    return status

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
        
        If you are not registering to this app, simply ignore this email and 
        dont share OTP with any one.
        
        Thank you
        
        Best wishes,
        SNS Management"""
        return template
    
#forgot password template
    @staticmethod
    def forgotPasswordTemplate(url:str,username:str="User"):
        template = f"""Hello {username},
        To manage your files and notes, first reset password and login with the new password.

        Your Reset Password Link:{url}

        If it is not done by you simply ignore this email
        Thanks for choosing the app.

        Regards
        SNS Management
        """
        return template