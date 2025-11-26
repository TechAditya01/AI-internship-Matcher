"""
WSGI entry point for production deployment (Render, Heroku, etc.)
This module is used by gunicorn to run the Flask app.

Usage:
  gunicorn -w 4 -b 0.0.0.0:10000 wsgi:app
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
