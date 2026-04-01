#!/bin/bash

echo "🛡️  SafeVoice Phase 2 - Starting System"
echo "========================================"
echo ""

# Check if in backend directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
cd backend
pip install -q -r requirements.txt

# Run tests
echo ""
echo "🧪 Running system tests..."
python3 test_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting SafeVoice server..."
    echo ""
    echo "📍 Access points:"
    echo "   - Authentication: http://localhost:8000/auth.html"
    echo "   - Main App: http://localhost:8000/"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    uvicorn main:app --reload --port 8000
else
    echo ""
    echo "❌ System tests failed. Please fix the issues before starting."
    exit 1
fi
