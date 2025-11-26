import os
import logging
from dotenv import load_dotenv
import pathlib
from sqlalchemy import text
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# FIXED IMPORT PATHS
from app.extensions import db, migrate


# Set up logging
logging.basicConfig(level=logging.DEBUG)

def create_app():
    # Create the app
    app = Flask(__name__)

    # Load `.env` from repo root
    try:
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        dotenv_path = repo_root / '.env'
        if dotenv_path.exists():
            load_dotenv(dotenv_path=str(dotenv_path))
            app.logger.debug(f"Loaded environment variables from {dotenv_path}")
    except Exception:
        pass

    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Database Config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///internship_matching.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Feature flag
    try:
        app.config['MATCH_COMPLETENESS_THRESHOLD'] = int(os.environ.get('MATCH_COMPLETENESS_THRESHOLD', 70))
    except Exception:
        app.config['MATCH_COMPLETENESS_THRESHOLD'] = 70

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # FIXED IMPORT (must happen after db.init_app)
    from app.models import Student, Department, Admin, Internship, Match, Application

    # Blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.oauth_routes import oauth_bp
    app.register_blueprint(oauth_bp)

    # Auto table creation for dev (not prod)
    with app.app_context():
        db.create_all()

        try:
            inspector = db.engine
            if inspector.dialect.name == 'sqlite':
                with db.engine.connect() as conn:
                    res = conn.execute(text("PRAGMA table_info('applications')"))
                    existing_cols = [row[1] for row in res.fetchall()]

                expected = {
                    'department_notes': 'TEXT',
                    'interview_date': 'DATETIME',
                    'response_date': 'DATETIME'
                }

                for col, col_type in expected.items():
                    if col not in existing_cols:
                        try:
                            with db.engine.begin() as conn:
                                conn.execute(text(f"ALTER TABLE applications ADD COLUMN {col} {col_type}"))
                            app.logger.info(f"Added missing column '{col}' to applications table")
                        except Exception as alter_e:
                            app.logger.error(f"Failed to add column {col}: {alter_e}")
        except Exception as check_e:
            app.logger.debug(f"DB schema check skipped: {check_e}")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
