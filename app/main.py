"""
IPL Match Prediction Dashboard - Production Version
Uses comprehensive ball-by-ball data from IPL.csv (283,678 records)
Features: Match prediction, team analysis, 2026 season, historical data
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer import IPLAnalyzer

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="IPL Prediction Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZE SESSION STATE & LOAD DATA
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_resource
def load_analyzer():
    """Load and cache the data analyzer"""
    return IPLAnalyzer('data/IPL_FINAL.csv')

try:
    analyzer = load_analyzer()
    data_loaded = analyzer.df is not None
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    st.title("🏏 IPL Match Prediction Dashboard")
    st.markdown("Predict IPL match outcomes using comprehensive historical data (2008-2026)")
    
    if not data_loaded:
        st.error("❌ Failed to load data. Please ensure IPL.csv is in the data/ directory.")
        st.info("Download IPL.csv and place it in: data/IPL.csv")
        return
    
    # Sidebar navigation
    st.sidebar.header("📊 Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["🎯 Match Prediction", "📈 Team Analysis", "🏟️ Venue Stats", "🔍 2026 Season", "📋 Historical Data"]
    )
    
    # Route to appropriate page
    if page == "🎯 Match Prediction":
        prediction_page()
    elif page == "📈 Team Analysis":
        team_analysis_page()
    elif page == "🏟️ Venue Stats":
        venue_stats_page()
    elif page == "🔍 2026 Season":
        season_2026_page()
    elif page == "📋 Historical Data":
        historical_data_page()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1: MATCH PREDICTION
# ═══════════════════════════════════════════════════════════════════════════════

def prediction_page():
    st.header("🎯 Match Prediction")
    st.markdown("Predict the winner and analyze match dynamics")
    
    # Get team list
    team_stats = analyzer.get_team_statistics()
    all_teams = sorted(team_stats.keys())
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("🏠 Home Team", all_teams, key="home")
    
    with col2:
        away_team = st.selectbox("🚗 Away Team", [t for t in all_teams if t != home_team], key="away")
    
    # Toss details
    st.subheader("Toss Information")
    col1, col2 = st.columns(2)
    
    with col1:
        toss_winner = st.radio("Who won toss?", [home_team, away_team], horizontal=True)
    
    with col2:
        toss_decision = st.radio("Toss decision?", ["bat", "field"], horizontal=True)
    
    # Predict button
    if st.button("🔮 Predict Match", use_container_width=True, key="predict_btn"):
        with st.spinner("Analyzing match data..."):
            prediction = analyzer.predict_match(home_team, away_team, venue="Unknown")
            
            st.success("✅ Prediction Complete!")
            
            # Display probabilities
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    f"🏠 {home_team}",
                    f"{prediction['team1_win_prob']:.1%}",
                    "Win Probability"
                )
            
            with col2:
                st.metric(
                    f"🚗 {away_team}",
                    f"{prediction['team2_win_prob']:.1%}",
                    "Win Probability"
                )
            
            # Chart
            st.subheader("📊 Win Probability Comparison")
            chart_data = pd.DataFrame({
                'Team': [home_team, away_team],
                'Probability': [prediction['team1_win_prob'], prediction['team2_win_prob']]
            })
            st.bar_chart(chart_data.set_index('Team'), use_container_width=True)
            
            # Score analysis
            st.subheader("📈 Score Analysis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{home_team}** Average: {prediction['team1_avg_runs']:.0f} runs")
            with col2:
                st.write(f"**{away_team}** Average: {prediction['team2_avg_runs']:.0f} runs")
            
            # Chasing thresholds
            st.subheader("🎯 Chasing Difficulty Levels")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success("🟢 **Easy Chase**\n< 160 runs\n✓ 80% win rate")
            with col2:
                st.warning("🟡 **Moderate Chase**\n160-180 runs\n≈ 50% win rate")
            with col3:
                st.error("🔴 **Difficult Chase**\n> 180 runs\n✗ 35% win rate")
            
            # Key factors
            st.subheader("🔍 Key Factors")
            
            team1_stats = team_stats[home_team]
            team2_stats = team_stats[away_team]
            
            factors = f"""
            - **{home_team} Historical Win Rate**: {team1_stats['win_rate']:.1%}
            - **{away_team} Historical Win Rate**: {team2_stats['win_rate']:.1%}
            - **Home Advantage**: +3% for {home_team}
            - **Toss Impact**: {toss_winner} won toss, chose to {toss_decision}
            - **Sample Size**: {team1_stats['matches']} matches analyzed for {home_team}
            """
            st.markdown(factors)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: TEAM ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def team_analysis_page():
    st.header("📈 Team Analysis")
    st.markdown("Detailed statistics for each IPL team (all time)")
    
    team_stats = analyzer.get_team_statistics()
    all_teams = sorted(team_stats.keys())
    
    selected_team = st.selectbox("Select Team", all_teams)
    
    if selected_team in team_stats:
        stats = team_stats[selected_team]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Matches", stats['matches'])
        with col2:
            st.metric("✅ Wins", stats['wins'])
        with col3:
            st.metric("❌ Losses", stats['losses'])
        with col4:
            st.metric("🎯 Win Rate", f"{stats['win_rate']:.1%}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📈 Avg Runs Scored", f"{stats['avg_runs']:.0f}")
        with col2:
            st.metric("⚡ Expected Score", f"{stats['avg_runs']:.0f} runs per match")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: VENUE STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

def venue_stats_page():
    st.header("🏟️ Venue Statistics")
    st.markdown("Analyze performance at different IPL venues")
    
    with st.spinner("Loading venue data..."):
        venues = analyzer.get_venue_statistics()
        
        if venues is not None and len(venues) > 0:
            st.subheader("Top 10 Venues by Match Count")
            
            chart_data = venues.head(10)
            st.bar_chart(chart_data['total_matches'])
            
            st.subheader("Venue Details")
            st.dataframe(venues.head(15), use_container_width=True)
        else:
            st.info("No venue data available")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: 2026 SEASON ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def season_2026_page():
    st.header("🔍 IPL 2026 Season Analysis")
    st.markdown("Current season standings and match results")
    
    with st.spinner("Loading 2026 season data..."):
        standings, matches = analyzer.get_2026_season_data()
        
        if standings is not None and len(standings) > 0:
            st.subheader("📊 Current Standings")
            
            # Create standings table with ranking
            standings_display = standings.copy()
            standings_display.insert(0, 'Rank', range(1, len(standings_display) + 1))
            
            st.dataframe(standings_display, use_container_width=True, hide_index=True)
            
            # Pie chart
            st.subheader("📈 Win Distribution (Top 5)")
            fig_data = standings_display.head(5).set_index('winner')
            st.pie_chart(fig_data['wins'])
            
            # Recent matches
            st.subheader("⚡ Recent Matches")
            
            if len(matches) > 0:
                recent_matches = matches.tail(10).sort_values('date', ascending=False)
                
                display_cols = ['date', 'batting_team', 'bowling_team', 'match_won_by', 'win_outcome', 'venue']
                available_cols = [c for c in display_cols if c in recent_matches.columns]
                
                st.dataframe(recent_matches[available_cols], use_container_width=True)
        else:
            st.info("No 2026 season data available yet")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: HISTORICAL DATA
# ═══════════════════════════════════════════════════════════════════════════════

def historical_data_page():
    st.header("📋 Historical Data Explorer")
    st.markdown("Browse and analyze historical IPL data (2008-2026)")
    
    # Dataset overview
    st.subheader("📊 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Total Records", f"{len(analyzer.df):,}")
    with col2:
        st.metric("🏏 Unique Matches", analyzer.df['match_id'].nunique())
    with col3:
        st.metric("🎭 Unique Teams", analyzer.df['batting_team'].nunique())
    with col4:
        st.metric("📅 Years Covered", f"2008-2026")
    
    # Top players
    st.subheader("⭐ Top 10 Batsmen (All Time)")
    batsmen, bowlers = analyzer.get_player_statistics()
    
    if len(batsmen) > 0:
        display_batsmen = batsmen.head(10).copy()
        display_batsmen.columns = ['Runs', 'Matches', 'Balls', 'Average', 'Strike Rate']
        display_batsmen = display_batsmen.round(2)
        st.dataframe(display_batsmen, use_container_width=True)
    
    st.subheader("🎯 Top 10 Bowlers (All Time)")
    if len(bowlers) > 0:
        st.dataframe(bowlers.head(10), use_container_width=True)
    
    st.subheader("📈 Data Statistics")
    st.info(f"""
    - **Ball-by-ball records**: {len(analyzer.df):,}
    - **Total matches**: {analyzer.df['match_id'].nunique()}
    - **Teams**: {analyzer.df['batting_team'].nunique()}
    - **Unique batters**: {analyzer.df['batter'].nunique()}
    - **Unique bowlers**: {analyzer.df['bowler'].nunique()}
    - **Seasons**: {int(analyzer.df['year'].max() - analyzer.df['year'].min() + 1)} (2008-2026)
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# RUN APP
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
