"""
LIME-based Explainability for Trek Recommendations
Provides human-understandable reasons for trek recommendations
"""

import numpy as np
from typing import Dict, List, Tuple
from app.models import User, Trek


class TrekExplainer:
    """Provides feature-based explanations for trek recommendations."""
    
    def __init__(self):
        self.feature_weights = {
            'difficulty_match': 0.25,
            'budget_match': 0.20,
            'altitude_match': 0.15,
            'duration_match': 0.12,
            'cultural_interest': 0.10,
            'nature_interest': 0.10,
            'season_match': 0.08
        }
        
    def explain_recommendation(self, user: User, trek: Trek, final_score: float,
                              algorithm_used: str = "Hybrid") -> Dict:
        """Generate human-readable explanation for why a trek was recommended."""
        feature_contributions = self._calculate_feature_contributions(user, trek)
        
        sorted_features = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        positive = [(feat, score) for feat, score in sorted_features if score > 0]
        negative = [(feat, score) for feat, score in sorted_features if score < 0]
        
        return {
            'trek_name': trek.name,
            'final_score': round(final_score, 3),
            'algorithm': algorithm_used,
            'top_positive_features': positive[:3],
            'top_negative_features': negative[:2],
            'feature_contributions': feature_contributions,
            'explanation_text': self._generate_text_explanation(
                trek.name, positive[:3], negative[:2], final_score
            )
        }
    
    def _calculate_feature_contributions(self, user: User, trek: Trek) -> Dict[str, float]:
        """Calculate feature contributions to recommendation."""
        contributions = {}
        
        # 1. Difficulty Match
        difficulty_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3, 'Expert': 4}
        trek_diff_map = {'Easy': 1, 'Moderate': 2, 'Challenging': 3, 'Strenuous': 4}
        user_diff = difficulty_map.get(user.experience_level, 2)
        trek_diff = trek_diff_map.get(trek.difficulty, 2)
        diff_delta = abs(user_diff - trek_diff)
        
        if diff_delta == 0:
            contributions['difficulty_match'] = self.feature_weights['difficulty_match']
        elif diff_delta == 1:
            contributions['difficulty_match'] = self.feature_weights['difficulty_match'] * 0.5
        else:
            contributions['difficulty_match'] = -self.feature_weights['difficulty_match'] * 0.3
        
        # 2. Budget Match
        if trek.cost_min and user.budget_max:
            if trek.cost_min <= user.budget_max:
                budget_ratio = trek.cost_min / max(user.budget_max, 1)
                contributions['budget_match'] = self.feature_weights['budget_match'] * (1 - budget_ratio * 0.5)
            else:
                overage = (trek.cost_min - user.budget_max) / max(user.budget_max, 1)
                contributions['budget_match'] = -self.feature_weights['budget_match'] * min(overage, 1.0)
        else:
            contributions['budget_match'] = 0
        
        # 3. Altitude Match
        max_safe_altitude = self._calculate_max_safe_altitude(user)
        if trek.max_altitude:
            altitude_diff = trek.max_altitude - max_safe_altitude
            if altitude_diff <= 0:
                contributions['altitude_match'] = self.feature_weights['altitude_match']
            elif altitude_diff <= 500:
                contributions['altitude_match'] = self.feature_weights['altitude_match'] * 0.6
            else:
                contributions['altitude_match'] = -self.feature_weights['altitude_match'] * 0.5
        else:
            contributions['altitude_match'] = 0
        
        # 4. Duration Match
        if trek.duration_days and user.available_days:
            duration_diff = abs(trek.duration_days - user.available_days)
            if duration_diff == 0:
                contributions['duration_match'] = self.feature_weights['duration_match']
            elif duration_diff <= 2:
                contributions['duration_match'] = self.feature_weights['duration_match'] * 0.7
            else:
                contributions['duration_match'] = -self.feature_weights['duration_match'] * 0.4
        else:
            contributions['duration_match'] = 0
        
        # 5. Cultural Interest Alignment
        if user.cultural_interest and trek.cultural_interest:
            cultural_alignment = 1 - abs(user.cultural_interest - trek.cultural_interest)
            contributions['cultural_interest'] = self.feature_weights['cultural_interest'] * cultural_alignment
        else:
            contributions['cultural_interest'] = 0
        
        # 6. Nature Interest Alignment
        if user.nature_interest and trek.nature_interest:
            nature_alignment = 1 - abs(user.nature_interest - trek.nature_interest)
            contributions['nature_interest'] = self.feature_weights['nature_interest'] * nature_alignment
        else:
            contributions['nature_interest'] = 0
        
        # 7. Season Match
        contributions['season_match'] = self.feature_weights['season_match'] * 0.5
        
        return contributions
    
    def _calculate_max_safe_altitude(self, user: User) -> int:
        """Calculate maximum safe altitude based on user profile."""
        base_altitude = {
            'Beginner': 4000,
            'Intermediate': 5000,
            'Advanced': 5500,
            'Expert': 6000
        }.get(user.experience_level, 4000)
        
        fitness_bonus = {
            'Low': -500,
            'Moderate': 0,
            'High': 500,
            'Very High': 1000
        }.get(user.fitness_level, 0)
        
        return base_altitude + fitness_bonus
    
    def _generate_text_explanation(self, trek_name: str, positive_features: List[Tuple[str, float]],
                                   negative_features: List[Tuple[str, float]], score: float) -> str:
        """Generate human-readable text explanation."""
        feature_descriptions = {
            'difficulty_match': 'difficulty level matches your experience',
            'budget_match': 'cost fits within your budget',
            'altitude_match': 'altitude is suitable for your fitness level',
            'duration_match': 'duration aligns with your preference',
            'cultural_interest': 'cultural experiences match your interests',
            'nature_interest': 'natural scenery matches your interests',
            'season_match': 'best seasons align with your preferred time'
        }
        
        text = f"**{trek_name}** (Score: {score:.2f})\n\n"
        
        if positive_features:
            text += "✓ **Recommended because:**\n"
            for feat, contribution in positive_features:
                desc = feature_descriptions.get(feat, feat)
                text += f"  • {desc} (+{contribution:.2f})\n"
        
        if negative_features:
            text += "\n✗ **Potential concerns:**\n"
            for feat, contribution in negative_features:
                desc = feature_descriptions.get(feat, feat)
                text += f"  • {desc} ({contribution:.2f})\n"
        
        return text


def explain_top_recommendations(user: User, recommendations: List[Tuple[Trek, float]],
                               algorithm: str = "Hybrid", top_n: int = 5) -> List[Dict]:
    """Generate explanations for top N recommendations."""
    explainer = TrekExplainer()
    explanations = []
    
    for trek, score in recommendations[:top_n]:
        explanation = explainer.explain_recommendation(user, trek, score, algorithm)
        explanations.append(explanation)
    
    return explanations
