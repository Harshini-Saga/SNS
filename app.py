from flask import Flask,render_template,request,redirect,session
from database import createTables
from database import AuthQueries
from utils import EmailTemplates,sendEmail
import random
app=Flask(__name__)

#home route
@app.route('/')
def home():
    return render_template('home.html')
#login
@app.route("/login",methods=['GET','POST'])
def login():
    #GET Request
    if request.method == 'GET':
        return render_template('login.html')
    #POST request   
    if request.method == 'POST':
        email=request.form.get("email")
        password=request.form.get("password")
        print(email,password)
@app.route("/register",methods=['GET','POST'])
def register():
    #GET Request
    if request.method == 'GET':
        return render_template('register.html')
    #POST request
    if request.method =='POST':
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        print(name,email,password,confirm_password)
        # check password and confirm password both same or not
        if password != confirm_password:
            print("Password mismatch")
            return redirect("/register")
        # check email already exists or not
        status,msg = AuthQueries.checkEmailExists(email=email)
        if status == True:
            print(msg)
            return redirect("/login")
        print(msg)
        if status == False:
            print(msg)
        # generate otp
        otp = random.randint(1000,9999) # It generates 4 digit random number
        # send otp via email
        body=EmailTemplates.registerEmailTemplate(otp=otp,username=name)
        status,msg=sendEmail(to_email=email,
                             subject="SNS Register",
                             body=body)
        if status == False:
            print(msg)
            return redirect('/register')
        session.clear()
        session['otp'] = otp
        session['username'] = name
        session['password'] = password
        # redirect to verify otp page
        return redirect('/verify-otp')
@app.route('/verify-otp',methods=['GET','POST'])
def verifyotp():
    if request.method=="GET":
        return render_template("verifyotp.html")
    

#main
if __name__=="__main__":
    print(createTables())
    app.run(debug=True)