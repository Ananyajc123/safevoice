@echo off
echo 🛡️  SafeVoice Phase 2 - Starting System
echo ========================================
echo.

REM Check if in correct directory
if not exist "backend\main.py" (
    echo ❌ Error: Please run this script from the project root directory
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed
    exit /b 1
)

echo ✅ Python found

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
cd backend
pip install -q -r requirements.txt

REM Run tests
echo.
echo 🧪 Running system tests...
python test_system.py

if errorlevel 1 (
    echo.
    echo ❌ System tests failed. Please fix the issues before starting.
    exit /b 1
)

echo.
echo 🚀 Starting SafeVoice server...
echo.
echo 📍 Access points:
echo    - Authentication: http://localhost:8000/auth.html
echo    - Main App: http://localhost:8000/
echo    - API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn main:app --reload --port 8000
