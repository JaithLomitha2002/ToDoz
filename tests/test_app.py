import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import User
import pytest

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
        yield client

def test_register_login_logout(client):
    # Register
    response = client.post("/register", data={"username": "testuser", "password": "testpass"}, follow_redirects=True)
    assert b"Registration successful" in response.data

    # Login
    response = client.post("/login", data={"username": "testuser", "password": "testpass"}, follow_redirects=True)
    assert b"Your Projects" in response.data

    # Logout
    response = client.get("/logout", follow_redirects=True)
    assert b"Login" in response.data