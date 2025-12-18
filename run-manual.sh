#!/bin/bash
# Manual startup guide for Core Cartographer

echo "════════════════════════════════════════════════════════════"
echo "   Core Cartographer - Manual Startup Guide"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Since Docker is not installed, you'll need to run the backend"
echo "and frontend in separate terminal windows."
echo ""
echo "📋 INSTRUCTIONS:"
echo ""
echo "1️⃣  In THIS terminal, run:"
echo "   ./start-backend.sh"
echo ""
echo "2️⃣  In a SECOND terminal, run:"
echo "   cd $(pwd)"
echo "   ./start-frontend.sh"
echo ""
echo "3️⃣  Open your browser to:"
echo "   http://localhost:3000"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
read -p "Press Enter to start the backend now (or Ctrl+C to exit)..."
echo ""

./start-backend.sh
