from flask import Blueprint, render_template, session, redirect, url_for, flash
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


@bp.route("/health")
def health():
    """Health check route for deployment monitoring."""
    return "OK"
