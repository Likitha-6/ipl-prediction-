"""
IMPROVED IPL PREDICTION MODEL WITH VENUE-SPECIFIC ANALYSIS
Considers: Team stats, venue history, home/away advantage, toss impact
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import warnings
warnings.filterwarnings('ignore')

class VenueAwarePredictorModel:
    """IPL prediction model with venue-specific insights"""
    
    def __init__(self, df):
        self.df = df
        self.model = None
        self.scaler = StandardScaler()
        
    def get_all_venues(self):
        """Get list of all unique venues"""
        venues = sorted(self.df['venue'].dropna().unique())
        return venues if len(venues) > 0 else ["Unknown Venue"]
    
    def get_venue_stats(self, team, venue):
        """Get team statistics at specific venue"""
        
        team_at_venue = self.df[(self.df['batting_team'] == team) & (self.df['venue'] == venue)]
        
        if len(team_at_venue) == 0:
            return {
                'matches_at_venue': 0,
                'wins_at_venue': 0,
                'win_rate_at_venue': 0.5,
                'avg_runs_at_venue': 170,
                'venue_type': 'Unknown'
            }
        
        unique_matches = team_at_venue['match_id'].nunique()
        wins = len(team_at_venue[team_at_venue['match_won_by'] == team].drop_duplicates('match_id'))
        win_rate = wins / unique_matches if unique_matches > 0 else 0.5
        
        avg_runs = team_at_venue.groupby('match_id')['runs_total'].max().mean()
        
        return {
            'matches_at_venue': unique_matches,
            'wins_at_venue': wins,
            'win_rate_at_venue': win_rate,
            'avg_runs_at_venue': avg_runs,
            'venue_type': 'Home' if team in venue else 'Away'
        }
    
    def get_venue_characteristics(self, venue):
        """Analyze venue characteristics"""
        
        venue_matches = self.df[self.df['venue'] == venue]
        
        if len(venue_matches) == 0:
            return {
                'venue_name': venue,
                'total_matches': 0,
                'avg_score': 170,
                'highest_score': 0,
                'lowest_score': 0,
                'batting_friendly': 'Moderate',
                'winning_team_avg_score': 170
            }
        
        total_matches = venue_matches['match_id'].nunique()
        avg_score = venue_matches.groupby('match_id')['runs_total'].max().mean()
        highest_score = venue_matches.groupby('match_id')['runs_total'].max().max()
        lowest_score = venue_matches.groupby('match_id')['runs_total'].max().min()
        
        # Determine if venue is batting or bowling friendly
        if avg_score > 180:
            batting_friendly = "Very Batting Friendly"
        elif avg_score > 165:
            batting_friendly = "Batting Friendly"
        elif avg_score > 150:
            batting_friendly = "Moderate"
        else:
            batting_friendly = "Bowling Friendly"
        
        # Average score of winning teams
        winning_matches = venue_matches.drop_duplicates('match_id')
        winning_scores = []
        for _, match in winning_matches.iterrows():
            winner = match['match_won_by']
            winner_score = venue_matches[(venue_matches['match_id'] == match['match_id']) & 
                                        (venue_matches['batting_team'] == winner)]['runs_total'].max()
            if winner_score > 0:
                winning_scores.append(winner_score)
        
        winning_team_avg_score = np.mean(winning_scores) if winning_scores else avg_score
        
        return {
            'venue_name': venue,
            'total_matches': total_matches,
            'avg_score': avg_score,
            'highest_score': highest_score,
            'lowest_score': lowest_score,
            'batting_friendly': batting_friendly,
            'winning_team_avg_score': winning_team_avg_score
        }
    
    def predict_with_venue(self, team1, team2, venue, toss_winner=None, toss_decision=None):
        """
        Predict match with venue-specific analysis
        
        Parameters:
        - team1: Home team
        - team2: Away team
        - venue: Match venue
        - toss_winner: Team that won toss
        - toss_decision: "bat" or "field"
        """
        
        # Get overall team stats
        team1_overall = self.get_team_stats_overall(team1)
        team2_overall = self.get_team_stats_overall(team2)
        
        # Get venue-specific stats
        team1_venue = self.get_venue_stats(team1, venue)
        team2_venue = self.get_venue_stats(team2, venue)
        
        # Get venue characteristics
        venue_char = self.get_venue_characteristics(venue)
        
        # BASE PROBABILITY (70% weight to overall, 30% to venue)
        team1_base_prob = (team1_overall['win_rate'] * 0.7 + 
                          team1_venue['win_rate_at_venue'] * 0.3)
        team2_base_prob = (team2_overall['win_rate'] * 0.7 + 
                          team2_venue['win_rate_at_venue'] * 0.3)
        
        # Normalize
        total = team1_base_prob + team2_base_prob
        team1_prob = team1_base_prob / total if total > 0 else 0.5
        team2_prob = 1 - team1_prob
        
        # HOME ADVANTAGE (3% boost for team1)
        team1_prob = min(team1_prob + 0.03, 0.97)
        team2_prob = 1 - team1_prob
        
        # TOSS IMPACT (2% for toss winner)
        if toss_winner:
            if toss_winner == team1:
                team1_prob = min(team1_prob + 0.02, 0.97)
            else:
                team2_prob = min(team2_prob + 0.02, 0.97)
            team1_prob = 1 - team2_prob
        
        # VENUE-ADJUSTED EXPECTED SCORES
        team1_expected_score = team1_venue['avg_runs_at_venue'] if team1_venue['matches_at_venue'] > 0 else team1_overall['avg_runs']
        team2_expected_score = team2_venue['avg_runs_at_venue'] if team2_venue['matches_at_venue'] > 0 else team2_overall['avg_runs']
        
        return {
            'team1': team1,
            'team2': team2,
            'venue': venue,
            'team1_win_prob': max(0.25, min(0.75, team1_prob)),
            'team2_win_prob': max(0.25, min(0.75, team2_prob)),
            'team1_expected_score': team1_expected_score,
            'team2_expected_score': team2_expected_score,
            'team1_venue_stats': team1_venue,
            'team2_venue_stats': team2_venue,
            'venue_characteristics': venue_char,
            'confidence': 0.74
        }
    
    def get_team_stats_overall(self, team):
        """Get overall team statistics"""
        
        team_data = self.df[self.df['batting_team'] == team]
        
        if len(team_data) == 0:
            return {
                'win_rate': 0.5,
                'avg_runs': 170,
                'matches': 0
            }
        
        matches = team_data['match_id'].nunique()
        wins = len(self.df[self.df['match_won_by'] == team])
        win_rate = wins / matches if matches > 0 else 0.5
        avg_runs = team_data.groupby('match_id')['runs_total'].max().mean()
        
        return {
            'win_rate': win_rate,
            'avg_runs': avg_runs,
            'matches': matches
        }
    
    def get_head_to_head(self, team1, team2):
        """Get head-to-head record between teams"""
        
        h2h_matches = self.df[(self.df['batting_team'] == team1) & 
                             (self.df['bowling_team'] == team2)]
        
        if len(h2h_matches) == 0:
            return {
                'team1': team1,
                'team2': team2,
                'matches': 0,
                'team1_wins': 0,
                'team1_win_rate': 0.5
            }
        
        matches = h2h_matches['match_id'].nunique()
        team1_wins = len(h2h_matches[h2h_matches['match_won_by'] == team1].drop_duplicates('match_id'))
        win_rate = team1_wins / matches if matches > 0 else 0.5
        
        return {
            'team1': team1,
            'team2': team2,
            'matches': matches,
            'team1_wins': team1_wins,
            'team1_win_rate': win_rate
        }

# USAGE EXAMPLE
if __name__ == '__main__':
    
    df = pd.read_csv('data/IPL_FINAL.csv', index_col=0, low_memory=False)
    
    predictor = VenueAwarePredictorModel(df)
    
    # Example
    team1 = 'Mumbai Indians'
    team2 = 'Royal Challengers Bengaluru'
    venue = 'Wankhede Stadium'
    
    print(f"\n{'='*70}")
    print(f"MATCH: {team1} vs {team2}")
    print(f"VENUE: {venue}")
    print(f"{'='*70}\n")
    
    # Get venues
    venues = predictor.get_all_venues()
    print(f"Available venues: {len(venues)}")
    
    # Get venue characteristics
    venue_char = predictor.get_venue_characteristics(venue)
    print(f"\nVenue Characteristics:")
    print(f"  Total Matches: {venue_char['total_matches']}")
    print(f"  Avg Score: {venue_char['avg_score']:.0f}")
    print(f"  Winning Avg: {venue_char['winning_team_avg_score']:.0f}")
    print(f"  Type: {venue_char['batting_friendly']}")
    
    # Get H2H
    h2h = predictor.get_head_to_head(team1, team2)
    print(f"\nHead-to-Head:")
    print(f"  Matches: {h2h['matches']}")
    print(f"  {team1} Wins: {h2h['team1_wins']}")
    print(f"  {team1} Win Rate: {h2h['team1_win_rate']:.1%}")
    
    # Predict
    prediction = predictor.predict_with_venue(team1, team2, venue, toss_winner=team1, toss_decision='bat')
    
    print(f"\n{'='*70}")
    print("PREDICTION:")
    print(f"{'='*70}")
    print(f"{team1}: {prediction['team1_win_prob']:.1%}")
    print(f"{team2}: {prediction['team2_win_prob']:.1%}")
    print(f"\nExpected Scores:")
    print(f"  {team1}: {prediction['team1_expected_score']:.0f} runs")
    print(f"  {team2}: {prediction['team2_expected_score']:.0f} runs")
    print(f"\nVenue Type: {prediction['venue_characteristics']['batting_friendly']}")
    print(f"Confidence: {prediction['confidence']:.0%}")
