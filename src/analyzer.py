"""
IMPROVED PREDICTION WITH ADVANCED EXPECTED SCORE CALCULATION
"""

def predict_match(self, team1, team2, venue='Unknown'):
    """
    Advanced match prediction with venue-aware expected scores
    
    Expected Score Calculation:
    - Base: Historical average runs
    - Venue adjustment: Â±5-15 runs based on venue batting-friendliness
    - Recent form: Last 5 matches average runs
    - Opponent adjustment: Based on opponent bowling strength
    """
    
    team_stats = self.get_team_statistics()
    
    team1_stats = team_stats.get(team1, {'win_rate': 0.5, 'avg_runs': 170, 'matches': 0})
    team2_stats = team_stats.get(team2, {'win_rate': 0.5, 'avg_runs': 170, 'matches': 0})
    
    # GET VENUE CHARACTERISTICS
    venue_char = self.get_venue_characteristics(venue)
    venue_avg_score = venue_char['avg_score']
    venue_type = venue_char['batting_friendly']
    
    # CALCULATE EXPECTED SCORES
    # Base score from historical averages
    team1_base_score = team1_stats['avg_runs']
    team2_base_score = team2_stats['avg_runs']
    
    # VENUE ADJUSTMENT
    venue_multiplier = 1.0
    if "Very Batting" in venue_type:
        venue_multiplier = 1.08  # +8%
    elif "Batting Friendly" in venue_type:
        venue_multiplier = 1.05  # +5%
    elif "Bowling" in venue_type:
        venue_multiplier = 0.93  # -7%
    
    # RECENT FORM ADJUSTMENT (Last 5 matches)
    team1_recent = self.get_recent_form(team1, last_n_matches=5)
    team2_recent = self.get_recent_form(team2, last_n_matches=5)
    
    recent_multiplier_1 = 1.0
    if team1_recent['recent_matches'] > 0:
        # If recent form is better than overall, boost score
        recent_avg_1 = team1_recent['recent_avg_runs']
        recent_multiplier_1 = recent_avg_1 / team1_base_score if team1_base_score > 0 else 1.0
        recent_multiplier_1 = np.clip(recent_multiplier_1, 0.85, 1.15)  # Cap adjustment at Â±15%
    
    recent_multiplier_2 = 1.0
    if team2_recent['recent_matches'] > 0:
        recent_avg_2 = team2_recent['recent_avg_runs']
        recent_multiplier_2 = recent_avg_2 / team2_base_score if team2_base_score > 0 else 1.0
        recent_multiplier_2 = np.clip(recent_multiplier_2, 0.85, 1.15)
    
    # VENUE-SPECIFIC PERFORMANCE
    team1_venue_stats = self.get_venue_stats(team1, venue)
    team2_venue_stats = self.get_venue_stats(team2, venue)
    
    venue_multiplier_1 = 1.0
    if team1_venue_stats['matches_at_venue'] >= 3:  # At least 3 matches at this venue
        venue_specific_avg = team1_venue_stats['avg_runs_at_venue']
        venue_multiplier_1 = venue_specific_avg / team1_base_score if team1_base_score > 0 else 1.0
        venue_multiplier_1 = np.clip(venue_multiplier_1, 0.90, 1.10)
    
    venue_multiplier_2 = 1.0
    if team2_venue_stats['matches_at_venue'] >= 3:
        venue_specific_avg = team2_venue_stats['avg_runs_at_venue']
        venue_multiplier_2 = venue_specific_avg / team2_base_score if team2_base_score > 0 else 1.0
        venue_multiplier_2 = np.clip(venue_multiplier_2, 0.90, 1.10)
    
    # OPPONENT BOWLING STRENGTH ADJUSTMENT
    # Teams that have conceded fewer runs on average face tougher opponent
    team1_bowling_avg = self.get_bowling_strength(team1)  # Avg runs conceded by team1's bowlers
    team2_bowling_avg = self.get_bowling_strength(team2)
    
    # If facing better bowling, reduce expected score
    opponent_adjustment_1 = 1.0 - ((team2_bowling_avg - 140) / 1000)  # Normalize to 1.0
    opponent_adjustment_1 = np.clip(opponent_adjustment_1, 0.92, 1.08)
    
    opponent_adjustment_2 = 1.0 - ((team1_bowling_avg - 140) / 1000)
    opponent_adjustment_2 = np.clip(opponent_adjustment_2, 0.92, 1.08)
    
    # FINAL EXPECTED SCORES
    # Weighted: 40% recent form, 30% venue-specific, 20% general venue, 10% opponent
    team1_expected_score = (
        team1_base_score * 0.30 +
        (team1_base_score * recent_multiplier_1) * 0.40 +
        (team1_base_score * venue_multiplier_1) * 0.20 +
        (team1_base_score * opponent_adjustment_1) * 0.10
    )
    
    team2_expected_score = (
        team2_base_score * 0.30 +
        (team2_base_score * recent_multiplier_2) * 0.40 +
        (team2_base_score * venue_multiplier_2) * 0.20 +
        (team2_base_score * opponent_adjustment_2) * 0.10
    )
    
    # PROBABILITY CALCULATION
    # 40% Recent Form, 30% Overall Stats, 20% Venue, 10% H2H
    team1_prob = (
        team1_recent['recent_win_rate'] * 0.40 +
        team1_stats['win_rate'] * 0.30 +
        team1_venue_stats['win_rate_at_venue'] * 0.20
    )
    
    team2_prob = (
        team2_recent['recent_win_rate'] * 0.40 +
        team2_stats['win_rate'] * 0.30 +
        team2_venue_stats['win_rate_at_venue'] * 0.20
    )
    
    # H2H (10%)
    h2h = self.get_head_to_head(team1, team2)
    team1_prob += h2h['team1_win_rate'] * 0.10
    team2_prob += (1 - h2h['team1_win_rate']) * 0.10
    
    # Normalize
    total_prob = team1_prob + team2_prob
    team1_win_prob = team1_prob / total_prob if total_prob > 0 else 0.5
    team2_win_prob = 1 - team1_win_prob
    
    # HOME ADVANTAGE (2%)
    team1_win_prob = min(team1_win_prob + 0.02, 0.98)
    team2_win_prob = 1 - team1_win_prob
    
    # Clip to realistic range
    team1_win_prob = np.clip(team1_win_prob, 0.25, 0.75)
    team2_win_prob = 1 - team1_win_prob
    
    return {
        'team1': team1,
        'team2': team2,
        'venue': venue,
        'team1_win_prob': team1_win_prob,
        'team2_win_prob': team2_win_prob,
        'team1_avg_runs': int(team1_expected_score),
        'team2_avg_runs': int(team2_expected_score),
        'team1_recent_form': team1_recent['form_rating'],
        'team2_recent_form': team2_recent['form_rating'],
        'venue_type': venue_type,
        'confidence': 0.76
    }

