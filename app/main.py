"""
IPL Match Prediction Dashboard - PREMIUM DESIGN (NO CACHE)
Modern, attractive interface with advanced styling and animations
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.analyzer import IPLAnalyzer

st.set_page_config(
    page_title="IPL Prediction Engine",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PREMIUM CSS STYLING
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Poppins:wght@600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        color: #f1f5f9;
    }
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 4rem 2rem;
        border-radius: 25px;
        margin-bottom: 3rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(240, 147, 251, 0.3) 0%, transparent 70%);
        border-radius: 50%;
    }
    
    .header-content {
        position: relative;
        z-index: 1;
        text-align: center;
    }
    
    .header-content h1 {
        margin: 0;
        font-size: 4rem;
        font-weight: 800;
        color: white;
        font-family: 'Poppins', sans-serif;
        letter-spacing: -2px;
        text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .header-content p {
        margin: 1rem 0 0 0;
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    .team-display {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(148, 163, 184, 0.2);
        transition: all 0.3s ease;
    }
    
    .team-display:hover {
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
    }
    
    .team-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 1rem 0;
        font-family: 'Poppins', sans-serif;
    }
    
    .probability-container {
        margin: 2rem 0;
    }
    
    .probability-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    
    .probability-bar {
        background: rgba(148, 163, 184, 0.1);
        border: 1px solid rgba(148, 163, 184, 0.2);
        height: 50px;
        border-radius: 15px;
        overflow: hidden;
        position: relative;
    }
    
    .probability-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        transition: width 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    }
    
    .stat-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        border-color: rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
    
    .stat-value {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.8rem 0;
        font-family: 'Poppins', sans-serif;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .difficulty-badge {
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        font-family: 'Poppins', sans-serif;
        border: none;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
    }
    
    .difficulty-easy {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .difficulty-moderate {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .difficulty-difficult {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .difficulty-title {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
    
    .difficulty-subtitle {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }
    
    .difficulty-rate {
        font-size: 0.95rem;
        margin-top: 1rem;
        opacity: 0.9;
    }
    
    .section-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f1f5f9;
        margin: 3rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #667eea, #764ba2) 1;
        font-family: 'Poppins', sans-serif;
        letter-spacing: -0.5px;
    }
    
    .insight-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        border-left: 4px solid #667eea;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    
    .insight-box:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .insight-box h4 {
        color: #667eea;
        margin: 0 0 0.8rem 0;
        font-size: 1.1rem;
        font-weight: 700;
        font-family: 'Poppins', sans-serif;
    }
    
    .insight-box p {
        margin: 0.5rem 0;
        color: #cbd5e1;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# LOAD DATA - NO CACHE
analyzer = IPLAnalyzer('data/IPL_FINAL.csv')
data_loaded = analyzer.df is not None

def main():
    st.markdown("""
    <div class='header-container'>
        <div class='header-content'>
            <h1>Cricket Match Prediction</h1>
            <p>AI-Powered IPL Win Probability Engine</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not data_loaded:
        st.error("Failed to load data")
        return
    
    st.sidebar.markdown("### Select Analysis")
    page = st.sidebar.radio(
        "Navigation",
        ["Match Prediction", "Team Performance", "Venue Insights", "2026 Season", "Historical Analysis"],
        label_visibility="collapsed"
    )
    
    if page == "Match Prediction":
        prediction_page()
    elif page == "Team Performance":
        team_analysis_page()
    elif page == "Venue Insights":
        venue_stats_page()
    elif page == "2026 Season":
        season_2026_page()
    elif page == "Historical Analysis":
        historical_data_page()

