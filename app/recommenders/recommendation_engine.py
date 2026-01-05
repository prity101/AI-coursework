"""
Comprehensive Recommendation Engine
Integrates Content-Based, Collaborative, Knowledge-Based, and Hybrid approaches
"""
import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from app.models import Trek, User, Rating
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """Main recommendation engine combining multiple algorithms"""
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.cache = {}
    
    # ==================== CONTENT-BASED FILTERING ====================
    
    def content_based_recommend(self, user: User, all_treks: List[Trek], top_k: int = 10) -> List[Tuple[Trek, float, Dict]]:
        """Content-Based Filtering using cosine similarity"""
        recommendations = []
        user_vector = self._build_user_vector(user)
        
        for trek in all_treks:
            if not self._meets_hard_constraints(user, trek):
                continue
            
            trek_vector = self._build_trek_vector(trek)
            
            user_array = np.array([user_vector.get(k, 0) for k in sorted(user_vector.keys())])
            trek_array = np.array([trek_vector.get(k, 0) for k in sorted(trek_vector.keys())])
            
            similarity = float(cosine_similarity([user_array], [trek_array])[0][0])
            
            penalty = self._calculate_soft_penalty(user, trek)
            final_score = similarity * (1.0 - penalty)
            
            explanation = self._build_content_explanation(user, trek, similarity)
            recommendations.append((trek, final_score, explanation))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
    
    # ==================== COLLABORATIVE FILTERING ====================
    
    def collaborative_filtering_recommend(self, user: User, all_treks: List[Trek], 
                                         all_users: List[User], top_k: int = 10) -> List[Tuple[Trek, float, Dict]]:
        """Collaborative Filtering using User-Based Approach"""
        recommendations = {}
        
        similar_users = self._find_similar_users(user, all_users, top_similar=5)
        user_rated_treks = set(r.trek_id for r in user.ratings)
        
        for similar_user, similarity_score in similar_users:
            for rating in similar_user.ratings:
                if rating.trek_id in user_rated_treks:
                    continue
                
                trek = Trek.query.get(rating.trek_id)
                if trek is None:
                    continue
                
                weighted_score = rating.rating * similarity_score
                
                if trek.id not in recommendations:
                    recommendations[trek.id] = {
                        'trek': trek,
                        'score': 0,
                        'votes': 0,
                        'similar_users': []
                    }
                
                recommendations[trek.id]['score'] += weighted_score
                recommendations[trek.id]['votes'] += 1
                recommendations[trek.id]['similar_users'].append((similar_user.name, rating.rating))
        
        result = []
        for trek_id, data in recommendations.items():
            if data['votes'] > 0:
                normalized_score = data['score'] / data['votes']
                explanation = {
                    'method': 'Collaborative Filtering',
                    'reason': f"Users similar to you rated this highly",
                    'similar_users': data['similar_users'],
                    'average_rating': normalized_score
                }
                result.append((data['trek'], normalized_score, explanation))
        
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:top_k]
    
    # ==================== KNOWLEDGE-BASED FILTERING ====================
    
    def knowledge_based_recommend(self, user: User, all_treks: List[Trek], top_k: int = 10) -> List[Tuple[Trek, float, Dict]]:
        """Knowledge-Based Filtering using expert rules"""
        recommendations = []
        
        for trek in all_treks:
            if not self._meets_hard_constraints(user, trek):
                continue
            
            score = 0.0
            reasons = []
            
            difficulty_score, diff_reason = self._score_difficulty_progression(user, trek)
            score += difficulty_score * 0.3
            if diff_reason:
                reasons.append(diff_reason)
            
            seasonal_score, season_reason = self._score_seasonal_fit(user, trek)
            score += seasonal_score * 0.2
            if season_reason:
                reasons.append(season_reason)
            
            interest_score, interest_reason = self._score_interest_alignment(user, trek)
            score += interest_score * 0.25
            if interest_reason:
                reasons.append(interest_reason)
            
            experience_score, exp_reason = self._score_experience_fit(user, trek)
            score += experience_score * 0.25
            if exp_reason:
                reasons.append(exp_reason)
            
            explanation = {
                'method': 'Knowledge-Based',
                'score_components': {
                    'difficulty_fit': difficulty_score,
                    'seasonal_fit': seasonal_score,
                    'interest_alignment': interest_score,
                    'experience_fit': experience_score
                },
                'reasons': reasons
            }
            
            recommendations.append((trek, score, explanation))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
    
    # ==================== HYBRID APPROACH ====================
    
    def hybrid_recommend(self, user: User, all_treks: List[Trek], all_users: List[User], 
                        top_k: int = 10, weights: Dict[str, float] = None) -> List[Tuple[Trek, float, Dict]]:
        """Hybrid Recommendation combining all approaches"""
        if weights is None:
            weights = {
                'content_based': 0.40,
                'collaborative': 0.30,
                'knowledge_based': 0.30
            }
        
        total_weight = sum(weights.values())
        weights = {k: v/total_weight for k, v in weights.items()}
        
        content_recs = self.content_based_recommend(user, all_treks, top_k=top_k*2)
        collab_recs = self.collaborative_filtering_recommend(user, all_treks, all_users, top_k=top_k*2)
        knowledge_recs = self.knowledge_based_recommend(user, all_treks, top_k=top_k*2)
        
        content_scores = {trek.id: score for trek, score, _ in content_recs}
        collab_scores = {trek.id: score for trek, score, _ in collab_recs}
        knowledge_scores = {trek.id: score for trek, score, _ in knowledge_recs}
        
        max_content = max(content_scores.values()) if content_scores else 1
        max_collab = max(collab_scores.values()) if collab_scores else 1
        max_knowledge = max(knowledge_scores.values()) if knowledge_scores else 1
        
        hybrid_scores = {}
        all_trek_ids = set(content_scores.keys()) | set(collab_scores.keys()) | set(knowledge_scores.keys())
        
        for trek_id in all_trek_ids:
            content_norm = (content_scores.get(trek_id, 0) / max_content) if max_content > 0 else 0
            collab_norm = (collab_scores.get(trek_id, 0) / max_collab) if max_collab > 0 else 0
            knowledge_norm = (knowledge_scores.get(trek_id, 0) / max_knowledge) if max_knowledge > 0 else 0
            
            combined_score = (
                content_norm * weights['content_based'] +
                collab_norm * weights['collaborative'] +
                knowledge_norm * weights['knowledge_based']
            )
            
            trek = Trek.query.get(trek_id)
            if trek:
                hybrid_scores[trek_id] = (trek, combined_score, {
                    'content_based': content_norm,
                    'collaborative': collab_norm,
                    'knowledge_based': knowledge_norm
                })
        
        recommendations = list(hybrid_scores.values())
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        result_with_explanation = []
        for trek, score, component_scores in recommendations[:top_k]:
            explanation = {
                'method': 'Hybrid',
                'weights': weights,
                'component_scores': component_scores,
                'reason': 'Combines content-based, collaborative filtering, and knowledge-based rules'
            }
            result_with_explanation.append((trek, score, explanation))
        
        return result_with_explanation
    
    # ==================== HELPER METHODS ====================
    
    def _build_user_vector(self, user: User) -> Dict[str, float]:
        experience_map = {'Beginner': 0.25, 'Intermediate': 0.5, 'Advanced': 0.75, 'Expert': 1.0}
        fitness_map = {'Low': 0.25, 'Moderate': 0.5, 'High': 0.75, 'Very High': 1.0}
        return {
            'experience': experience_map.get(user.experience_level, 0.5),
            'fitness': fitness_map.get(user.fitness_level, 0.5),
            'altitude_exp': min(user.altitude_experience / 6000.0, 1.0),
            'cultural_interest': user.cultural_interest,
            'nature_interest': user.nature_interest,
            'adventure_interest': user.adventure_interest
        }
    
    def _build_trek_vector(self, trek: Trek) -> Dict[str, float]:
        difficulty_map = {'Easy': 0.25, 'Moderate': 0.5, 'Hard': 0.75, 'Very Hard': 1.0}
        return {
            'experience': difficulty_map.get(trek.difficulty, 0.5),
            'fitness': difficulty_map.get(trek.difficulty, 0.5),
            'altitude_exp': min(trek.max_altitude / 6000.0, 1.0) if trek.max_altitude else 0.5,
            'cultural_interest': trek.cultural_score or 0.5,
            'nature_interest': trek.nature_score or 0.5,
            'adventure_interest': trek.adventure_score or 0.5
        }
    
    def _meets_hard_constraints(self, user: User, trek: Trek) -> bool:
        if trek.cost_min and user.budget_max and trek.cost_min > user.budget_max:
            return False
        if trek.duration_days and user.available_days and trek.duration_days > user.available_days:
            return False
        
        difficulty_levels = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3, 'Expert': 4}
        trek_difficulty = {'Easy': 1, 'Moderate': 2, 'Hard': 3, 'Very Hard': 4}
        
        user_level = difficulty_levels.get(user.experience_level, 2)
        required_level = trek_difficulty.get(trek.difficulty, 2)
        
        if required_level > user_level + 1:
            return False
        return True
    
    def _calculate_soft_penalty(self, user: User, trek: Trek) -> float:
        penalty = 0.0
        if user.budget_max and user.budget_max > 0:
            cost_ratio = trek.cost_min / user.budget_max if trek.cost_min else 0
            if cost_ratio > 0.9:
                penalty += 0.15
            elif cost_ratio > 0.7:
                penalty += 0.05
        
        if user.available_days and user.available_days > 0:
            duration_ratio = trek.duration_days / user.available_days if trek.duration_days else 0
            if duration_ratio > 0.95:
                penalty += 0.15
            elif duration_ratio > 0.7:
                penalty += 0.05
        return min(penalty, 0.3)
    
    def _find_similar_users(self, user: User, all_users: List[User], top_similar: int = 5) -> List[Tuple[User, float]]:
        if not user.ratings:
            return []
        
        user_vector = self._build_user_vector(user)
        similarities = []
        
        for other_user in all_users:
            if other_user.id == user.id or not other_user.ratings:
                continue
            
            other_vector = self._build_user_vector(other_user)
            user_arr = np.array([user_vector.get(k, 0) for k in sorted(user_vector.keys())])
            other_arr = np.array([other_vector.get(k, 0) for k in sorted(other_vector.keys())])
            
            similarity = float(cosine_similarity([user_arr], [other_arr])[0][0])
            similarities.append((other_user, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_similar]
    
    def _score_difficulty_progression(self, user: User, trek: Trek) -> Tuple[float, str]:
        difficulty_levels = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3, 'Expert': 4}
        trek_difficulty = {'Easy': 1, 'Moderate': 2, 'Hard': 3, 'Very Hard': 4}
        
        user_level = difficulty_levels.get(user.experience_level, 2)
        trek_level = trek_difficulty.get(trek.difficulty, 2)
        
        if trek_level == user_level:
            return 1.0, f"Perfect difficulty level for {user.experience_level} trekkers"
        elif trek_level == user_level + 1:
            return 0.8, f"Good challenge for {user.experience_level} trekkers"
        elif trek_level > user_level + 1:
            return 0.3, "Challenging - might be too difficult"
        else:
            return 0.6, f"Good for building experience"
    
    def _score_seasonal_fit(self, user: User, trek: Trek) -> Tuple[float, str]:
        if not trek.best_seasons or not user.preferred_seasons:
            return 0.7, None
        
        trek_seasons = set(trek.best_seasons.replace('|', ',').split(','))
        user_seasons = set(user.preferred_seasons.split(','))
        
        overlap = len(trek_seasons & user_seasons)
        total = len(trek_seasons | user_seasons)
        
        score = overlap / total if total > 0 else 0.5
        
        if score > 0.7:
            return score, f"Great seasonal fit"
        elif score > 0.3:
            return score, f"Some seasonal overlap"
        else:
            return 0.3, f"Different seasons"
    
    def _score_interest_alignment(self, user: User, trek: Trek) -> Tuple[float, str]:
        cultural_alignment = 1.0 - abs(user.cultural_interest - (trek.cultural_score or 0.5))
        nature_alignment = 1.0 - abs(user.nature_interest - (trek.nature_score or 0.5))
        adventure_alignment = 1.0 - abs(user.adventure_interest - (trek.adventure_score or 0.5))
        
        combined_score = (cultural_alignment + nature_alignment + adventure_alignment) / 3
        
        if combined_score > 0.8:
            return combined_score, "Excellent interest match"
        elif combined_score > 0.6:
            return combined_score, "Good interest alignment"
        else:
            return combined_score, "Some interest overlap"
    
    def _score_experience_fit(self, user: User, trek: Trek) -> Tuple[float, str]:
        trek_altitude = trek.max_altitude or 3000
        user_altitude = user.altitude_experience or 0
        altitude_score = 1.0 - abs(user_altitude - trek_altitude) / 6000.0
        altitude_score = max(0, min(altitude_score, 1.0))
        
        if altitude_score > 0.8:
            return altitude_score, "Altitude experience match"
        elif altitude_score > 0.5:
            return altitude_score, "Reasonable altitude challenge"
        else:
            return altitude_score, "Significant altitude challenge"
    
    def _build_content_explanation(self, user: User, trek: Trek, similarity: float) -> Dict:
        reasons = []
        
        if abs(user.cultural_interest - (trek.cultural_score or 0.5)) < 0.2:
            reasons.append(f"Matches your cultural interest")
        
        if abs(user.nature_interest - (trek.nature_score or 0.5)) < 0.2:
            reasons.append(f"Matches your nature interest")
        
        if abs(user.adventure_interest - (trek.adventure_score or 0.5)) < 0.2:
            reasons.append(f"Matches your adventure interest")
        
        if trek.difficulty in self._map_experience_to_difficulties(user.experience_level):
            reasons.append(f"Appropriate difficulty for your level")
        
        if trek.cost_min and user.budget_max and trek.cost_min <= user.budget_max:
            reasons.append(f"Fits your budget range")
        
        return {
            'method': 'Content-Based Filtering',
            'similarity_score': similarity,
            'reasons': reasons
        }
    
    def _map_experience_to_difficulties(self, experience: str) -> List[str]:
        mapping = {
            'Beginner': ['Easy', 'Moderate'],
            'Intermediate': ['Moderate', 'Hard'],
            'Advanced': ['Hard', 'Very Hard'],
            'Expert': ['Very Hard']
        }
        return mapping.get(experience, ['Moderate'])
