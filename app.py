from flask import Flask,render_template,request
from database import createTables


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
@app.route("/register",methods=['GET','POST'])
def register():
    #GET Request
    if request.method == 'GET':
        return render_template('register.html')
    #POST request
#main
if __name__=="__main__":
    print(createTables())
    app.run(debug=True)