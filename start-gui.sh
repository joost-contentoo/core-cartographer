#!/bin/bash

# Core Cartographer GUI Launcher

echo "🗺️  Launching Core Cartographer GUI..."
echo ""

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please copy .env.example to .env and add your API key"
    echo ""
    read -p "Press Enter to continue anyway..."
fi

# Launch Streamlit GUI
echo "Starting Streamlit..."
echo "The GUI will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run src/core_cartographer/gui.py
