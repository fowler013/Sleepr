"""
Player Performance Prediction Model
Uses machine learning to predict fantasy football player performance
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import logging

logger = logging.getLogger(__name__)

class PlayerPerformanceModel:
    """ML model for predicting player fantasy performance"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, df):
        """
        Prepare features for model training/prediction
        
        Args:
            df: DataFrame with player statistics
            
        Returns:
            np.array: Processed features
        """
        # Feature engineering
        features = []
        
        # Recent performance (last 4 weeks average)
        features.append(df['recent_avg_points'])
        features.append(df['recent_targets'])
        features.append(df['recent_carries'])
        
        # Season-long metrics
        features.append(df['season_avg_points'])
        features.append(df['snap_percentage'])
        features.append(df['target_share'])
        features.append(df['red_zone_touches'])
        
        # Situational factors
        features.append(df['opponent_rank_vs_position'])
        features.append(df['weather_factor'])
        features.append(df['home_away'])  # 1 for home, 0 for away
        
        # Player characteristics
        features.append(df['age'])
        features.append(df['years_experience'])
        features.append(df['injury_risk_score'])
        
        return np.column_stack(features)
    
    def train(self, training_data):
        """
        Train the model on historical data
        
        Args:
            training_data: DataFrame with historical player performance
        """
        logger.info("Training player performance model...")
        
        # Prepare features and target
        X = self.prepare_features(training_data)
        y = training_data['actual_fantasy_points']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Model trained - MAE: {mae:.2f}, R²: {r2:.3f}")
        self.is_trained = True
        
    def predict(self, player_data):
        """
        Predict fantasy points for players
        
        Args:
            player_data: DataFrame with current player stats
            
        Returns:
            np.array: Predicted fantasy points
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
            
        X = self.prepare_features(player_data)
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        
        # Calculate confidence intervals
        # For Random Forest, we can use prediction std from trees
        tree_predictions = np.array([tree.predict(X_scaled) for tree in self.model.estimators_])
        std_predictions = np.std(tree_predictions, axis=0)
        
        return {
            'predictions': predictions,
            'std': std_predictions,
            'confidence_lower': predictions - 1.96 * std_predictions,
            'confidence_upper': predictions + 1.96 * std_predictions
        }
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        if not self.is_trained:
            return None
            
        feature_names = [
            'recent_avg_points', 'recent_targets', 'recent_carries',
            'season_avg_points', 'snap_percentage', 'target_share', 'red_zone_touches',
            'opponent_rank_vs_position', 'weather_factor', 'home_away',
            'age', 'years_experience', 'injury_risk_score'
        ]
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def save_model(self, filepath):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
            
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
        
    def load_model(self, filepath):
        """Load trained model from disk"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.is_trained = model_data['is_trained']
        logger.info(f"Model loaded from {filepath}")

class WaiverWireAnalyzer:
    """Analyzer for identifying waiver wire opportunities"""
    
    @staticmethod
    def calculate_opportunity_score(player_stats):
        """
        Calculate opportunity score for waiver wire players
        
        Args:
            player_stats: DataFrame with player statistics
            
        Returns:
            DataFrame: Players with opportunity scores
        """
        # Factors that indicate opportunity
        factors = {
            'snap_count_trend': 0.3,  # Increasing snap count
            'target_trend': 0.25,     # Increasing targets/carries
            'red_zone_usage': 0.2,    # Red zone opportunities
            'matchup_favorability': 0.15,  # Upcoming matchups
            'injury_replacement': 0.1   # Replacing injured starter
        }
        
        # Placeholder calculation - implement actual logic
        opportunity_scores = np.random.uniform(1, 10, len(player_stats))
        
        result = player_stats.copy()
        result['opportunity_score'] = opportunity_scores
        result['recommendation_strength'] = pd.cut(
            opportunity_scores, 
            bins=[0, 4, 7, 10], 
            labels=['Low', 'Medium', 'High']
        )
        
        return result.sort_values('opportunity_score', ascending=False)

if __name__ == "__main__":
    # Example usage
    model = PlayerPerformanceModel()
    print("Player performance model initialized")
