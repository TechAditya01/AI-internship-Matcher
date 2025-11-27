from flask import Blueprint, render_template, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from .database import get_user_by_email
from .database import save_user
import logging

bp = Blueprint("routes", __name__, template_folder="../templates")

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@bp.route("/")
def index():
    """Home page route."""
    user = session.get("user_info")  # Stored after successful OAuth
    LOG.info(f"Rendering home page. User logged in: {bool(user)}")
    
    try:
        return render_template("index.html", user=user)
    except Exception as e:
        LOG.error(f"Template render failed: {e}")
        return "<h2>Error: index.html missing or failed to render.</h2>"


@bp.route("/logout")
def logout():
    """Logs out the user and removes session tokens."""
    if session.get("user_info"):
        LOG.info(f"Logging out user: {session['user_info'].get('email')}")
        flash("You have been logged out.", "info")
    else:
        LOG.info("Logout request but no active session.")

    session.clear()
    return redirect(url_for("routes.index"))

@routes.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user_type = request.form.get("user_type")

    user = get_user_by_email(email)

    if user and check_password_hash(user.password, password):
        session["user"] = user.email
        session["user_type"] = user_type
        flash("Login successful!", "success")
        return redirect(url_for("routes.dashboard"))  # adjust if needed
    else:
        flash("Invalid credentials", "danger")
        return redirect(url_for("routes.home"))


@bp.route("/health")
def health():
    """Health check route for deployment monitoring."""
    return "OK"
