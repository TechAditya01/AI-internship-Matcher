from flask import Blueprint, redirect, request, session, flash, url_for, current_app
from app.oauth import get_authorization_url, exchange_code_for_token, get_google_user_info
import logging

oauth_bp = Blueprint("oauth", __name__)
LOG = logging.getLogger(__name__)

@oauth_bp.route("/auth/google")
def auth_google():
    """
    Start Google OAuth flow. The frontend should hit this route (or you can
    link to it as /auth/google?type=student).
    """
    auth_url = get_authorization_url()
    if not auth_url:
        flash("Google OAuth is not configured on this server.", "error")
        LOG.error("Google OAuth not configured")
        return redirect(url_for("routes.index") if "routes" in current_app.blueprints else "/")
    return redirect(auth_url)

@oauth_bp.route("/oauth2callback")
def oauth2callback():
    """
    Callback used by Google to return the authorization code.
    We exchange code -> token -> userinfo and save essential session details.
    """
    code = request.args.get("code")
    state = request.args.get("state")
    if not code:
        flash("No authorization code returned.", "error")
        LOG.error("No auth code in callback.")
        return redirect(url_for("routes.index") if "routes" in current_app.blueprints else "/")

    token_data = exchange_code_for_token(code)
    if not token_data or "access_token" not in token_data:
        flash("Failed to exchange code for token.", "error")
        LOG.error(f"Token exchange failed: {token_data}")
        return redirect(url_for("routes.index") if "routes" in current_app.blueprints else "/")

    user_info = get_google_user_info(token_data["access_token"])
    if not user_info:
        flash("Failed to fetch user info from Google.", "error")
        return redirect(url_for("routes.index") if "routes" in current_app.blueprints else "/")

    # Minimal session storage — expand as needed
    session_user_type = request.args.get("type", "student")
    session["oauth_user_type"] = session_user_type
    session["user_info"] = {
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "google_id": user_info.get("id"),
        "picture": user_info.get("picture")
    }

    flash(f"Authenticated as {user_info.get('email')}", "success")
    return redirect(url_for("routes.index"))
