#!/bin/bash

# Start backend from project root so imports work
cd "$(dirname "$0")"

# Check for .env
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please create one from .env.example"
    exit 1
fi

# Export environment variables
export $(cat .env | grep -v '^#' | xargs)

# Add backend to PYTHONPATH
export PYTHONPATH="${PWD}:${PWD}/backend:${PWD}/src:${PYTHONPATH}"

echo "Starting Core Cartographer Backend..."
echo "API will be available at http://localhost:8000"
echo "Docs available at http://localhost:8000/docs"
echo ""

cd backend
source venv/bin/activate
cd ..
uvicorn backend.src.api.main:app --reload --host 0.0.0.0 --port 8000
