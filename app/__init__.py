# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Load configuration if you have a config file
    # app.config.from_object('app.config.Config')
    
    # Import and register blueprints using relative imports
    from .oauth_routes import oauth_bp
    from .routes import main_bp
    
    app.register_blueprint(oauth_bp)
    app.register_blueprint(main_bp)
    
    # Initialize other components here (DB, utils, etc.)
    # from .database import init_db
    # init_db(app)
    
    return app
