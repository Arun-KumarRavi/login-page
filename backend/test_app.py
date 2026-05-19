import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_missing_creds(client):
    response = client.post('/api/login', json={"username": "test"})
    assert response.status_code == 400

def test_login_invalid_creds(client):
    response = client.post('/api/login', json={"username": "wrong", "password": "user"})
    assert response.status_code == 401
