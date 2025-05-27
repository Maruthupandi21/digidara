from flask import Flask, render_template,request,redirect
from flask_mysqldb import MySQL

notices = Flask(__name__)
notices.config['MYSQL_HOST'] = 'localhost'
notices.config['MYSQL_USER']='root'
notices.config['MYSQL_PASSWORD']='yourpassword'
notices.config['MYSQL_DB']='notices_db'
mysql = MySQL(notices)
@notices.route('/')
def show_notices():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notices ORDER BY date DESC")
    notices = cur.fetchall()
    return render_template('notices_board.html', notices=notices)

@notices.route('/post',methods=['GET','POST'])
def post_notice():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        department = request.form['department']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO notices (title, description, category, department) VALUES (%s, %s, %s, %s)", (title, description, category, department))
        mysql.connection.commit()
        return redirect('/')
    return render_template('post_notice.html')
@notices.route('/admin', methods=['GET', 'POST'])
def manage_notices():
    if request.method == 'POST':
        notice_id = request.form['notice_id']
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM notices WHERE_id = %s", (notice_id,))
        mysql.connection.commit()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notices ORDER BY posted_on DESC")
    notices = cur.fetchall()
    return render_template('admin_manage.html', notices=notices)
    

    
    