from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from mysql.connector import errorcode

app = Flask(__name__)
app.secret_key = '1a2s6ws6e8c2g46h7e'  # Required for session management

# 🔧 MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DATABASE'] = 'admine'

# Function to create a database connection
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
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Invalid MySQL username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database does not exist")
        else:
            print(f"Error: {err}")
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
        # Convert admin_id to int to match the database column type
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
            admin = cursor.fetchone()  # Use fetchone() to get a single dictionary
            if admin:
                session['admin'] = admin['admin_id']
                return redirect(url_for('post_notice'))
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
    # Uncomment the following line to enforce admin-only access
    # if 'admin' not in session:
    #     return redirect(url_for('admin'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        department = request.form['department']
        posted_by = session.get('admin', 'Unknown')
        
        conn = get_db_connection()
        if not conn:
            return render_template("post1.html", error="Database connection failed")
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notices (title, description, category, department, posted_by) VALUES (%s, %s, %s, %s, %s)",
                (title, description, category, department, posted_by)
            )
            conn.commit()
            return redirect(url_for('home'))
        except mysql.connector.Error as e:
            conn.rollback()
            print(f"Error inserting notice: {e}")
            return render_template("post1.html", error="Failed to post notice. Please try again.")
        finally:
            cursor.close()
            conn.close()
    
    return render_template("post1.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    return render_template("admin.html")

if __name__ == '__main__':
    app.run(debug=True)