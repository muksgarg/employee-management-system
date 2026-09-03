from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

# --- HTML Template ---
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Employee Management System</title>
    <style>
        body { font-family: Arial, sans-serif; background:#f6f8fb; margin:0; padding:0; }
        .container { max-width: 800px; margin: 40px auto; background:#fff; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,.06); padding: 24px; }
        h1, h2 { text-align:center; color:#394867; }
        .flash { padding:10px 16px; margin:12px 0 0 0; border-radius:5px; color: #234040; background:#ecfcec; border:1px solid #b8dfc5;}
        .flash.error { color: #6d1e11; background:#fff0f0; border:1px solid #ecaab8; }
        table { width:100%; border-collapse: collapse; margin:24px 0;}
        th, td { padding:10px 14px; border-bottom: 1px solid #e0e4ea; text-align: left;}
        th {background: #c3d1e6;}
        tr:last-child td { border-bottom:none;}
        .actions a, .actions form { display:inline;}
        .btn { padding: 4px 12px; border:none; border-radius:3px; text-decoration:none; cursor:pointer;}
        .btn-edit { background:#ffeec3; color:#937102;}
        .btn-delete { background:#ffc5c5; color: #a12323;}
        .btn-add { background:#bbdcf7; color: #234877;}
        .btn-search { background:#d4ffe6; color:#15784a; }
        .form-row { display:flex; gap:14px;}
        .input, select { padding: 6px 8px; border:1px solid #aaabcd; border-radius:3px;}
        .input:focus { outline:1px solid #8eacff;}
        .search-bar { margin-top: 10px; margin-bottom: 20px;}
        label { min-width:85px; font-weight:600; }
        .confirm-box { background:#fffaa9; padding:18px; border-radius:6px; margin:30px auto; width:340px; text-align:center;}
    </style>
</head>
<body>
<div class="container">
    <h1>Employee Management System</h1>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="flash {{ category }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {# --- Search and Filter Bar --- #}
    <form class="search-bar" method="GET" action="/">
        <div class="form-row">
            <input class="input" style="flex:2;" type="text" name="search" value="{{ request.args.get('search','') }}" placeholder="Search by Name...">
            <select name="department" class="input" style="flex:1;">
                <option value="">All Departments</option>
                {% for dep in departments %}
                  <option value="{{dep}}" {% if dep==request.args.get('department') %}selected{% endif %}>{{dep}}</option>
                {% endfor %}
            </select>
            <button type="submit" class="btn btn-search">Search</button>
            <a href="{{ url_for('index') }}" class="btn">Reset</a>
        </div>
    </form>

    {# --- Add Employee Form --- #}
    <h2>Add New Employee</h2>
    <form method="POST" action="{{ url_for('add_employee') }}">
        <div class="form-row" style="margin-bottom:11px;">
            <label>Name:</label>
            <input class="input" type="text" name="name" maxlength="100" required value="{{ request.form.get('name','') }}">
            <label>Department:</label>
            <input class="input" type="text" name="department" maxlength="100" required value="{{ request.form.get('department','') }}">
            <label>Email:</label>
            <input class="input" type="email" name="email" maxlength="100" required value="{{ request.form.get('email','') }}">
            <button type="submit" class="btn btn-add">Add</button>
        </div>
    </form>

    {# --- Employee Table --- #}
    <h2>All Employees</h2>
    <table>
        <tr>
            <th>ID</th><th>Name</th><th>Department</th><th>Email</th><th>Actions</th>
        </tr>
        {% for emp in employees %}
        <tr>
            <td>{{emp.id}}</td>
            <td>{{emp.name}}</td>
            <td>{{emp.department}}</td>
            <td>{{emp.email}}</td>
            <td class="actions">
                <a href="{{ url_for('edit_employee', id=emp.id) }}" class="btn btn-edit">Edit</a>
                <a href="{{ url_for('delete_employee', id=emp.id) }}" class="btn btn-delete">Delete</a>
            </td>
        </tr>
        {% endfor %}
        {% if not employees %}
        <tr><td colspan="5" style="text-align:center;color:#aaa;">No employee records found.</td></tr>
        {% endif %}
    </table>
</div>
</body>
</html>

{# --- Edit Employee Page --- #}
{% if edit %}
<div class="container">
    <h2>Edit Employee</h2>
    <form method="POST">
        <div class="form-row" style="margin-bottom:11px;">
            <label>Name:</label>
            <input class="input" type="text" name="name" maxlength="100" required value="{{ emp.name }}">
            <label>Department:</label>
            <input class="input" type="text" name="department" maxlength="100" required value="{{ emp.department }}">
            <label>Email:</label>
            <input class="input" type="email" name="email" maxlength="100" required value="{{ emp.email }}">
            <button type="submit" class="btn btn-add">Update</button>
            <a href="{{ url_for('index') }}" class="btn">Cancel</a>
        </div>
    </form>
</div>
{% endif %}

{# --- Delete Confirmation Page --- #}
{% if delete %}
<div class="container">
    <div class="confirm-box">
        <h2>Delete Employee</h2>
        <p>Are you sure you want to <b>DELETE</b> <code>{{ emp.name }}</code> (<i>{{ emp.email }}</i>)?</p>
        <form method="POST" style="margin:16px 0 0 0;">
            <button type="submit" class="btn btn-delete">Yes, Delete</button>
            <a href="{{ url_for('index') }}" class="btn">Cancel</a>
        </form>
    </div>
</div>
{% endif %}
"""

# --- ROUTES ---

@app.route('/', methods=['GET'])
def index():
    search = request.args.get('search', '').strip()
    dep = request.args.get('department', '').strip()
    query = Employee.query
    # Filter logic
    if search:
        query = query.filter(Employee.name.ilike(f"%{search}%"))
    if dep:
        query = query.filter(Employee.department == dep)
    employees = query.order_by(Employee.id).all()
    # For department dropdown
    departments = [d[0] for d in db.session.query(Employee.department).distinct().all()]
    return render_template_string(
        TEMPLATE, employees=employees, departments=departments, edit=False, delete=False
    )

# --- Add Employee Handler ---
@app.route('/add', methods=['POST'])
def add_employee():
    name = request.form.get('name', '').strip()
    department = request.form.get('department', '').strip()
    email = request.form.get('email', '').strip()

    # Input validation
    if not name or not department or not email:
        flash("All fields are required!", "error")
    elif len(name) > 100 or len(department) > 100 or len(email) > 100:
        flash("Input exceeds maximum allowed length.", "error")
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Please enter a valid email address.", "error")
    elif Employee.query.filter_by(email=email).first():
        flash("An employee with this email already exists.", "error")
    else:
        new_emp = Employee(name=name, department=department, email=email)
        db.session.add(new_emp)
        db.session.commit()
        flash(f"Employee '{name}' added successfully.", "success")
        return redirect(url_for('index'))

    # On error, keep form state and show message
    return index()

# --- Edit/Update Handler ---
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    emp = db.get_or_404(Employee, id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        department = request.form.get('department', '').strip()
        email = request.form.get('email', '').strip()
        # Validation
        if not name or not department or not email:
            flash("All fields are required!", "error")
        elif len(name) > 100 or len(department) > 100 or len(email) > 100:
            flash("Input exceeds maximum allowed length.", "error")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address.", "error")
        elif Employee.query.filter(Employee.email==email, Employee.id!=id).first():
            flash("Another employee already has this email.", "error")
        else:
            emp.name = name
            emp.department = department
            emp.email = email
            db.session.commit()
            flash("Employee updated successfully.", "success")
            return redirect(url_for('index'))
        # on validation fail
    departments = [d[0] for d in db.session.query(Employee.department).distinct().all()]
    employees = Employee.query.order_by(Employee.id).all()
    return render_template_string(
        TEMPLATE, employees=employees, departments=departments, emp=emp, edit=True, delete=False
    )

# --- Delete Confirmation Page & Handler ---
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_employee(id):
    emp = db.get_or_404(Employee, id)
    if request.method == 'POST':
        db.session.delete(emp)
        db.session.commit()
        flash(f"Employee '{emp.name}' deleted.", "success")
        return redirect(url_for('index'))
    departments = [d[0] for d in db.session.query(Employee.department).distinct().all()]
    employees = Employee.query.order_by(Employee.id).all()
    return render_template_string(
        TEMPLATE, employees=employees, departments=departments, emp=emp, edit=False, delete=True
    )

# --- Initialize DB & Run App ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)