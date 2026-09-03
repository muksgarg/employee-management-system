import pytest
from app import app, db, Employee

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}

def test_add_employee(client):
    response = client.post('/add', data={
        'name': 'John Doe',
        'department': 'Engineering',
        'email': 'john@example.com',
        'salary': '50000'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'John Doe' in response.data
    assert b'50000' in response.data

    with app.app_context():
        emp = Employee.query.filter_by(email='john@example.com').first()
        assert emp.salary == 50000.0

def test_add_employee_missing_salary(client):
    response = client.post('/add', data={
        'name': 'Jane Doe',
        'department': 'Engineering',
        'email': 'jane@example.com',
        'salary': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'All fields are required!' in response.data

    with app.app_context():
        assert Employee.query.filter_by(email='jane@example.com').first() is None

def test_add_employee_negative_salary(client):
    response = client.post('/add', data={
        'name': 'Neg Salary',
        'department': 'Engineering',
        'email': 'neg@example.com',
        'salary': '-100'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please enter a valid, non-negative salary.' in response.data

    with app.app_context():
        assert Employee.query.filter_by(email='neg@example.com').first() is None

def test_add_employee_invalid_salary(client):
    response = client.post('/add', data={
        'name': 'Bad Salary',
        'department': 'Engineering',
        'email': 'bad@example.com',
        'salary': 'not-a-number'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please enter a valid, non-negative salary.' in response.data

    with app.app_context():
        assert Employee.query.filter_by(email='bad@example.com').first() is None

def test_add_employee_zero_salary(client):
    response = client.post('/add', data={
        'name': 'Zero Salary',
        'department': 'Engineering',
        'email': 'zero@example.com',
        'salary': '0'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please enter a valid, non-negative salary.' not in response.data

    with app.app_context():
        emp = Employee.query.filter_by(email='zero@example.com').first()
        assert emp is not None
        assert emp.salary == 0.0

def test_add_employee_duplicate_email(client):
    client.post('/add', data={
        'name': 'First',
        'department': 'Engineering',
        'email': 'dup@example.com',
        'salary': '10000'
    }, follow_redirects=True)

    response = client.post('/add', data={
        'name': 'Second',
        'department': 'Engineering',
        'email': 'dup@example.com',
        'salary': '20000'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'An employee with this email already exists.' in response.data

    with app.app_context():
        assert Employee.query.filter_by(email='dup@example.com').count() == 1

def test_edit_employee_salary(client):
    client.post('/add', data={
        'name': 'Edit Me',
        'department': 'HR',
        'email': 'editme@example.com',
        'salary': '40000'
    }, follow_redirects=True)

    with app.app_context():
        emp = Employee.query.filter_by(email='editme@example.com').first()
        emp_id = emp.id

    response = client.post(f'/edit/{emp_id}', data={
        'name': 'Edit Me',
        'department': 'HR',
        'email': 'editme@example.com',
        'salary': '60000'
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        updated = db.session.get(Employee, emp_id)
        assert updated.salary == 60000.0

def test_edit_employee_negative_salary(client):
    client.post('/add', data={
        'name': 'Edit Neg',
        'department': 'HR',
        'email': 'editneg@example.com',
        'salary': '40000'
    }, follow_redirects=True)

    with app.app_context():
        emp_id = Employee.query.filter_by(email='editneg@example.com').first().id

    response = client.post(f'/edit/{emp_id}', data={
        'name': 'Edit Neg',
        'department': 'HR',
        'email': 'editneg@example.com',
        'salary': '-500'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please enter a valid, non-negative salary.' in response.data

    with app.app_context():
        assert db.session.get(Employee, emp_id).salary == 40000.0

def test_edit_employee_invalid_salary(client):
    client.post('/add', data={
        'name': 'Edit Bad',
        'department': 'HR',
        'email': 'editbad@example.com',
        'salary': '40000'
    }, follow_redirects=True)

    with app.app_context():
        emp_id = Employee.query.filter_by(email='editbad@example.com').first().id

    response = client.post(f'/edit/{emp_id}', data={
        'name': 'Edit Bad',
        'department': 'HR',
        'email': 'editbad@example.com',
        'salary': 'nope'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please enter a valid, non-negative salary.' in response.data

    with app.app_context():
        assert db.session.get(Employee, emp_id).salary == 40000.0

def test_search_employee(client):
    client.post('/add', data={
        'name': 'Alice Smith',
        'department': 'HR',
        'email': 'alice@example.com',
        'salary': '45000'
    }, follow_redirects=True)
    
    response = client.get('/?search=Alice')
    assert response.status_code == 200
    assert b'Alice Smith' in response.data

def test_delete_employee(client):
    client.post('/add', data={
        'name': 'Bob Ross',
        'department': 'Design',
        'email': 'bob@example.com',
        'salary': '55000'
    }, follow_redirects=True)
    
    with app.app_context():
        emp = Employee.query.filter_by(name='Bob Ross').first()
        emp_id = emp.id
        
    response = client.post(f'/delete/{emp_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'<td>Bob Ross</td>' not in response.data
    
    with app.app_context():
        assert db.session.get(Employee, emp_id) is None