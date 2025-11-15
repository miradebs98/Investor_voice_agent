#!/bin/bash
# Quick activation script for the virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Ready to go! Run: python run.py"

