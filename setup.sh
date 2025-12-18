#!/bin/bash

# Core Cartographer Setup Script
# This script helps set up the development environment

set -e

echo "🚀 Core Cartographer Setup"
echo "=========================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Check if ANTHROPIC_API_KEY is set
if grep -q "your_anthropic_api_key_here" .env 2>/dev/null; then
    echo "⚠️  WARNING: ANTHROPIC_API_KEY not set in .env"
    echo "   Please edit .env and add your API key before running the application"
    echo ""
fi

# Create frontend .env.local if it doesn't exist
if [ ! -f frontend/.env.local ]; then
    echo "📝 Creating frontend/.env.local..."
    cp frontend/.env.local.example frontend/.env.local
    echo "✅ Frontend environment configured"
    echo ""
fi

echo "🏗️  Building Docker containers..."
docker-compose build

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application, run:"
echo "  docker-compose up"
echo ""
echo "Then access:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
