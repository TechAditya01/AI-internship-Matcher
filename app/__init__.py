from flask import Flask
from app.routes import main_bp
from app.oauth_routes import oauth_bp
from app.database import init_db

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your-secret-key"

    init_db(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(oauth_bp)

    return app
