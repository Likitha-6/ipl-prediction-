"""
Feature Engineering Module
Creates features for ML model training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Create features for match prediction"""
    
    def __init__(self, matches_df, deliveries_df):
        self.matches_df = matches_df.copy()
        self.deliveries_df = deliveries_df.copy()
        self.team_stats = {}
        self.feature_df = None
    
    def calculate_team_statistics(self):
        """Calculate comprehensive team statistics"""
        logger.info("Calculating team statistics...")
        
        matches = self.matches_df[self.matches_df['winner'] != 'No Result'].copy()
        
        # Get all unique teams
        all_teams = set(matches['team1'].unique()) | set(matches['team2'].unique())
        
        for team in all_teams:
            team_matches = matches[
                ((matches['team1'] == team) | (matches['team2'] == team))
            ].copy()
            
            wins = len(team_matches[team_matches['winner'] == team])
            total = len(team_matches)
            
            # Runs statistics
            team_1_runs = self.matches_df[self.matches_df['team1'] == team]['target_runs'].mean()
            team_2_runs = self.matches_df[self.matches_df['team2'] == team]['target_runs'].mean()
            avg_runs_scored = (team_1_runs + team_2_runs) / 2
            
            # Home and away
            home_matches = team_matches[team_matches['team1'] == team]
            away_matches = team_matches[team_matches['team2'] == team]
            
            home_wins = len(home_matches[home_matches['winner'] == team])
            away_wins = len(away_matches[away_matches['winner'] == team])
            
            self.team_stats[team] = {
                'total_matches': total,
                'wins': wins,
                'losses': total - wins,
                'win_rate': wins / total if total > 0 else 0,
                'home_matches': len(home_matches),
                'home_wins': home_wins,
                'home_win_rate': home_wins / len(home_matches) if len(home_matches) > 0 else 0,
                'away_matches': len(away_matches),
                'away_wins': away_wins,
                'away_win_rate': away_wins / len(away_matches) if len(away_matches) > 0 else 0,
                'avg_runs_scored': avg_runs_scored,
            }
        
        logger.info(f"Calculated stats for {len(self.team_stats)} teams")
        return self.team_stats
    
    def get_recent_form(self, team, reference_date, days=30):
        """Get team's recent form"""
        recent_matches = self.matches_df[
            (
                ((self.matches_df['team1'] == team) | (self.matches_df['team2'] == team)) &
                (self.matches_df['date'] <= reference_date) &
                (self.matches_df['date'] >= (reference_date - timedelta(days=days)))
            )
        ].sort_values('date', ascending=False).head(5)
        
        if len(recent_matches) == 0:
            return 0
        
        wins = len(recent_matches[recent_matches['winner'] == team])
        return wins / len(recent_matches)
    
    def get_head_to_head(self, team1, team2):
        """Get head-to-head record"""
        h2h = self.matches_df[
            (
                ((self.matches_df['team1'] == team1) & (self.matches_df['team2'] == team2)) |
                ((self.matches_df['team1'] == team2) & (self.matches_df['team2'] == team1))
            )
        ]
        
        if len(h2h) == 0:
            return 0.5  # Default to 50% if no history
        
        team1_wins = len(h2h[h2h['winner'] == team1])
        return team1_wins / len(h2h)
    
    def create_match_features(self, team1, team2, toss_winner, toss_decision, match_date=None):
        """Create features for a specific match"""
        
        if match_date is None:
            match_date = datetime.now()
        
        features = {}
        
        # Team statistics
        t1_stats = self.team_stats.get(team1, {})
        t2_stats = self.team_stats.get(team2, {})
        
        features['team1_win_rate'] = t1_stats.get('win_rate', 0.5)
        features['team2_win_rate'] = t2_stats.get('win_rate', 0.5)
        
        features['team1_home_win_rate'] = t1_stats.get('home_win_rate', 0.5) if toss_winner == team1 or True else 0
        features['team2_away_win_rate'] = t2_stats.get('away_win_rate', 0.5) if team2 != toss_winner or True else 0
        
        # Recent form
        features['team1_recent_form'] = self.get_recent_form(team1, match_date)
        features['team2_recent_form'] = self.get_recent_form(team2, match_date)
        
        # Head to head
        features['team1_h2h_rate'] = self.get_head_to_head(team1, team2)
        
        # Toss impact
        features['toss_winner_is_team1'] = 1 if toss_winner == team1 else 0
        features['toss_bat_impact'] = 1 if toss_decision == 'bat' else 0
        
        # Average runs
        features['team1_avg_runs'] = t1_stats.get('avg_runs_scored', 170)
        features['team2_avg_runs'] = t2_stats.get('avg_runs_scored', 170)
        
        # Derived features
        features['team1_vs_team2_strength'] = features['team1_win_rate'] - features['team2_win_rate']
        features['team1_home_advantage'] = 0.03 if toss_winner == team1 else -0.03
        
        return features
    
    def create_training_dataset(self):
        """Create dataset for model training"""
        logger.info("Creating training dataset...")
        
        training_data = []
        
        for idx, match in self.matches_df.iterrows():
            if match['winner'] == 'No Result':
                continue
            
            team1 = match['team1']
            team2 = match['team2']
            winner = match['winner']
            match_date = match['date']
            
            # Skip if team stats not available
            if team1 not in self.team_stats or team2 not in self.team_stats:
                continue
            
            features = self.create_match_features(
                team1, team2,
                match['toss_winner'],
                match['toss_decision'],
                match_date
            )
            
            features['match_id'] = match['id']
            features['date'] = match_date
            features['team1'] = team1
            features['team2'] = team2
            features['venue'] = match['venue']
            features['target_runs'] = match['target_runs']
            features['result'] = match['result']
            features['winner'] = winner
            features['team1_won'] = 1 if winner == team1 else 0
            
            training_data.append(features)
        
        self.feature_df = pd.DataFrame(training_data)
        logger.info(f"Created {len(self.feature_df)} training samples")
        
        return self.feature_df
    
    def get_feature_importance_columns(self):
        """Get important feature columns"""
        return [
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


def main():
    """Test feature engineering"""
    from data_loader import IPLDataLoader
    
    logger.info("Loading data...")
    loader = IPLDataLoader('data')
    matches, deliveries = loader.load_raw_data()
    loader.clean_team_names()
    loader.clean_matches()
    
    logger.info("Engineering features...")
    engineer = FeatureEngineer(matches, deliveries)
    engineer.calculate_team_statistics()
    training_df = engineer.create_training_dataset()
    
    print("\n" + "="*70)
    print("FEATURE ENGINEERING SUMMARY")
    print("="*70)
    print(f"Training samples: {len(training_df)}")
    print(f"Features: {len(engineer.get_feature_importance_columns())}")
    print(f"\nSample features:")
    print(training_df.head(1).to_string())
    print("\n✓ Features created successfully!")


if __name__ == '__main__':
    main()
