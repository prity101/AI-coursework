"""
Flask Application Factory
"""
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
import os

db = SQLAlchemy()

def create_app(config_class=Config):
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure instance folder exists
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'instance'), exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register API routes
    from app.routes.recommendations import recommendation_bp
    app.register_blueprint(recommendation_bp, url_prefix='/api')
    
    # Frontend directory - go up from app/ to backend/ then to frontend/
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(os.path.dirname(backend_dir), 'frontend')
    
    @app.route('/')
    def index():
        try:
            return send_from_directory(frontend_dir, 'index.html')
        except Exception as e:
            return f"Frontend directory: {frontend_dir}<br>Error: {str(e)}"
    
    @app.route('/<path:filename>')
    def serve_frontend(filename):
        try:
            return send_from_directory(frontend_dir, filename)
        except Exception as e:
            return f"Looking for: {filename} in {frontend_dir}<br>Error: {str(e)}", 404
    
    return app
