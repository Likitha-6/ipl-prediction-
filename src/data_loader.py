"""
Data Loader Module
Loads and processes comprehensive IPL ball-by-ball data from IPL.csv
Supports 283,678 ball-by-ball records with 64 detailed columns
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
import logging
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPLDataLoader:
    """Load and process comprehensive IPL data"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.ipl_file = self.data_dir / 'IPL.csv'
        self.matches_file = self.data_dir / 'matches.csv'
        self.deliveries_file = self.data_dir / 'deliveries.csv'
        self.df = None  # Main comprehensive dataframe
        self.matches_df = None
        self.deliveries_df = None
    
    def load_raw_data(self):
        """Load raw CSV files"""
        logger.info("Loading raw data...")
        
        if not self.matches_file.exists():
            raise FileNotFoundError(f"Matches file not found: {self.matches_file}")
        if not self.deliveries_file.exists():
            raise FileNotFoundError(f"Deliveries file not found: {self.deliveries_file}")
        
        self.matches_df = pd.read_csv(self.matches_file)
        self.deliveries_df = pd.read_csv(self.deliveries_file)
        
        logger.info(f"Loaded {len(self.matches_df)} matches")
        logger.info(f"Loaded {len(self.deliveries_df)} deliveries")
        
        return self.matches_df, self.deliveries_df
    
    def clean_team_names(self):
        """Standardize team names"""
        logger.info("Cleaning team names...")
        
        team_mapping = {
            'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
            'Kings XI Punjab': 'Punjab Kings',
            'Delhi Daredevils': 'Delhi Capitals',
            'Deccan Chargers': 'Sunrisers Hyderabad',
            'Rising Pune Supergiant': 'Rising Pune Supergiants',
            'Gujarat Lions': 'Gujarat Titans',
        }
        
        # Map team names in matches
        for old_name, new_name in team_mapping.items():
            self.matches_df['team1'] = self.matches_df['team1'].replace(old_name, new_name)
            self.matches_df['team2'] = self.matches_df['team2'].replace(old_name, new_name)
            self.matches_df['toss_winner'] = self.matches_df['toss_winner'].replace(old_name, new_name)
            self.matches_df['winner'] = self.matches_df['winner'].replace(old_name, new_name)
        
        # Map in deliveries
        for old_name, new_name in team_mapping.items():
            self.deliveries_df['batting_team'] = self.deliveries_df['batting_team'].replace(old_name, new_name)
            self.deliveries_df['bowling_team'] = self.deliveries_df['bowling_team'].replace(old_name, new_name)
        
        logger.info("Team names standardized")
    
    def clean_matches(self):
        """Clean matches data"""
        logger.info("Cleaning matches data...")
        
        # Convert date to datetime
        self.matches_df['date'] = pd.to_datetime(self.matches_df['date'])
        
        # Fill missing winner values
        self.matches_df['winner'].fillna('No Result', inplace=True)
        
        # Extract year from date
        self.matches_df['year'] = self.matches_df['date'].dt.year
        
        logger.info("Matches data cleaned")
    
    def calculate_team_stats(self):
        """Calculate team statistics from historical data"""
        logger.info("Calculating team statistics...")
        
        team_stats = {}
        
        # Get all unique teams
        all_teams = set(self.matches_df['team1'].unique()) | set(self.matches_df['team2'].unique())
        
        for team in all_teams:
            matches = self.matches_df[
                ((self.matches_df['team1'] == team) | (self.matches_df['team2'] == team)) &
                (self.matches_df['winner'] != 'No Result')
            ]
            
            home_matches = self.matches_df[
                (self.matches_df['team1'] == team) &
                (self.matches_df['winner'] != 'No Result')
            ]
            
            away_matches = self.matches_df[
                (self.matches_df['team2'] == team) &
                (self.matches_df['winner'] != 'No Result')
            ]
            
            wins = len(matches[matches['winner'] == team])
            total = len(matches)
            
            team_stats[team] = {
                'total_matches': total,
                'wins': wins,
                'losses': total - wins,
                'win_rate': wins / total if total > 0 else 0,
                'home_matches': len(home_matches),
                'home_wins': len(home_matches[home_matches['winner'] == team]),
                'away_matches': len(away_matches),
                'away_wins': len(away_matches[away_matches['winner'] == team]),
            }
        
        logger.info(f"Calculated stats for {len(team_stats)} teams")
        return team_stats
    
    def get_head_to_head(self, team1, team2):
        """Get head-to-head record between two teams"""
        matches = self.matches_df[
            ((self.matches_df['team1'] == team1) & (self.matches_df['team2'] == team2)) |
            ((self.matches_df['team1'] == team2) & (self.matches_df['team2'] == team1))
        ]
        
        team1_wins = len(matches[matches['winner'] == team1])
        team2_wins = len(matches[matches['winner'] == team2])
        
        return {
            'total_matches': len(matches),
            f'{team1}_wins': team1_wins,
            f'{team2}_wins': team2_wins,
            'tie': len(matches) - team1_wins - team2_wins
        }
    
    def get_venue_stats(self, venue):
        """Get statistics for a specific venue"""
        venue_matches = self.matches_df[self.matches_df['venue'] == venue]
        
        return {
            'total_matches': len(venue_matches),
            'avg_winning_margin': venue_matches['result_margin'].mean(),
            'high_score': venue_matches.groupby('team1')['target_runs'].max().max()
        }
    
    def prepare_for_ml(self):
        """Prepare data for machine learning"""
        logger.info("Preparing data for ML...")
        
        ml_data = []
        
        for idx, row in self.matches_df.iterrows():
            team1 = row['team1']
            team2 = row['team2']
            winner = row['winner']
            
            # Basic features
            feature_dict = {
                'match_id': row['id'],
                'date': row['date'],
                'team1': team1,
                'team2': team2,
                'venue': row['venue'],
                'toss_winner': row['toss_winner'],
                'toss_decision': row['toss_decision'],
                'target_runs': row['target_runs'],
                'winner': winner,
                'result': row['result'],
                'year': row['year']
            }
            
            ml_data.append(feature_dict)
        
        ml_df = pd.DataFrame(ml_data)
        logger.info(f"Prepared {len(ml_df)} records for ML")
        
        return ml_df
    
    def get_processed_data(self):
        """Get fully processed data"""
        self.load_raw_data()
        self.clean_team_names()
        self.clean_matches()
        
        return self.prepare_for_ml()


def main():
    """Test data loader"""
    loader = IPLDataLoader('data')
    matches, deliveries = loader.load_raw_data()
    loader.clean_team_names()
    loader.clean_matches()
    
    print("\n" + "="*70)
    print("DATA LOADING SUMMARY")
    print("="*70)
    print(f"Matches: {len(matches)}")
    print(f"Deliveries: {len(deliveries)}")
    
    # Get stats
    stats = loader.calculate_team_stats()
    print(f"\nTop 5 Teams by Win Rate:")
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]['win_rate'], reverse=True)
    for i, (team, stat) in enumerate(sorted_stats[:5], 1):
        print(f"  {i}. {team}: {stat['win_rate']:.2%} ({stat['wins']}/{stat['total_matches']})")
    
    print("\n✓ Data loaded successfully!")


if __name__ == '__main__':
    main()
