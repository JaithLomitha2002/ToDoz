from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Project, Task, TaskAssignee, ProjectMember, User
from datetime import datetime

task_bp = Blueprint("task", __name__)

@task_bp.route("/project/<int:project_id>/task/create", methods=["POST"])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    if project.manager_id != current_user.id:
        return jsonify({"error": "Only manager can create tasks"}), 403
    name = request.form["name"]
    end_date = request.form.get("end_date")
    priority = request.form.get("priority", "medium")
    task = Task(
        project_id=project_id,
        name=name,
        end_date=datetime.strptime(end_date, "%Y-%m-%d") if end_date else None,
        priority=priority,
        creator_id=current_user.id
    )
    db.session.add(task)
    db.session.commit()
    return redirect(url_for("project.project_detail", project_id=project_id))

@task_bp.route("/task/<int:task_id>/assign", methods=["POST"])
@login_required
def assign_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project
    if project.manager_id != current_user.id:
        return jsonify({"error": "Only manager can assign"}), 403
    username = request.form["username"]
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    # Only members can be assigned
    pm = ProjectMember.query.filter_by(project_id=project.id, user_id=user.id, status="accepted").first()
    if not pm:
        return jsonify({"error": "User not a project member"}), 400
    existing = TaskAssignee.query.filter_by(task_id=task_id, user_id=user.id).first()
    if existing:
        return jsonify({"error": "Already assigned"}), 400
    ta = TaskAssignee(task_id=task_id, user_id=user.id)
    db.session.add(ta)
    db.session.commit()
    return redirect(url_for("project.project_detail", project_id=project.id))

@task_bp.route("/task/<int:task_id>/remove_assignee/<int:user_id>", methods=["POST"])
@login_required
def remove_assignee(task_id, user_id):
    task = Task.query.get_or_404(task_id)
    project = task.project
    if project.manager_id != current_user.id:
        return jsonify({"error": "Only manager can remove assignees"}), 403
    ta = TaskAssignee.query.filter_by(task_id=task_id, user_id=user_id).first()
    if ta:
        db.session.delete(ta)
        db.session.commit()
    return redirect(url_for("project.project_detail", project_id=project.id))

@task_bp.route("/task/<int:task_id>/update_progress", methods=["POST"])
@login_required
def update_progress(task_id):
    task = Task.query.get_or_404(task_id)
    # Only assigned members can update progress
    ta = TaskAssignee.query.filter_by(task_id=task_id, user_id=current_user.id).first()
    if not ta:
        return jsonify({"error": "Not assigned"}), 403
    progress = int(request.form["progress"])
    task.progress = max(0, min(100, progress))
    db.session.commit()
    return redirect(url_for("project.project_detail", project_id=task.project_id))

@task_bp.route("/task/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project
    if project.manager_id != current_user.id:
        return jsonify({"error": "Only manager can delete"}), 403
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("project.project_detail", project_id=project.id))