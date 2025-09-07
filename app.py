from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, User
from controllers.login_controller import login_bp
from controllers.crud_controller import crud_bp
from controllers.project_controller import project_bp
from controllers.task_controller import task_bp
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///test.db")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your_secret_key_here")
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login.login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app.register_blueprint(login_bp)
app.register_blueprint(crud_bp)
app.register_blueprint(project_bp)
app.register_blueprint(task_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)