from flask import Flask, render_template_string, request, redirect, url_for
from datetime import date
import mysql.connector

app = Flask(__name__)

# MySQL Database connection config
db_config = {
    'host': 'localhost',       # your MySQL host
    'user': 'root',            # your MySQL username
    'password': 'yourpassword',# your MySQL password
    'database': 'digital_notice_board'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

@app.route('/')
def home():
    return render_template_string(home_html)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    selected_notice = None
    msg = ''
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notices")
    all_notices = cursor.fetchall()

    if request.method == 'POST':
        notice_id = request.form.get('notice_id')
        if notice_id:
            cursor.execute("SELECT * FROM notices WHERE id = %s", (notice_id,))
            selected_notice = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template_string(admin_html, notices=all_notices, selected_notice=selected_notice, msg=msg)

@app.route('/admin/action', methods=['POST'])
def admin_action():
    notice_id = request.form.get('notice_id')
    title = request.form.get('title')
    message = request.form.get('message')
    action = request.form.get('action')

    msg = ''
    conn = get_db_connection()
    cursor = conn.cursor()

    if action == 'Add':
        cursor.execute(
            "INSERT INTO notices (title, message, date) VALUES (%s, %s, %s)",
            (title, message, date.today())
        )
        conn.commit()
        msg = 'Notice added successfully.'

    elif action == 'Update':
        if notice_id:
            cursor.execute(
                "UPDATE notices SET title = %s, message = %s, date = %s WHERE id = %s",
                (title, message, date.today(), notice_id)
            )
            conn.commit()
            msg = 'Notice updated successfully.'

    elif action == 'Delete':
        if notice_id:
            cursor.execute(
                "DELETE FROM notices WHERE id = %s", (notice_id,)
            )
            conn.commit()
            msg = 'Notice deleted successfully.'

    cursor.close()
    conn.close()

    # After action redirect to admin GET to avoid resubmission and refresh selection
    return redirect(url_for('admin'))

@app.route('/notices')
def view_notices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notices ORDER BY date DESC")
    all_notices = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template_string(view_html, notices=all_notices)

if __name__ == '__main__':
    app.run(debug=True)