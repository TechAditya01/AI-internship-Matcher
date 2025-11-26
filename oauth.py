import os
import logging


def create_google_flow():
    """Create and return a google_auth_oauthlib.flow.Flow configured from env vars.

    Returns None if dependencies or configuration are missing.
    """
    try:
        import importlib
        module = importlib.import_module('google_auth_oauthlib.flow')
        Flow = getattr(module, 'Flow')
    except Exception as e:
        logging.debug(f"Google oauth library missing: {e}")
        return None

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.getenv('OAUTH_REDIRECT_URI', 'http://127.0.0.1:5000/oauth2callback')

    if not client_id or not client_secret:
        logging.debug("Google client id/secret not configured in environment")
        return None

    # Allow insecure transport for local development when redirect URI is localhost
    try:
        if redirect_uri.startswith('http://127.0.0.1') or redirect_uri.startswith('http://localhost'):
            os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')
            logging.debug('Set OAUTHLIB_INSECURE_TRANSPORT=1 for local development')
    except Exception:
        pass

    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ]
        )
        flow.redirect_uri = redirect_uri
        return flow
    except Exception as e:
        logging.error(f"Failed to create Google OAuth flow: {e}")
        return None


def get_google_user_info(access_token):
    """Fetch user info from Google using an access token. Returns dict or None."""
    try:
        import requests
        headers = {'Authorization': f'Bearer {access_token}'}
        resp = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', params={'alt': 'json'}, headers=headers, timeout=5)
        if resp.ok:
            return resp.json()
        logging.error(f"Failed to fetch Google user info: {resp.status_code} {resp.text}")
    except Exception as e:
        logging.error(f"Error requesting Google user info: {e}")
    return None


def handle_google_login(user_info, user_type='student'):
    """Create or lookup a user (Student) from Google user_info.

    Returns (success: bool, user_obj or None)
    """
    try:
        from extensions import db
        from models import Student, Department
    except Exception as e:
        logging.error(f"DB/models import failed in oauth handler: {e}")
        return False, None

    if not user_info or 'email' not in user_info:
        logging.error("Google user info missing email")
        return False, None

    email = user_info.get('email')
    google_id = user_info.get('id')
    name = user_info.get('name') or email.split('@')[0]
    picture = user_info.get('picture')

    try:
        if user_type == 'student':
            user = None
            if google_id:
                user = Student.query.filter_by(google_id=google_id).first()
            if not user:
                user = Student.query.filter_by(email=email).first()

            if user:
                # Update google fields if missing
                updated = False
                if not user.google_id and google_id:
                    user.google_id = google_id
                    updated = True
                if picture and not user.profile_picture:
                    user.profile_picture = picture
                    updated = True
                if updated:
                    db.session.commit()
                return True, user

            # Create new student
            new_user = Student(
                email=email,
                name=name,
                google_id=google_id,
                profile_picture=picture
            )
            db.session.add(new_user)
            db.session.commit()
            return True, new_user

        # For departments we currently do not support Google sign-up via UI
        if user_type == 'department':
            return False, None

    except Exception as e:
        logging.error(f"Error creating/finding user from Google info: {e}")
        try:
            db.session.rollback()
        except Exception:
            pass

    return False, None
