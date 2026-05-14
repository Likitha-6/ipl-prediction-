#!/bin/bash
# GitHub Repository Setup Script
# Run this after creating a new repository on GitHub

echo "======================================"
echo "IPL Prediction Dashboard - GitHub Setup"
echo "======================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Get repository URL
echo "Enter your GitHub repository URL:"
echo "Example: https://github.com/yourusername/IPL_Prediction_Dashboard.git"
read REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Repository URL is required."
    exit 1
fi

# Initialize git
echo ""
echo "Initializing git repository..."
git init

# Add remote
echo "Adding remote repository..."
git remote add origin $REPO_URL

# Create initial commit
echo ""
echo "Creating initial commit..."
git add .
git commit -m "Initial commit: IPL Prediction Dashboard

- Data loading and preprocessing
- Feature engineering for ML
- ML model training and prediction
- Streamlit web dashboard
- Comprehensive documentation"

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "======================================"
echo "✅ Repository initialized successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Go to: $REPO_URL"
echo "2. Add collaborators if needed"
echo "3. Enable GitHub Pages for documentation"
echo "4. Set up CI/CD (optional)"
echo ""
echo "To clone this repository later:"
echo "  git clone $REPO_URL"
