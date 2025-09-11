import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import Flask
from models import db, User
from flask_login import LoginManager
from controllers.login_controller import login_bp
from controllers.project_controller import project_bp
from controllers.crud_controller import crud_bp
from controllers.task_controller import task_bp

def create_test_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SECRET_KEY"] = "test"
    app.config["WTF_CSRF_ENABLED"] = False

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "login.login"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # 🔹 Register all blueprints (not just login_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(crud_bp)
    app.register_blueprint(task_bp)

    return app

@pytest.fixture
def client():
    app = create_test_app()
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_register_login_logout(client):
    # Register
    response = client.post("/register", data={"username": "testuser", "password": "testpass"}, follow_redirects=True)
    assert b"Registration successful" in response.data

    # Login
    response = client.post("/login", data={"username": "testuser", "password": "testpass"}, follow_redirects=True)
    # Adjust this assertion if needed depending on what the post-login page shows
    assert b"Dashboard" in response.data or b"Projects" in response.data or b"Login" not in response.data

    # Logout
    response = client.get("/logout", follow_redirects=True)
    assert b"Login" in response.data