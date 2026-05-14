"""
Machine Learning Model Module
Trains and evaluates prediction models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPLPredictionModel:
    """IPL Match Prediction Model"""
    
    def __init__(self, model_type='ensemble'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.feature_importance = None
        self.metrics = {}
    
    def prepare_training_data(self, feature_df):
        """Prepare data for training"""
        logger.info("Preparing training data...")
        
        # Feature columns
        self.feature_columns = [
            'team1_win_rate',
            'team2_win_rate',
            'team1_home_win_rate',
            'team2_away_win_rate',
            'team1_recent_form',
            'team2_recent_form',
            'team1_h2h_rate',
            'toss_winner_is_team1',
            'team1_vs_team2_strength',
            'team1_home_advantage',
            'team1_avg_runs',
            'team2_avg_runs',
        ]
        
        # Create X and y
        X = feature_df[self.feature_columns].fillna(0.5)
        y = feature_df['team1_won']
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        logger.info(f"X shape: {X.shape}, y shape: {y.shape}")
        logger.info(f"Positive class: {(y == 1).sum()}, Negative class: {(y == 0).sum()}")
        
        return X, y
    
    def train(self, feature_df, test_size=0.2, random_state=42):
        """Train the model"""
        logger.info(f"Training {self.model_type} model...")
        
        X, y = self.prepare_training_data(feature_df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if self.model_type == 'logistic':
            self.model = LogisticRegression(random_state=random_state, max_iter=1000)
        elif self.model_type == 'random_forest':
            self.model = RandomForestClassifier(n_estimators=100, random_state=random_state)
        elif self.model_type == 'gradient_boost':
            self.model = GradientBoostingClassifier(n_estimators=100, random_state=random_state)
        elif self.model_type == 'ensemble':
            # Use logistic regression for ensemble
            self.model = LogisticRegression(random_state=random_state, max_iter=1000)
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        self._evaluate(X_train_scaled, X_test_scaled, y_train, y_test)
        
        logger.info("Model training complete!")
        return self.model
    
    def _evaluate(self, X_train, X_test, y_train, y_test):
        """Evaluate model performance"""
        logger.info("Evaluating model...")
        
        # Predictions
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # Metrics
        self.metrics = {
            'train_accuracy': accuracy_score(y_train, y_train_pred),
            'test_accuracy': accuracy_score(y_test, y_test_pred),
            'precision': precision_score(y_test, y_test_pred),
            'recall': recall_score(y_test, y_test_pred),
            'f1': f1_score(y_test, y_test_pred),
        }
        
        logger.info(f"Train Accuracy: {self.metrics['train_accuracy']:.4f}")
        logger.info(f"Test Accuracy: {self.metrics['test_accuracy']:.4f}")
        logger.info(f"Precision: {self.metrics['precision']:.4f}")
        logger.info(f"Recall: {self.metrics['recall']:.4f}")
        logger.info(f"F1-Score: {self.metrics['f1']:.4f}")
    
    def predict_probability(self, features_dict):
        """Predict win probability for a match"""
        
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Create feature vector
        feature_values = []
        for col in self.feature_columns:
            feature_values.append(features_dict.get(col, 0.5))
        
        X = np.array(feature_values).reshape(1, -1)
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prob = self.model.predict_proba(X_scaled)[0]
        
        return {
            'team1_win_prob': float(prob[1]),
            'team2_win_prob': float(prob[0]),
        }
    
    def save_model(self, model_path='models'):
        """Save trained model"""
        logger.info(f"Saving model to {model_path}...")
        
        Path(model_path).mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, f'{model_path}/model.pkl')
        joblib.dump(self.scaler, f'{model_path}/scaler.pkl')
        
        # Save feature columns
        with open(f'{model_path}/features.txt', 'w') as f:
            f.write('\n'.join(self.feature_columns))
        
        # Save metrics
        import json
        with open(f'{model_path}/metrics.json', 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        logger.info("Model saved!")
    
    def load_model(self, model_path='models'):
        """Load trained model"""
        logger.info(f"Loading model from {model_path}...")
        
        self.model = joblib.load(f'{model_path}/model.pkl')
        self.scaler = joblib.load(f'{model_path}/scaler.pkl')
        
        # Load feature columns
        with open(f'{model_path}/features.txt', 'r') as f:
            self.feature_columns = f.read().strip().split('\n')
        
        logger.info("Model loaded!")


def main():
    """Train and test model"""
    from data_loader import IPLDataLoader
    from feature_engineering import FeatureEngineer
    
    # Load data
    logger.info("Loading data...")
    loader = IPLDataLoader('data')
    matches, deliveries = loader.load_raw_data()
    loader.clean_team_names()
    loader.clean_matches()
    
    # Engineer features
    logger.info("Engineering features...")
    engineer = FeatureEngineer(matches, deliveries)
    engineer.calculate_team_statistics()
    training_df = engineer.create_training_dataset()
    
    # Train model
    model = IPLPredictionModel(model_type='ensemble')
    model.train(training_df)
    
    # Save model
    model.save_model('models')
    
    print("\n" + "="*70)
    print("MODEL TRAINING COMPLETE")
    print("="*70)
    print(f"\nMetrics:")
    for metric, value in model.metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    print("\n✓ Model trained and saved!")


if __name__ == '__main__':
    main()
