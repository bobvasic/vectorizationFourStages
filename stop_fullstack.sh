#!/bin/bash
###############################################################################
# CyberLink Security - Stop Full-Stack Vectorizer
###############################################################################

echo "🛑 Stopping Full-Stack Application..."
echo ""

# Kill backend if PID file exists
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo "✓ Backend server stopped (PID: $BACKEND_PID)"
    fi
    rm backend.pid
fi

# Kill frontend if PID file exists
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✓ Frontend server stopped (PID: $FRONTEND_PID)"
    fi
    rm frontend.pid
fi

# Fallback: kill by port
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

echo ""
echo "✓ All servers stopped"
