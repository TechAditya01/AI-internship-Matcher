import os
import logging
from dotenv import load_dotenv
import pathlib
from sqlalchemy import text
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.extensions import db, migrate


logging.basicConfig(level=logging.DEBUG)


def create_app():
    app = Flask(__name__)

    # Load .env from project root
    try:
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        dotenv_path = repo_root / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path=str(dotenv_path))
            app.logger.debug(f"Loaded .env from: {dotenv_path}")
    except Exception:
        app.logger.warning("Failed to load .env (ignored).")

    # Secret Key
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

    # Reverse Proxy Support (fixes HTTPS redirect issues on production)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Database Config
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///internship_matching.db"
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Feature flag
    app.config["MATCH_COMPLETENESS_THRESHOLD"] = int(
        os.getenv("MATCH_COMPLETENESS_THRESHOLD", 70)
    )

    # Import all models BEFORE migrations
    from app import models  # safer for flask-migrate

    # Init Flask Extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Routes
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from app.oauth_routes import oauth_bp
    app.register_blueprint(oauth_bp)

    # Only auto-create schema in development
    if app.config.get("ENV") == "development":
        with app.app_context():
            db.create_all()

            # SQLite schema auto-fix (optional)
            try:
                if db.engine.dialect.name == "sqlite":
                    with db.engine.connect() as conn:
                        res = conn.execute(text("PRAGMA table_info('applications')"))
                        existing_cols = [row[1] for row in res.fetchall()]

                    expected = {
                        "department_notes": "TEXT",
                        "interview_date": "DATETIME",
                        "response_date": "DATETIME",
                    }

                    for col, col_type in expected.items():
                        if col not in existing_cols:
                            with db.engine.begin() as conn:
                                conn.execute(text(f"ALTER TABLE applications ADD COLUMN {col} {col_type}"))
                            app.logger.info(f"Added missing column: {col}")

            except Exception as e:
                app.logger.error(f"SQLite schema patch skipped: {e}")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
