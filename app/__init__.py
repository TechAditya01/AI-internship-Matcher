import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Extensions are in app/extensions.py
from app.extensions import db, migrate

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

    app = Flask(__name__, template_folder="templates")
>>>>>>> 9b96774 (updated code)
=======
def create_app():
    app = Flask(__name__, template_folder="templates")
=======
    app = Flask(__name__, template_folder="templates")
>>>>>>> 9b96774 (updated code)

    # load .env from repo root if present
    try:
        repo_root = Path(__file__).resolve().parents[1]
        dotenv_path = repo_root / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path)
            app.logger.info(f"Loaded environment from {dotenv_path}")
        else:
            app.logger.info(".env not found; using environment variables")
    except Exception as e:
        app.logger.warning(f"Failed to load .env: {e}")

    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # SQLAlchemy config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///internship_matching.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 300, "pool_pre_ping": True}

    # feature flags
    try:
        app.config["MATCH_COMPLETENESS_THRESHOLD"] = int(os.environ.get("MATCH_COMPLETENESS_THRESHOLD", 70))
    except Exception:
        app.config["MATCH_COMPLETENESS_THRESHOLD"] = 70

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # import models AFTER db.init_app to avoid circular import problems
    try:
        from app import models  # registers models with SQLAlchemy
    except Exception as e:
        app.logger.warning(f"Couldn't import models: {e}")

    # register blueprints (import after app created)
    from app import routes as routes_mod
    from app import oauth_routes as oauth_routes_mod

    # routes.py defines `bp` and oauth_routes.py defines `oauth_bp`
    app.register_blueprint(routes_mod.bp)
    app.register_blueprint(oauth_routes_mod.oauth_bp)

    # Create tables automatically (development convenience)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"db.create_all() failed: {e}")

    return app
