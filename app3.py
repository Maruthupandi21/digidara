from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '1a2s6ws6e8c2g46h7e'  # Change in production!

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DATABASE'] = 'admine'

# File Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE']
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/notice2')
def notice2():
    conn = get_db_connection()
    if not conn:
        return render_template("notice2.html", error="Database connection failed")

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notices ORDER BY created_at DESC")
        notices = cursor.fetchall()
        return render_template("notice2.html", notices=notices)
    except mysql.connector.Error as e:
        print(f"Error fetching notices: {e}")
        return render_template("notice2.html", error="Failed to fetch notices")
    finally:
        cursor.close()
        conn.close()

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        password = request.form['password']
        try:
            admin_id = int(admin_id)
        except ValueError:
            return render_template("admin.html", error="Admin ID must be a number")

        conn = get_db_connection()
        if not conn:
            return render_template("admin.html", error="Database connection failed")

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admins WHERE admin_id=%s AND password=%s", (admin_id, password))
            admin = cursor.fetchone()
            if admin:
                session['admin'] = admin['admin_id']
                return redirect(url_for('admin_manage'))
            else:
                return render_template("admin.html", error="Invalid credentials")
        except mysql.connector.Error as e:
            print(f"Error during admin login: {e}")
            return render_template("admin.html", error="Database error during login")
        finally:
            cursor.close()
            conn.close()

    return render_template("admin.html")

@app.route('/post_notice', methods=['GET', 'POST'])
def post_notice():
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        department = request.form['department']
        posted_by = session.get('admin', 'Unknown')

        image_file = request.files.get('image')
        image_filename = None

        if image_file and image_file.filename != '' and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        conn = get_db_connection()
        if not conn:
            return render_template("post1.html", error="Database connection failed")

        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notices (title, description, category, department, posted_by, image_filename, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                (title, description, category, department, posted_by, image_filename)
            )
            conn.commit()
            return redirect(url_for('notice2'))
        except mysql.connector.Error as e:
            conn.rollback()
            print(f"Error inserting notice: {e}")
            return render_template("post1.html", error="Failed to post notice. Please try again.")
        finally:
            cursor.close()
            conn.close()

    return render_template("post1.html")

@app.route('/admin_manage')
def admin_manage():
    if 'admin' not in session:
        return redirect(url_for('admin'))

    conn = get_db_connection()
    if not conn:
        return render_template("admin_manage.html", error="Database connection failed")

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notices ORDER BY created_at DESC")
        notices = cursor.fetchall()
        return render_template("admin_manage.html", notices=notices)
    except mysql.connector.Error as e:
        print(f"Error fetching notices: {e}")
        return render_template("admin_manage.html", error="Failed to fetch notices")
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_notice', methods=['POST'])
def delete_notice():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    notice_id = request.form.get('notice_id')
    if not notice_id:
        return redirect(url_for('admin_manage'))

    conn = get_db_connection()
    if not conn:
        return render_template("admin_manage.html", error="Database connection failed")

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notices WHERE id = %s", (notice_id,))
        conn.commit()
    except mysql.connector.Error as e:
        print(f"Error deleting notice: {e}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_manage'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    # Redirect admin page to login page or admin_manage if logged in
    if 'admin' in session:
        return redirect(url_for('admin_manage'))
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
