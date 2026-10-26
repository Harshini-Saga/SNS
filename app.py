from flask import Flask,render_template,request,redirect,session,url_for,send_file,flash
from database import createTables
from database import AuthQueries,NotesQueries,FileQueries
from utils import EmailTemplates,sendEmail,generateHashPassword,validateHashPassword
import random
import os
from werkzeug.utils import secure_filename
import uuid
#used to create token and validate token
from itsdangerous import URLSafeTimedSerializer,SignatureExpired,BadTimeSignature 
from mimetypes import guess_type
app=Flask(__name__)
app.secret_key = "Harshini@2005"
serializer=URLSafeTimedSerializer(app.secret_key)

if not os.path.exists('uploads'):
    os.mkdir('uploads')
#generate token
def generateToken(email:str):
    token=serializer.dumps(obj=email,salt="reset-password")
    return token

def validateToken(token):
    try:
        data = serializer.loads(token, salt="reset-password",max_age=600)#10 mins
        return data
    except BadTimeSignature:
        print("Time Expired")
        return redirect('/login')
    except SignatureExpired:
        print("Invalid URL")
        return redirect('/login')
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
        #check whether email exists or not
        status,user = AuthQueries.checkEmailExists(email=email,data=True)
        if status == False:
            flash(user,'msg' if status else 'err')
            return redirect('/login')
        #match the password with the database password
        status = validateHashPassword(password=password,hash_password=user['hashpassword'])
        if status == False:
            flash("Password incorrect",'msg' if status else 'err')
            return redirect('/login')
        #redirect to dashboard page
        session.clear()
        session['id']=user['userid']
        session['username']=user['username']
        return redirect('/dashboard')

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
            flash("Password Mismatch",'msg' if status else 'err')
            return redirect("/register")
        # check email already exists or not
        status,msg = AuthQueries.checkEmailExists(email=email)
        if status == True:
            flash(msg,'msg' if status else 'err')
            return redirect("/login")
        print(msg)
        if status == False:
            flash(msg,'msg' if status else 'err')
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
        session['email'] = email
        # redirect to verify otp page
        return redirect('/verify-otp')
@app.route('/verify-otp',methods=['GET','POST'])
def verifyotp():
    if request.method=="GET":
        return render_template("verifyotp.html")
    if request.method=="POST":
        otp=int(request.form.get('otp'))
        #match otp
        if otp!=session['otp']:
            print("OTP Incorrect")
            return redirect("/verify-otp")
        hash_password = generateHashPassword(password=session['password'])
        #store user data in database
        status,msg=AuthQueries.insertUserRecord(username=session['username'],email=session['email'],hash_password=hash_password)
        if status == False:
            print(msg)
            return redirect('/')
        if status==True:
            print(msg)
            return redirect('/login')

#forgot password
@app.route('/forgot-password',methods=['GET','POST'])
def forgot_password():
    if request.method=='GET':
        return render_template('forgot_password.html')
    if request.method == 'POST':
        email=request.form.get('email')
        #check email exists
        status,msg=AuthQueries.checkEmailExists(email=email)
        if status == False:
            print(msg)
            return redirect(url_for('login'))
        #generate token
        token=generateToken(email=email)
        reset_link=url_for('reset_password',token=token,_external=True)
        #store email in token
        #generate reset password link
        #send link via email
        body = EmailTemplates.forgotPasswordTemplate(url=reset_link)
        status,msg=sendEmail(to_email=email,subject="Reset Password - SNS",
                            body=body)
        if status == False:
            print(msg)
            return redirect(url_for('forgot_password'))
        print(msg)
        #redirect to login page
        return redirect(url_for('login'))
#reset password
@app.route('/reset-password/<token>', methods=['GET','POST'])
def reset_password(token):
    #validate token
    email=validateToken(token=token)
    if request.method == 'GET':
        return render_template('reset_password.html',token_val=token)
    if request.method == 'POST':
        new_password=request.form.get('new_password')
        confirm_password=request.form.get('confirm_password')
        if new_password!=confirm_password:
            print("Password missmatch")
            return redirect(url_for('reset_password',token=token))
        #generate hash password
        hash_password=generateHashPassword(password=new_password)
        #update new hash password in database
        status,msg=AuthQueries.updatePassword(email=email,hash_password=hash_password)
        print(msg)
        return f"<h2>{msg}</h2>"
        #return msg like "Password updated"

#Dashboard
@app.route('/dashboard')
def dashboard():
    if 'id' not in session:
        return redirect('/login')
    return render_template('dashboard.html',username=session.get('username'))
