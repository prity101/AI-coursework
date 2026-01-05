"""
Database Models
SQLAlchemy models for Users, Treks, and Ratings
"""
from app import db
from datetime import datetime

class User(db.Model):
    """User model - stores user profile and preferences"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    nationality = db.Column(db.String(50))
    
    # Experience and fitness
    experience_level = db.Column(db.String(20))
    fitness_level = db.Column(db.String(20))
    altitude_experience = db.Column(db.Integer, default=0)
    
    # Budget and time
    budget_min = db.Column(db.Integer)
    budget_max = db.Column(db.Integer)
    available_days = db.Column(db.Integer)
    
    # Interest scores (0.0 to 1.0)
    cultural_interest = db.Column(db.Float, default=0.5)
    nature_interest = db.Column(db.Float, default=0.5)
    adventure_interest = db.Column(db.Float, default=0.5)
    
    # Preferences
    preferred_seasons = db.Column(db.String(50))
    accommodation_preference = db.Column(db.String(20))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'nationality': self.nationality,
            'experience_level': self.experience_level,
            'fitness_level': self.fitness_level,
            'altitude_experience': self.altitude_experience,
            'budget_min': self.budget_min,
            'budget_max': self.budget_max,
            'available_days': self.available_days,
            'cultural_interest': self.cultural_interest,
            'nature_interest': self.nature_interest,
            'adventure_interest': self.adventure_interest,
            'preferred_seasons': self.preferred_seasons,
            'accommodation_preference': self.accommodation_preference,
            'rating_count': len(self.ratings)
        }
    
    def get_feature_vector(self):
        experience_map = {'Beginner': 0.25, 'Intermediate': 0.5, 'Advanced': 0.75, 'Expert': 1.0}
        fitness_map = {'Low': 0.25, 'Moderate': 0.5, 'High': 0.75, 'Very High': 1.0}
        return {
            'experience': experience_map.get(self.experience_level, 0.5),
            'fitness': fitness_map.get(self.fitness_level, 0.5),
            'altitude_exp': min(self.altitude_experience / 6000.0, 1.0),
            'cultural_interest': self.cultural_interest,
            'nature_interest': self.nature_interest,
            'adventure_interest': self.adventure_interest
        }


class Trek(db.Model):
    """Trek model - stores trek information"""
    __tablename__ = 'treks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    region = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))
    
    duration_days = db.Column(db.Integer)
    max_altitude = db.Column(db.Integer)
    cost_min = db.Column(db.Integer)
    cost_max = db.Column(db.Integer)
    best_seasons = db.Column(db.String(100))
    
    cultural_score = db.Column(db.Float, default=0.5)
    nature_score = db.Column(db.Float, default=0.5)
    adventure_score = db.Column(db.Float, default=0.5)
    
    accommodation_type = db.Column(db.String(30))
    permit_required = db.Column(db.Boolean, default=False)
    guide_required = db.Column(db.Boolean, default=False)
    physical_fitness = db.Column(db.String(20))
    technical_skills = db.Column(db.String(30))
    
    description = db.Column(db.Text)
    highlights = db.Column(db.Text)
    avg_rating = db.Column(db.Float, default=4.0)
    rating_count = db.Column(db.Integer, default=0)
    
    ratings = db.relationship('Rating', backref='trek', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'region': self.region,
            'difficulty': self.difficulty,
            'duration_days': self.duration_days,
            'max_altitude': self.max_altitude,
            'cost_min': self.cost_min,
            'cost_max': self.cost_max,
            'best_seasons': self.best_seasons,
            'cultural_score': self.cultural_score,
            'nature_score': self.nature_score,
            'adventure_score': self.adventure_score,
            'accommodation_type': self.accommodation_type,
            'permit_required': self.permit_required,
            'guide_required': self.guide_required,
            'physical_fitness': self.physical_fitness,
            'technical_skills': self.technical_skills,
            'description': self.description,
            'highlights': self.highlights,
            'avg_rating': self.avg_rating,
            'rating_count': self.rating_count
        }
    
    def get_feature_vector(self):
        difficulty_map = {'Easy': 0.25, 'Moderate': 0.5, 'Hard': 0.75, 'Very Hard': 1.0}
        return {
            'difficulty': difficulty_map.get(self.difficulty, 0.5),
            'duration': min(self.duration_days / 21.0, 1.0) if self.duration_days else 0.5,
            'altitude': min(self.max_altitude / 6000.0, 1.0) if self.max_altitude else 0.5,
            'cultural_score': self.cultural_score or 0.5,
            'nature_score': self.nature_score or 0.5,
            'adventure_score': self.adventure_score or 0.5,
            'cost': min((self.cost_min + self.cost_max) / 2 / 2000.0, 1.0) if self.cost_min and self.cost_max else 0.5
        }


class Rating(db.Model):
    """Rating model - stores user ratings for treks"""
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'trek_id': self.trek_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.isoformat()
        }
