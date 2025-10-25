#!/bin/bash
###############################################################################
# CyberLink Security - Full-Stack Vectorizer Startup Script
# Starts both backend (FastAPI) and frontend (Vite/React)
###############################################################################

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       CYBERLINK SECURITY - VECTORIZER.DEV FULL STACK      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Check if backend port is available
if check_port 8000; then
    echo -e "${RED}⚠️  Port 8000 is already in use${NC}"
    echo "   Kill the process or change the backend port"
    echo ""
    read -p "Kill existing process on port 8000? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✓ Killed process on port 8000${NC}"
        sleep 1
    else
        exit 1
    fi
fi

# Check if frontend port is available
if check_port 5173; then
    echo -e "${RED}⚠️  Port 5173 is already in use${NC}"
    echo "   Kill the process or change the frontend port"
    echo ""
    read -p "Kill existing process on port 5173? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:5173 | xargs kill -9 2>/dev/null
        echo -e "${GREEN}✓ Killed process on port 5173${NC}"
        sleep 1
    else
        exit 1
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "STEP 1/3: INSTALLING FRONTEND DEPENDENCIES"
echo "════════════════════════════════════════════════════════════"
echo ""

# Install frontend dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "STEP 2/3: STARTING BACKEND SERVER"
echo "════════════════════════════════════════════════════════════"
echo ""

# Start backend in background
cd backend_processor

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 detected: $(python3 --version)${NC}"

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv and install dependencies
source venv/bin/activate
echo "📥 Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install backend dependencies${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🚀 Starting Backend API Server...${NC}"
python3 api_server.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

# Wait for backend to start
sleep 3

# Check if backend is running
if check_port 8000; then
    echo -e "${GREEN}✓ Backend server started (PID: $BACKEND_PID)${NC}"
    echo -e "   API: ${BLUE}http://localhost:8000${NC}"
    echo -e "   Docs: ${BLUE}http://localhost:8000/docs${NC}"
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "   Check backend.log for errors"
    exit 1
fi

cd ..

echo ""
echo "════════════════════════════════════════════════════════════"
echo "STEP 3/3: STARTING FRONTEND SERVER"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${BLUE}🚀 Starting Frontend Development Server...${NC}"
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid

# Wait for frontend to start
sleep 3

# Check if frontend is running
if check_port 5173; then
    echo -e "${GREEN}✓ Frontend server started (PID: $FRONTEND_PID)${NC}"
    echo -e "   App: ${BLUE}http://localhost:5173${NC}"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
    echo "   Check frontend.log for errors"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    🎉 SERVERS RUNNING!                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✓ Backend:${NC}  http://localhost:8000 (PID: $BACKEND_PID)"
echo -e "${GREEN}✓ Frontend:${NC} http://localhost:5173 (PID: $FRONTEND_PID)"
echo ""
echo "📖 API Docs:    http://localhost:8000/docs"
echo "💚 Health:      http://localhost:8000/health"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop both servers, run:"
echo "   ./stop_fullstack.sh"
echo ""
echo "🌐 Opening application in browser..."
sleep 2

# Open browser (works on most Linux systems)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173 2>/dev/null &
elif command -v gnome-open &> /dev/null; then
    gnome-open http://localhost:5173 2>/dev/null &
elif command -v firefox &> /dev/null; then
    firefox http://localhost:5173 2>/dev/null &
elif command -v google-chrome &> /dev/null; then
    google-chrome http://localhost:5173 2>/dev/null &
fi

echo ""
echo "✨ Full-stack application is ready!"
echo "   Press Ctrl+C to stop (or use ./stop_fullstack.sh)"
echo ""

# Keep script running and monitor processes
trap 'echo ""; echo "Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT TERM

# Wait for processes
wait