# =====================================================================================
#                                      Notes Routes
# =====================================================================================  
@app.route('/dashboard/notes')
def mynotes():
    if 'id' not in session:
        return redirect('/login')
    userid=session['id']
    status,all_notes=NotesQueries.getAllNotes(userid=userid)
    return render_template('notes.html',notes=all_notes)


@app.route('/dashboard/notes/newnotes',methods=['GET','POST'])
def newnotes():
    if 'id' not in session:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('newnotes.html')
    if request.method == 'POST':
        title=request.form.get('title')
        content=request.form.get('content')
        userid=session['id']
        status,msg=NotesQueries.insertNotesRecord(userid=userid,title=title,content=content)
        print(msg)
        return redirect(url_for('mynotes'))
#view notes
@app.route('/dashboard/notes/view/<int:id>')
def view_notes(id):
    if 'id' not in session:
        return redirect('/login')
    #get notes by using notes id
    status,note=NotesQueries.getAllNotes(userid=session['id'],notesid=id)
    return render_template('view_notes.html',title=note['title'],content=note['content'])


# update notes
@app.route("/dashboard/notes/update/<int:notesid>", methods = ['GET','POST'])
def update_notes(notesid):
    if 'id' not in session:
            return redirect('/login')
    if request.method == 'GET':
        # get notes by notes id
        status, note = NotesQueries.getAllNotes(userid=session['id'],
                                                 notesid=notesid)
        return render_template('editnotes.html',
                               title = note['title'],
                               content = note['content'],
                               id = notesid)
    if request.method =='POST':
        title = request.form.get('title')
        content = request.form.get('content')
        # update notes in database
        status, msg = NotesQueries.updateNotes(notesid=notesid, 
                                               title=title,
                                               content=content)
        print(msg)
        return redirect(url_for('mynotes'))

@app.route("/dashboard/notes/delete/<int:notesid>")
def delete_notes(notesid):
    if 'id' not in session:
            return redirect('/login')
    if request.method == 'GET':
        status, msg = NotesQueries.deleteNotes(notesid=notesid)
        print(msg)
        return redirect(url_for('mynotes'))

# =====================================================================================
#                                      Files Routes
# =====================================================================================  
@app.route("/dashboard/files")
def myfiles():
    if 'id' not in session:
            return redirect('/login')
    #get all files based on userid
    status,all_files=FileQueries.getAllFiles(userid=session['id'])
    return render_template('files.html',files=all_files)

@app.route("/dashboard/files/upload-file" ,methods=['GET','POST'])
def upload_file():
    if 'id' not in session:
            return redirect('/login')
    if request.method=="GET":
        return render_template("upload_file.html")
    if request.method=="POST":
        file=request.files.get("file")
        #file meta data
        original_name = file.filename
        file_name=secure_filename(original_name)
        file_type=original_name.split(".")[-1]
        if file_type not in ('pdf','jpeg','jpg','docx','png','csv'):
            print("File type not allowed")
            return redirect(url_for('upload_file'))
        unique_name = str(uuid.uuid1()) + "_"+ file_name
        file_path = os.path.join('uploads',unique_name)
        #save file
        file.save(file_path)
        file_size=os.path.getsize(file_path)
        mime_type=guess_type(file_path)[0]
        data = (session['id'],original_name,unique_name,mime_type,file_size,file_path)
        status , msg = FileQueries.insertFileRecord(file_data=data)
        #store file meta data in table
        print(msg)
        return redirect(url_for('myfiles'))
@app.route("/dashboard/files/view/<int:file_id>")
def view_file(file_id):
    if 'id' not in session:
            return redirect('/login')
    #get file meta data by using file_id
    status,file = FileQueries.getAllFiles(userid=session['id'],fileid=file_id)
    return send_file(
        path_or_file=file['filepath'],
        mimetype=file['mimetype'],
        as_attachment=False
    )

@app.route("/dashboard/files/download/<int:file_id>")
def download_file(file_id):
    if 'id' not in session:
            return redirect('/login')
    status,file = FileQueries.getAllFiles(userid=session['id'],fileid=file_id)
    return send_file(
            path_or_file=file['filepath'],
            mimetype=file['mimetype'],
            as_attachment=True
        )

@app.route("/dashboard/files/delete/<int:file_id>")
def delete_file(file_id):
    if 'id' not in session:
            return redirect('/login')
    status, msg = FileQueries.deleteFiles(fileid=file_id)
    print(msg)
    return redirect(url_for('myfiles'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect('/login')
#main
if __name__=="__main__":
    print(createTables())
    app.run(debug=True)
    