#!/bin/bash
###############################################################################
# CyberLink Security - Vectorizer.dev Backend Startup Script
# Starts the FastAPI backend server for image vectorization
###############################################################################

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    CYBERLINK SECURITY - VECTORIZER.DEV BACKEND SERVER     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "   Please install Python 3.8+ to continue"
    exit 1
fi

echo "✓ Python 3 detected: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment found"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ All dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🚀 STARTING BACKEND SERVER"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📍 API Server: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "💚 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "════════════════════════════════════════════════════════════"
echo ""

# Start the backend server
python3 api_server.py
