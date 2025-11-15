#!/bin/bash

# Start both backend and frontend

echo "🚀 Starting VC Investor Voice Agent..."

# Start backend in background
echo "📡 Starting backend on port 8000..."
cd /Users/mira/Desktop/Mira/Hackaton
source venv/bin/activate
python run.py &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on port 8080..."
cd pitch-perfect-ai
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both services started!"
echo "📡 Backend: http://localhost:8000 (PID: $BACKEND_PID)"
echo "🎨 Frontend: http://localhost:8080 (PID: $FRONTEND_PID)"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
