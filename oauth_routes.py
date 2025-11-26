import os
from flask import Blueprint, request, redirect, session, url_for
from google_oauth import create_google_flow, get_google_user_info, handle_google_login


oauth_bp = Blueprint('oauth', __name__)

@oauth_bp.route("/auth/google")
def google_login():
    user_type = request.args.get('type', 'student')

    flow = create_google_flow()
    if not flow:
        return "Google OAuth is not configured. Contact admin.", 500

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes=True,
        prompt="consent"
    )

    session["oauth_state"] = state
    session["user_type"] = user_type
    return redirect(auth_url)


@oauth_bp.route("/auth/google/callback")
def google_callback():
    flow = create_google_flow()
    if not flow:
        return "OAuth not configured", 500

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    user_info = get_google_user_info(credentials.token)
    success, user = handle_google_login(user_info, session.get("user_type", "student"))

    if not success:
        return "Authentication failed", 401

    session["user_id"] = user.id
    session["logged_in"] = True

    return redirect("/")
