#!/bin/bash

# Finance Tracker - Quick Start Script
# This script sets up and runs the Finance Tracker application

echo "💰 Finance Tracker - Quick Start"
echo "================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file..."
    cp .env.example .env
    # Generate a random secret key
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    sed -i.bak "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    rm .env.bak 2>/dev/null
    echo "✅ .env file created with random SECRET_KEY"
else
    echo "✅ .env file already exists"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database initialized')"

# Ask if user wants to seed database
read -p "📊 Do you want to seed the database with sample data? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌱 Seeding database..."
    python3 seed_data.py
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🚀 Starting Finance Tracker..."
echo "   Access the application at: http://localhost:5000"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""
echo "================================="
echo ""

# Run the application
python3 app.py