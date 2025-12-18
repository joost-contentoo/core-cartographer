#!/bin/bash
# Start the Next.js frontend

echo "🎨 Starting Core Cartographer Frontend..."
echo ""

cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo ""
echo "✓ Frontend starting at http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

npm run dev
