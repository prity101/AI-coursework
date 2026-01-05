"""
API Routes for Trek Recommendation System
Content-Based, Collaborative, Knowledge-Based, and Hybrid recommendations
"""

from flask import Blueprint, request, jsonify
from app.models import Trek, User, Rating
from app.recommenders.recommendation_engine import RecommendationEngine
from app.explainability.lime_explainer import TrekExplainer
from app import db
import logging

logger = logging.getLogger(__name__)
recommendation_bp = Blueprint('recommendations', __name__)

rec_engine = RecommendationEngine()
trek_explainer = TrekExplainer()

# ==================== TREK ROUTES ====================

@recommendation_bp.route('/treks', methods=['GET'])
def get_all_treks():
    """Get all treks"""
    treks = Trek.query.all()
    return jsonify({
        'total': len(treks),
        'treks': [trek.to_dict() for trek in treks]
    }), 200

@recommendation_bp.route('/treks/<int:trek_id>', methods=['GET'])
def get_trek(trek_id):
    """Get a specific trek"""
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({'error': 'Trek not found'}), 404
    return jsonify(trek.to_dict()), 200

# ==================== USER ROUTES ====================

@recommendation_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        user = User(
            name=data.get('name'),
            age=data.get('age'),
            nationality=data.get('nationality'),
            experience_level=data.get('experience_level', 'Beginner'),
            fitness_level=data.get('fitness_level', 'Moderate'),
            altitude_experience=data.get('altitude_experience', 0),
            budget_min=data.get('budget_min', 0),
            budget_max=data.get('budget_max', 5000),
            available_days=data.get('available_days', 14),
            cultural_interest=data.get('cultural_interest', 0.5),
            nature_interest=data.get('nature_interest', 0.5),
            adventure_interest=data.get('adventure_interest', 0.5),
            preferred_seasons=data.get('preferred_seasons'),
            accommodation_preference=data.get('accommodation_preference', 'Any')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return jsonify({'error': str(e)}), 500

@recommendation_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200

@recommendation_bp.route('/users', methods=['GET'])
def get_all_users():
    """Get all users"""
    users = User.query.all()
    return jsonify({
        'total': len(users),
        'users': [user.to_dict() for user in users]
    }), 200

# ==================== RECOMMENDATION ROUTES ====================

@recommendation_bp.route('/recommend/content-based/<int:user_id>', methods=['GET'])
def content_based_recommend(user_id):
    """Content-Based Filtering recommendations"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        top_k = request.args.get('top_k', 10, type=int)
        all_treks = Trek.query.all()
        
        if not all_treks:
            return jsonify({'error': 'No treks available'}), 404
        
        recommendations = rec_engine.content_based_recommend(user, all_treks, top_k=top_k)
        
        return jsonify({
            'method': 'Content-Based Filtering',
            'user_id': user_id,
            'total_recommendations': len(recommendations),
            'recommendations': [
                {
                    'trek_id': trek.id,
                    'trek_name': trek.name,
                    'region': trek.region,
                    'difficulty': trek.difficulty,
                    'duration_days': trek.duration_days,
                    'max_altitude': trek.max_altitude,
                    'cost_range': f"${trek.cost_min}-${trek.cost_max}",
                    'score': round(score, 3),
                    'explanation': explanation,
                }
                for trek, score, explanation in recommendations
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@recommendation_bp.route('/recommend/collaborative/<int:user_id>', methods=['GET'])
def collaborative_recommend(user_id):
    """Collaborative Filtering recommendations"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        top_k = request.args.get('top_k', 10, type=int)
        all_treks = Trek.query.all()
        all_users = User.query.all()
        
        recommendations = rec_engine.collaborative_filtering_recommend(user, all_treks, all_users, top_k=top_k)
        
        return jsonify({
            'method': 'Collaborative Filtering',
            'user_id': user_id,
            'total_recommendations': len(recommendations),
            'recommendations': [
                {
                    'trek_id': trek.id,
                    'trek_name': trek.name,
                    'region': trek.region,
                    'difficulty': trek.difficulty,
                    'duration_days': trek.duration_days,
                    'max_altitude': trek.max_altitude,
                    'cost_range': f"${trek.cost_min}-${trek.cost_max}",
                    'score': round(score, 3),
                    'explanation': explanation,
                }
                for trek, score, explanation in recommendations
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@recommendation_bp.route('/recommend/knowledge-based/<int:user_id>', methods=['GET'])
def knowledge_based_recommend(user_id):
    """Knowledge-Based Filtering recommendations"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        top_k = request.args.get('top_k', 10, type=int)
        all_treks = Trek.query.all()
        
        recommendations = rec_engine.knowledge_based_recommend(user, all_treks, top_k=top_k)
        
        return jsonify({
            'method': 'Knowledge-Based Filtering',
            'user_id': user_id,
            'total_recommendations': len(recommendations),
            'recommendations': [
                {
                    'trek_id': trek.id,
                    'trek_name': trek.name,
                    'region': trek.region,
                    'difficulty': trek.difficulty,
                    'duration_days': trek.duration_days,
                    'max_altitude': trek.max_altitude,
                    'cost_range': f"${trek.cost_min}-${trek.cost_max}",
                    'score': round(score, 3),
                    'explanation': explanation,
                }
                for trek, score, explanation in recommendations
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@recommendation_bp.route('/recommend/hybrid/<int:user_id>', methods=['GET'])
def hybrid_recommend(user_id):
    """Hybrid recommendations combining all approaches"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        top_k = request.args.get('top_k', 10, type=int)
        all_treks = Trek.query.all()
        all_users = User.query.all()
        
        recommendations = rec_engine.hybrid_recommend(user, all_treks, all_users, top_k=top_k)
        
        return jsonify({
            'method': 'Hybrid Recommendation',
            'user_id': user_id,
            'total_recommendations': len(recommendations),
            'recommendations': [
                {
                    'trek_id': trek.id,
                    'trek_name': trek.name,
                    'region': trek.region,
                    'difficulty': trek.difficulty,
                    'duration_days': trek.duration_days,
                    'max_altitude': trek.max_altitude,
                    'cost_range': f"${trek.cost_min}-${trek.cost_max}",
                    'score': round(score, 3),
                    'explanation': explanation,
                }
                for trek, score, explanation in recommendations
            ]
        }), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== EXPLAINABILITY ROUTES ====================

@recommendation_bp.route('/explain/<int:user_id>/<int:trek_id>', methods=['GET'])
def explain_recommendation(user_id, trek_id):
    """Get XAI explanation for a recommendation"""
    try:
        user = User.query.get(user_id)
        trek = Trek.query.get(trek_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if not trek:
            return jsonify({'error': 'Trek not found'}), 404
        
        explanation = trek_explainer.explain_recommendation(user, trek, 0.8)
        
        return jsonify({
            'user_id': user_id,
            'trek_id': trek_id,
            'trek_name': trek.name,
            'explanation': explanation
        }), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== RATING ROUTES ====================

@recommendation_bp.route('/ratings', methods=['POST'])
def create_rating():
    """Create a new rating"""
    try:
        data = request.get_json()
        
        rating = Rating(
            user_id=data.get('user_id'),
            trek_id=data.get('trek_id'),
            rating=data.get('rating'),
            review=data.get('review')
        )
        
        db.session.add(rating)
        db.session.commit()
        
        return jsonify({
            'message': 'Rating created',
            'rating': rating.to_dict()
        }), 201
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== HEALTH CHECK ====================

@recommendation_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'treks': Trek.query.count(),
        'users': User.query.count(),
        'algorithms': ['content-based', 'collaborative', 'knowledge-based', 'hybrid']
    }), 200
