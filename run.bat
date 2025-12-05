@echo off
REM Finance Tracker - Quick Start Script for Windows

echo 💰 Finance Tracker - Quick Start
echo =================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -q -r requirements.txt
echo ✅ Dependencies installed

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 🔧 Creating .env file...
    copy .env.example .env
    echo ✅ .env file created - Please update SECRET_KEY in .env
) else (
    echo ✅ .env file already exists
)

REM Initialize database
echo 🗄️  Initializing database...
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database initialized')"

REM Ask if user wants to seed database
set /p SEED="📊 Do you want to seed the database with sample data? (y/n): "
if /i "%SEED%"=="y" (
    echo 🌱 Seeding database...
    python seed_data.py
)

echo.
echo 🎉 Setup complete!
echo.
echo 🚀 Starting Finance Tracker...
echo    Access the application at: http://localhost:5000
echo.
echo    Press Ctrl+C to stop the server
echo.
echo =================================
echo.

REM Run the application
python app.py

pause