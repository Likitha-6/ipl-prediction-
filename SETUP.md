# Setup Guide

## Quick Start (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/IPL_Prediction_Dashboard.git
cd IPL_Prediction_Dashboard
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Add Data Files
Place your data files in the `data/` directory:
- `matches.csv` - Match results
- `deliveries.csv` - Ball-by-ball data

```bash
mkdir -p data
# Copy your CSV files here
cp /path/to/matches.csv data/
cp /path/to/deliveries.csv data/
```

### 5. Train Model (Optional - First Time Only)
```bash
python src/model.py
```

This will:
- Load and clean data
- Engineer features
- Train ML model
- Save model to `models/` directory

### 6. Run Dashboard
```bash
streamlit run app/main.py
```

Open browser to `http://localhost:8501`

---

## Directory Structure

```
IPL_Prediction_Dashboard/
├── data/
│   ├── matches.csv           # Place your match data here
│   └── deliveries.csv        # Place your delivery data here
├── src/
│   ├── data_loader.py        # Data loading utilities
│   ├── feature_engineering.py # ML feature creation
│   ├── model.py              # Model training
│   └── utils.py              # Helper functions
├── app/
│   ├── main.py               # Streamlit application
│   └── pages/                # Additional pages (optional)
├── models/
│   ├── model.pkl             # Trained model (auto-generated)
│   ├── scaler.pkl            # Feature scaler (auto-generated)
│   └── metrics.json          # Model metrics (auto-generated)
├── notebooks/                # Jupyter notebooks (optional)
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── SETUP.md                  # This file
└── .gitignore               # Git ignore file
```

---

## Detailed Setup

### Python Version
- Requires Python 3.9 or higher
- Check: `python --version`

### Creating Virtual Environment

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Installing Dependencies

```bash
pip install -r requirements.txt
```

For development (with testing tools):
```bash
pip install -r requirements.txt
pip install pytest jupyter ipython
```

### Data Preparation

Your `matches.csv` should have these columns:
```
id, season, city, date, match_type, player_of_match, venue, team1, team2,
toss_winner, toss_decision, winner, result, result_margin, target_runs,
target_overs, super_over, method, umpire1, umpire2
```

Your `deliveries.csv` should have:
```
match_id, inning, batting_team, bowling_team, over, ball, batter, bowler,
non_striker, batsman_runs, extra_runs, total_runs, extras_type, is_wicket,
player_dismissed, dismissal_kind, fielder
```

### Testing Data Loading

```bash
python -c "
from src.data_loader import IPLDataLoader
loader = IPLDataLoader('data')
matches, deliveries = loader.load_raw_data()
print(f'Loaded {len(matches)} matches and {len(deliveries)} deliveries')
"
```

---

## Running the Application

### Option 1: Streamlit App (Recommended)
```bash
streamlit run app/main.py
```

Features:
- Interactive web interface
- Real-time predictions
- Historical data analysis
- Team comparisons

### Option 2: Command Line
```bash
python src/model.py --predict --team1 "RCB" --team2 "MI"
```

### Option 3: Python API
```python
from src.predictor import IPLPredictor

predictor = IPLPredictor()
result = predictor.predict(
    home_team="Royal Challengers Bengaluru",
    away_team="Mumbai Indians"
)
print(result)
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution:** Reinstall requirements
```bash
pip install --upgrade -r requirements.txt
```

### Issue: "FileNotFoundError: data/matches.csv not found"
**Solution:** Ensure data files are in correct location
```bash
ls -la data/  # Check if files exist
# If not, copy them:
cp /your/data/matches.csv data/
cp /your/data/deliveries.csv data/
```

### Issue: Model takes too long to train
**Solution:** 
- First time training is expected to take 2-5 minutes
- Subsequent runs will load cached model
- Check logs with: `python src/model.py --verbose`

### Issue: Port 8501 already in use
**Solution:** Use different port
```bash
streamlit run app/main.py --server.port 8502
```

---

## Development Setup

### For Contributors

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Install dev dependencies
5. Make changes
6. Run tests
7. Submit pull request

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/IPL_Prediction_Dashboard.git
cd IPL_Prediction_Dashboard

# Create branch
git checkout -b feature/my-feature

# Install dev tools
pip install -r requirements.txt
pip install pytest black flake8

# Make your changes
# ... edit files ...

# Run tests
pytest

# Format code
black .

# Lint
flake8 src/ app/

# Commit and push
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

---

## Configuration

Edit `config/config.yaml` to customize:
- Model type (ensemble, logistic, random_forest)
- Feature engineering parameters
- Streamlit settings
- Data paths

---

## Next Steps

1. ✅ Install and run dashboard
2. 📊 Explore historical data
3. 🎯 Make predictions
4. 📈 Analyze team performance
5. 🔧 Customize features
6. 📤 Deploy online (Streamlit Cloud, Heroku, etc.)

---

## Deployment

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repository
4. Deploy!

### Deploy to Heroku

```bash
# Create Procfile
echo "web: streamlit run app/main.py --logger.level=error" > Procfile

# Deploy
git push heroku main
```

---

## Performance Tips

- First prediction: ~2-3 seconds
- Subsequent predictions: <1 second (cached model)
- Data loading: ~5-10 seconds
- Model training: 2-5 minutes (one-time)

---

For more help, see README.md or create an issue on GitHub!
