from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, ToDo
from datetime import datetime

crud_bp = Blueprint("crud", __name__)

@crud_bp.route("/", methods=["GET"])
@login_required
def home():
    tasks = ToDo.query.filter_by(user_id=current_user.id).order_by(ToDo.date.desc()).all()
    return render_template("index.html", tasks=tasks)

@crud_bp.route("/add", methods=["POST"])
@login_required
def add():
    content = request.form["content"]
    new_task = ToDo(content=content, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("crud.home"))

@crud_bp.route("/delete/<int:id>")
@login_required
def delete(id):
    task = ToDo.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash("You got no permission to delete this task.")
        return redirect(url_for("crud.home"))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("crud.home"))

@crud_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    task = ToDo.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash("You got no permission to edit this task.")
        return redirect(url_for("crud.home"))
    if request.method == "POST":
        task.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("crud.home"))
    return render_template("edit.html", task=task)