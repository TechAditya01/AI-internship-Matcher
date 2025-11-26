from flask import Blueprint, render_template, session, redirect, url_for
import logging

bp = Blueprint("routes", __name__, template_folder="../templates")
LOG = logging.getLogger(__name__)

@bp.route("/")
def index():
    """Home page route."""
    user = session.get("user_info")  # Comes from OAuth login
    return render_template("index.html", user=user)

@bp.route("/logout")
def logout():
    """Logs out user and clears session."""
    session.clear()
    LOG.info("User logged out.")
    return redirect(url_for("routes.index"))

@bp.route("/health")
def health():
    """Simple health check route."""
    return "OK"