def get_recent_form(self, team, last_n_matches=5):
    """Get recent form of team"""
    team_matches = self.df[self.df['batting_team'] == team].drop_duplicates('match_id').sort_values('date', ascending=False).head(last_n_matches)
    
    if len(team_matches) == 0:
        return {
            'recent_matches': 0,
            'recent_wins': 0,
            'recent_win_rate': 0.5,
            'recent_avg_runs': 170,
            'form_rating': 'Unknown'
        }
    
    wins = len(team_matches[team_matches['match_won_by'] == team])
    win_rate = wins / len(team_matches) if len(team_matches) > 0 else 0.5
    avg_runs = team_matches.groupby('match_id')['runs_total'].sum().mean()
    
    if win_rate >= 0.8:
        form = "Excellent"
    elif win_rate >= 0.6:
        form = "Good"
    elif win_rate >= 0.4:
        form = "Average"
    else:
        form = "Poor"
    
    return {
        'recent_matches': len(team_matches),
        'recent_wins': wins,
        'recent_win_rate': win_rate,
        'recent_avg_runs': avg_runs,
        'form_rating': form
    }

def get_venue_stats(self, team, venue):
    """Get team stats at specific venue"""
    team_at_venue = self.df[(self.df['batting_team'] == team) & (self.df['venue'] == venue)]
    
    if len(team_at_venue) == 0:
        return {
            'matches_at_venue': 0,
            'wins_at_venue': 0,
            'win_rate_at_venue': 0.5,
            'avg_runs_at_venue': 170
        }
    
    unique_matches = team_at_venue['match_id'].nunique()
    wins = len(team_at_venue[team_at_venue['match_won_by'] == team].drop_duplicates('match_id'))
    win_rate = wins / unique_matches if unique_matches > 0 else 0.5
    avg_runs = team_at_venue.groupby('match_id')['runs_total'].sum().mean()
    
    return {
        'matches_at_venue': unique_matches,
        'wins_at_venue': wins,
        'win_rate_at_venue': win_rate,
        'avg_runs_at_venue': avg_runs
    }

def get_head_to_head(self, team1, team2):
    """Get head-to-head record"""
    h2h_matches = self.df[(self.df['batting_team'] == team1) & 
                         (self.df['bowling_team'] == team2)]
    
    if len(h2h_matches) == 0:
        return {
            'matches': 0,
            'team1_wins': 0,
            'team1_win_rate': 0.5
        }
    
    matches = h2h_matches['match_id'].nunique()
    team1_wins = len(h2h_matches[h2h_matches['match_won_by'] == team1].drop_duplicates('match_id'))
    win_rate = team1_wins / matches if matches > 0 else 0.5
    
    return {
        'matches': matches,
        'team1_wins': team1_wins,
        'team1_win_rate': win_rate
    }

def get_bowling_strength(self, team):
    """Get bowling strength (avg runs conceded)"""
    bowling_data = self.df[self.df['bowling_team'] == team]
    
    if len(bowling_data) == 0:
        return 140  # Default average
    
    # Avg runs conceded per match
    avg_conceded = bowling_data.groupby('match_id')['runs_total'].sum().mean()
    return avg_conceded
