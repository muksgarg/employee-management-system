import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Employee Management System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .form-box { margin-bottom: 20px; padding: 15px; border: 1px solid #ccc; width: 350px; }
        input { width: 90%; padding: 8px; margin: 5px 0 10px 0; }
        button { padding: 8px 15px; background-color: #28a745; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h2>Employee Management System (Base App)</h2>
    <div class="form-box">
        <h3>Add Employee</h3>
        <form action="/add" method="POST">
            <input type="text" name="name" placeholder="Full Name" required><br>
            <input type="text" name="department" placeholder="Department" required><br>
            <input type="email" name="email" placeholder="Email" required><br>
            <button type="submit">Add</button>
        </form>
    </div>

    <h3>Employee List</h3>
    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Department</th>
            <th>Email</th>
        </tr>
        {% for emp in employees %}
        <tr>
            <td>{{ emp[0] }}</td>
            <td>{{ emp[1] }}</td>
            <td>{{ emp[2] }}</td>
            <td>{{ emp[3] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, employees=employees)

@app.route('/add', methods=['POST'])
def add_employee():
    name = request.form['name']
    department = request.form['department']
    email = request.form['email']
    
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employees (name, department, email) VALUES (?, ?, ?)", (name, department, email))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(port=5000, debug=True)