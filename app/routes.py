from flask import (
    Blueprint, render_template, session, redirect, url_for,
    request, flash, jsonify
)
from .models import db, Internship, Application
from .matching_engine import match_internships
from .oauth_routes import oauth_login, oauth_callback
import logging

bp = Blueprint("routes", __name__, template_folder="../templates")
LOG = logging.getLogger(__name__)

# -------------------------------
# Home Page
# -------------------------------
@bp.route("/")
def index():
    user = session.get("user_info")
    return render_template("index.html", user=user)


# -------------------------------
# Google OAuth Entry Route
# -------------------------------
@bp.route("/auth/google")
def google_auth():
    user_type = request.args.get("type")
    session["pending_role"] = user_type
    return oauth_login()


@bp.route("/auth/google/callback")
def google_auth_callback():
    return oauth_callback()


# -------------------------------
# Dashboard
# -------------------------------
@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("routes.index"))

    user = User.query.get(session["user_id"])

    if user.role == "student":
        internships = Internship.query.all()
        return render_template("student_dashboard.html", user=user, internships=internships)

    if user.role == "department":
        internships = Internship.query.filter_by(department_id=user.id).all()
        return render_template("department_dashboard.html", user=user, internships=internships)

    if user.role == "admin":
        users = User.query.all()
        internships = Internship.query.all()
        return render_template("admin_dashboard.html", user=user, users=users, internships=internships)

    return "Invalid Role", 400


# -------------------------------
# Create Internship (Department)
# -------------------------------
@bp.route("/internship/create", methods=["POST"])
def create_internship():
    if session.get("role") != "department":
        return jsonify({"error": "Unauthorized"}), 403

    title = request.form.get("title")
    description = request.form.get("description")
    skills = request.form.get("skills")

    internship = Internship(
        title=title,
        description=description,
        skills=skills,
        department_id=session["user_id"]
    )

    db.session.add(internship)
    db.session.commit()

    flash("Internship posted successfully!", "success")
    return redirect(url_for("routes.dashboard"))


# -------------------------------
# Apply for Internship (Student)
# -------------------------------
@bp.route("/internship/<int:id>/apply")
def apply_internship(id):
    if session.get("role") != "student":
        return jsonify({"error": "Unauthorized"}), 403

    existing = Application.query.filter_by(
        internship_id=id, student_id=session["user_id"]
    ).first()

    if existing:
        flash("You already applied!", "info")
        return redirect(url_for("routes.dashboard"))

    application = Application(
        internship_id=id,
        student_id=session["user_id"],
        status="Pending"
    )

    db.session.add(application)
    db.session.commit()

    flash("Application submitted!", "success")
    return redirect(url_for("routes.dashboard"))


# -------------------------------
# Admin: Approve / Reject User
# -------------------------------
@bp.route("/admin/approve/<int:user_id>")
def approve_user(user_id):
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    user.approved = True
    db.session.commit()

    flash("User approved!", "success")
    return redirect(url_for("routes.dashboard"))


@bp.route("/admin/reject/<int:user_id>")
def reject_user(user_id):
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()

    flash("User removed!", "warning")
    return redirect(url_for("routes.dashboard"))


# -------------------------------
# Student: Update Profile → AI Matching Trigger
# -------------------------------
@bp.route("/update-profile", methods=["POST"])
def update_profile():
    if session.get("role") != "student":
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(session["user_id"])
    user.skills = request.form.get("skills")
    user.department_interest = request.form.get("department_interest")
    db.session.commit()

    match_internships(user)  # AI MATCHING ENGINE CALL

    flash("Profile updated & recommendations refreshed!", "success")
    return redirect(url_for("routes.dashboard"))


# -------------------------------
# Logout
# -------------------------------
@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.index"))


# -------------------------------
# Health Check (Render Deployment Needs This)
# -------------------------------
@bp.route("/health")
def health():
    return "OK", 200
