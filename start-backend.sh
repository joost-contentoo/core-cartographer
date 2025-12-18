#!/bin/bash
# Start the FastAPI backend

echo "🚀 Starting Core Cartographer Backend..."
echo ""

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No virtual environment detected. Activating .venv..."
    source .venv/bin/activate
fi

# Install backend dependencies if needed
echo "📦 Checking backend dependencies..."
cd backend
pip install -q -r requirements.txt

# Start the backend server
echo ""
echo "✓ Backend starting at http://localhost:8000"
echo "✓ API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd ..
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn backend.src.api.main:app --host 0.0.0.0 --port 8000 --reload