def prediction_page():
    st.markdown("<div class='section-header'>Match Prediction Engine</div>", unsafe_allow_html=True)
    
    team_stats = analyzer.get_team_statistics()
    all_teams = sorted(team_stats.keys())
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("Home Team", all_teams, key="home")
    
    with col2:
        away_team = st.selectbox("Away Team", [t for t in all_teams if t != home_team], key="away")
    
    st.markdown("### Match Context")
    col1, col2 = st.columns(2)
    
    with col1:
        toss_winner = st.radio("Toss Winner", [home_team, away_team], horizontal=True)
    
    with col2:
        toss_decision = st.radio("Decision", ["Bat", "Field"], horizontal=True)
    
    if st.button("Analyze Match", use_container_width=True, key="predict_btn"):
        with st.spinner("Analyzing..."):
            prediction = analyzer.predict_match(home_team, away_team, venue="Unknown")
            
            st.success("Analysis Complete!")
            
            st.markdown("<div class='section-header'>Win Probability</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class='team-display'>
                    <div class='team-name'>{home_team}</div>
                    <div class='probability-container'>
                        <div class='probability-label'>Win Chance</div>
                        <div class='probability-bar'>
                            <div class='probability-fill' style='width: {prediction['team1_win_prob']*100}%'>
                                {prediction['team1_win_prob']:.1%}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='team-display'>
                    <div class='team-name'>{away_team}</div>
                    <div class='probability-container'>
                        <div class='probability-label'>Win Chance</div>
                        <div class='probability-bar'>
                            <div class='probability-fill' style='width: {prediction['team2_win_prob']*100}%'>
                                {prediction['team2_win_prob']:.1%}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            fig = go.Figure(data=[
                go.Bar(x=[home_team, away_team], 
                       y=[prediction['team1_win_prob'], prediction['team2_win_prob']], 
                       marker_color=['#667eea', '#764ba2'],
                       text=[f"{prediction['team1_win_prob']:.1%}", f"{prediction['team2_win_prob']:.1%}"],
                       textposition='outside')
            ])
            fig.update_layout(
                title="Win Probability Comparison",
                showlegend=False,
                height=400,
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f1f5f9', family='Inter')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("<div class='section-header'>Expected Performance</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class='stat-box'>
                    <div class='stat-label'>Expected Score</div>
                    <div class='stat-value'>{prediction['team1_avg_runs']:.0f}</div>
                    <div class='stat-label'>{home_team}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='stat-box'>
                    <div class='stat-label'>Expected Score</div>
                    <div class='stat-value'>{prediction['team2_avg_runs']:.0f}</div>
                    <div class='stat-label'>{away_team}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div class='section-header'>Chase Analysis</div>", unsafe_allow_html=True)
            
            target = prediction['team2_avg_runs']
            
            if target < 160:
                diff_class = "difficulty-easy"
                level = "MANAGEABLE"
                rate = "75-85% Success Rate"
            elif target < 180:
                diff_class = "difficulty-moderate"
                level = "CHALLENGING"
                rate = "45-55% Success Rate"
            else:
                diff_class = "difficulty-difficult"
                level = "DIFFICULT"
                rate = "30-40% Success Rate"
            
            st.markdown(f"""
            <div class='difficulty-badge {diff_class}'>
                <div class='difficulty-title'>{level}</div>
                <div class='difficulty-subtitle'>Target: {target:.0f} Runs</div>
                <div class='difficulty-rate'>{rate}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='section-header'>Key Insights</div>", unsafe_allow_html=True)
            
            team1_stats = team_stats[home_team]
            team2_stats = team_stats[away_team]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class='insight-box'>
                    <h4>{home_team}</h4>
                    <p><strong>Win Rate:</strong> {team1_stats['win_rate']:.1%}</p>
                    <p><strong>Avg Runs:</strong> {team1_stats['avg_runs']:.0f}</p>
                    <p><strong>Matches:</strong> {team1_stats['matches']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='insight-box'>
                    <h4>{away_team}</h4>
                    <p><strong>Win Rate:</strong> {team2_stats['win_rate']:.1%}</p>
                    <p><strong>Avg Runs:</strong> {team2_stats['avg_runs']:.0f}</p>
                    <p><strong>Matches:</strong> {team2_stats['matches']}</p>
                </div>
                """, unsafe_allow_html=True)

def team_analysis_page():
    st.markdown("<div class='section-header'>Team Performance Analysis</div>", unsafe_allow_html=True)
    
    team_stats = analyzer.get_team_statistics()
    all_teams = sorted(team_stats.keys())
    
    selected_team = st.selectbox("Select Team", all_teams)
    
    if selected_team in team_stats:
        stats = team_stats[selected_team]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='stat-box'>
                <div class='stat-label'>Total Matches</div>
                <div class='stat-value'>{stats['matches']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='stat-box'>
                <div class='stat-label'>Wins</div>
                <div class='stat-value'>{stats['wins']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='stat-box'>
                <div class='stat-label'>Win Rate</div>
                <div class='stat-value'>{stats['win_rate']:.0%}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='stat-box'>
                <div class='stat-label'>Avg Runs</div>
                <div class='stat-value'>{stats['avg_runs']:.0f}</div>
            </div>
            """, unsafe_allow_html=True)

def venue_stats_page():
    st.markdown("<div class='section-header'>Venue Insights</div>", unsafe_allow_html=True)
    
    venues = analyzer.get_venue_statistics()
    
    if venues is not None and len(venues) > 0:
        fig = px.bar(venues.head(10), x=venues.head(10).index, y='total_matches')
        fig.update_traces(marker_color='#667eea')
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#f1f5f9'))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(venues.head(15), use_container_width=True)

def season_2026_page():
    st.markdown("<div class='section-header'>IPL 2026 Season</div>", unsafe_allow_html=True)
    
    standings, matches = analyzer.get_2026_season_data()
    
    if standings is not None and len(standings) > 0:
        st.subheader("League Standings")
        standings_display = standings.copy()
        standings_display.insert(0, 'Position', range(1, len(standings_display) + 1))
        st.dataframe(standings_display, use_container_width=True, hide_index=True)

def historical_data_page():
    st.markdown("<div class='section-header'>Historical Data</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-label'>Records</div>
            <div class='stat-value'>{len(analyzer.df):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-label'>Matches</div>
            <div class='stat-value'>{analyzer.df['match_id'].nunique()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-label'>Teams</div>
            <div class='stat-value'>{analyzer.df['batting_team'].nunique()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-label'>Years</div>
            <div class='stat-value'>19</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("Top Players")
    batsmen, bowlers = analyzer.get_player_statistics()
    
    if len(batsmen) > 0:
        st.write("**Top Batsmen**")
        st.dataframe(batsmen.head(10), use_container_width=True)
    
    if len(bowlers) > 0:
        st.write("**Top Bowlers**")
        st.dataframe(bowlers.head(10), use_container_width=True)

if __name__ == "__main__":
    main()
