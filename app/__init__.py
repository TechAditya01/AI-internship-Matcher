# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Relative imports for internal modules
    from app.oauth_routes import oauth_bp
    from .routes import main_bp
    
    app.register_blueprint(oauth_bp)
    app.register_blueprint(main_bp)
    
    # Initialize other things (DB, utils, etc.)
    # from .database import init_db
    # init_db(app)
    
    return app
