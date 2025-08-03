#!/bin/bash

echo "🤖 Starting AI-Powered Meeting Scheduler..."
echo ""

# Check if MongoDB is running
if ! brew services list | grep -q "mongodb-community.*started"; then
    echo "⚠️  MongoDB is not running. Starting MongoDB..."
    brew services start mongodb-community
    sleep 3
fi

# Start backend
echo "🚀 Starting Backend Server (Flask + MongoDB)..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Frontend Server (React)..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application is starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:5000"
echo "🗄️  MongoDB: Running locally"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user to stop
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait 