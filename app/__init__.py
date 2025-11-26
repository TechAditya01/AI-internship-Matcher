import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import text
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Correct imports
from app.extensions import db, migrate

# Logger setup
logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)

    # -------- Load Environment Variables --------
    try:
        repo_root = Path(__file__).resolve().parents[1]
        dotenv_path = repo_root / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path)
            app.logger.info(f"Loaded environment variables from: {dotenv_path}")
        else:
            app.logger.warning(".env file not found — using system environment variables.")
    except Exception as e:
        app.logger.error(f"Failed loading .env file: {e}")

    # -------- App Security --------
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

    # Fix reverse proxy issues when hosted
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # -------- Database Config --------
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///internship_matching.db"
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # -------- Feature Flag --------
    app.config["MATCH_COMPLETENESS_THRESHOLD"] = int(
        os.environ.get("MATCH_COMPLETENESS_THRESHOLD", 70)
    )

    # -------- Initialize Extensions --------
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models AFTER db initialization to avoid circular imports
    from app.models import Student, Department, Admin, Internship, Match, Application

    # -------- Register Blueprints --------
    from app.routes import bp as main_bp
    from app.oauth_routes import oauth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(oauth_bp)

    # -------- Automatic DB Fixing (DEV Only) --------
    with app.app_context():
        db.create_all()

        if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
            try:
                with db.engine.connect() as conn:
                    res = conn.execute(text("PRAGMA table_info('applications')"))
                    existing_cols = [row[1] for row in res]

                required_columns = {
                    "department_notes": "TEXT",
                    "interview_date": "DATETIME",
                    "response_date": "DATETIME"
                }

                for col, col_type in required_columns.items():
                    if col not in existing_cols:
                        try:
                            with db.engine.begin() as conn:
                                conn.execute(text(f"ALTER TABLE applications ADD COLUMN {col} {col_type}"))
                            app.logger.info(f"Added missing column: {col}")
                        except Exception as err:
                            app.logger.error(f"Failed to add column {col}: {err}")

            except Exception as err:
                app.logger.warning(f"Skipping SQLite schema patch: {err}")

    return app


# ------------------------------------------------------
# Allow local development execution
# ------------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
