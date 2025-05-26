from flask import Flask,render_template,request
import mysql.connector
logo=Flask(__name__)
db=mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dhanush@1",
    database="college"
)
cursor=db.cursor()
@logo.route("/")
def college():
    return render_template("login.html")
@logo.route('/login',methods=['POST'])
def login():
    username=request.form['username']
    password=request.form['password']
    insert__query="INSERT INTO tab(name,password)VALUES(%s,%s)"
    cursor.execute(insert__query,(username,password))
    db.commit()
    return "username added to database successfully"
if __name__=='__main__':
    logo.run(debug=True)
    