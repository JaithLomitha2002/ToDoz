from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Project, ProjectMember, User, Task, TaskAssignee
from datetime import datetime

project_bp = Blueprint("project", __name__)

@project_bp.route("/")
def home_redirect():
    return redirect(url_for("project.projects"))

@project_bp.route("/invitations")
@login_required
def invitations():
    invitations = ProjectMember.query.filter_by(user_id=current_user.id).filter(ProjectMember.status.in_(["pending", "rejected"])).all()
    return render_template("invitations.html", invitations=invitations)

@project_bp.route("/projects")
@login_required
def projects():
    # Show projects where user is manager or member
    managed = Project.query.filter_by(manager_id=current_user.id).all()
    member_projects = [pm.project for pm in ProjectMember.query.filter_by(user_id=current_user.id, status="accepted").all()]
    return render_template("projects.html", managed=managed, member_projects=member_projects)

@project_bp.route("/project/create", methods=["POST"])
@login_required
def create_project():
    name = request.form["name"]
    project = Project(name=name, manager_id=current_user.id)
    db.session.add(project)
    db.session.commit()
    # Add manager as accepted member
    pm = ProjectMember(project_id=project.id, user_id=current_user.id, status="accepted")
    db.session.add(pm)
    db.session.commit()
    return redirect(url_for("project.projects"))

@project_bp.route("/project/<int:project_id>")
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    # Access control: only members/managers can view
    pm = ProjectMember.query.filter_by(project_id=project_id, user_id=current_user.id, status="accepted").first()
    if not pm and project.manager_id != current_user.id:
        flash("Access denied.")
        return redirect(url_for("project.projects"))
    invitations = ProjectMember.query.filter_by(project_id=project_id, status="pending").all()
    return render_template("project_detail.html", project=project, invitations=invitations)

@project_bp.route("/project/<int:project_id>/invite", methods=["POST"])
@login_required
def invite_member(project_id):
    project = Project.query.get_or_404(project_id)
    if project.manager_id != current_user.id:
        return jsonify({"error": "Only manager can invite"}), 403
    username = request.form["username"]
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    # Prevent duplicate invitations
    existing = ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first()
    if existing:
        return jsonify({"error": "Already invited or member"}), 400
    pm = ProjectMember(project_id=project_id, user_id=user.id, status="pending")
    db.session.add(pm)
    db.session.commit()
    return redirect(url_for("project.project_detail", project_id=project_id))

@project_bp.route("/project/invitation/<int:inv_id>/<action>", methods=["POST"])
@login_required
def handle_invitation(inv_id, action):
    pm = ProjectMember.query.get_or_404(inv_id)
    if pm.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    if action == "accept":
        pm.status = "accepted"
    elif action == "reject":
        pm.status = "rejected"
    db.session.commit()
    return redirect(url_for("project.projects"))