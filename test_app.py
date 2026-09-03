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
        'email': 'john@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'John Doe' in response.data

def test_add_employee_duplicate_email(client):
    client.post('/add', data={
        'name': 'First',
        'department': 'Engineering',
        'email': 'dup@example.com'
    }, follow_redirects=True)

    response = client.post('/add', data={
        'name': 'Second',
        'department': 'Engineering',
        'email': 'dup@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'An employee with this email already exists.' in response.data

    with app.app_context():
        assert Employee.query.filter_by(email='dup@example.com').count() == 1

def test_search_employee(client):
    client.post('/add', data={
        'name': 'Alice Smith',
        'department': 'HR',
        'email': 'alice@example.com'
    }, follow_redirects=True)
    
    response = client.get('/?search=Alice')
    assert response.status_code == 200
    assert b'Alice Smith' in response.data

def test_delete_employee(client):
    client.post('/add', data={
        'name': 'Bob Ross',
        'department': 'Design',
        'email': 'bob@example.com'
    }, follow_redirects=True)
    
    with app.app_context():
        emp = Employee.query.filter_by(name='Bob Ross').first()
        emp_id = emp.id
        
    response = client.post(f'/delete/{emp_id}', follow_redirects=True)
    assert response.status_code == 200
    assert b'<td>Bob Ross</td>' not in response.data
    
    with app.app_context():
        assert db.session.get(Employee, emp_id) is None