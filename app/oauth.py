import os
import logging
import requests

LOG = logging.getLogger(__name__)

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# Make sure your Render redirect URI matches this (or set OAUTH_REDIRECT_URI env var)
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://127.0.0.1:5000/oauth2callback")

SCOPES = "openid email profile"

def create_google_flow_stub():
    """
    Backwards-compatible fallback for code paths that expect a 'flow' with
    authorization_url() and fetch_token(). In your routes we handle lazy imports,
    so this helper may not be required — but included for dev safety.
    """
    raise RuntimeError("Use the functions below: get_authorization_url(), exchange_code_for_token(), get_google_user_info()")

def get_authorization_url():
    if not CLIENT_ID:
        LOG.debug("GOOGLE_CLIENT_ID not configured")
        return None
    # Google OAuth2 endpoint for user consent
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        f"&scope={SCOPES}"
        "&access_type=offline"
        "&prompt=select_account"
    )
    return url

def exchange_code_for_token(code):
    if not CLIENT_ID or not CLIENT_SECRET:
        LOG.debug("Google client id/secret not configured")
        return None
    try:
        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        LOG.error(f"Token exchange failed: {e}")
        return None

def get_google_user_info(access_token):
    try:
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"alt": "json"},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        LOG.error(f"Failed to fetch google user info: {e}")
        return None
