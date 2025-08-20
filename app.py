from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, User
from controllers.login_controller import login_bp
from controllers.crud_controller import crud_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SECRET_KEY"] = "your_secret_key_here"
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(login_bp)
app.register_blueprint(crud_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)