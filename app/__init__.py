from flask import Flask
from app.extensions import db, migrate
from app.routes import main_bp
from app.oauth_routes import oauth_bp

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="your-secret-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///database.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(oauth_bp, url_prefix="/auth")

    return app
