"""
Configuration file for Flask application
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Application configuration"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'nepal-trek-recommendation-secret-key')
    
    # Database configuration - SQLite
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "instance", "database.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Data file path
    TREKS_CSV_PATH = os.path.join(BASE_DIR, 'data', 'nepal_treks_official.csv')
    
    # Recommendation settings
    RECOMMENDATION_SETTINGS = {
        'new_user_weights': {'alpha': 0.5, 'beta': 0.1, 'gamma': 0.4},
        'casual_user_weights': {'alpha': 0.4, 'beta': 0.3, 'gamma': 0.3},
        'regular_user_weights': {'alpha': 0.3, 'beta': 0.5, 'gamma': 0.2},
        'expert_user_weights': {'alpha': 0.2, 'beta': 0.7, 'gamma': 0.1},
        'casual_threshold': 5,
        'regular_threshold': 15,
        'expert_threshold': 16,
        'lambda_diversity': 0.7,
        'top_k': 5,
        'cf_neighbors': 20,
    }
