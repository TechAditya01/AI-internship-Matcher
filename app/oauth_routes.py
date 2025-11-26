from flask import Blueprint

oauth_bp = Blueprint("oauth", __name__)

@oauth_bp.route("/oauth")
def oauth_home():
    return "OAuth blueprint is working!"
