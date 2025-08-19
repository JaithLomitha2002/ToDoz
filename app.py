from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ToDo

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SECRET_KEY"] = "your_secret_key_here"
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

def __repr__(self):
    return "<Task %r>" % self.id
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for("register"))
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/", methods=["GET"])
@login_required
def home():
    tasks = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.date.desc()).all()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
@login_required
def add():
    content = request.form["content"]
    new_task = ToDo(content=content, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    task = ToDo.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash("You got no permission to delete this task.")
        return redirect(url_for("home"))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    task = ToDo.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash("You got no permission to edit this task.")
        return redirect(url_for("home"))
    if request.method == "POST":
        task.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", task=task)

if __name__ == "__main__":
    app.run(debug=True)
