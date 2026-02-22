#!/bin/bash

# Setup.sh - One-time setup script

echo "========================================="
echo "📦 Telegram Video Uploader - Setup"
echo "========================================="
echo ""

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x start_uploader.sh
chmod +x keep_alive.sh
echo "✅ Done"

# Create directories
echo "📁 Creating directories..."
mkdir -p downloads
mkdir -p logs
echo "✅ Done"

# Check Python installation
echo "🐍 Checking Python..."
if command -v python3 &>/dev/null; then
    echo "✅ Python $(python3 --version) found"
else
    echo "❌ Python not found. Please install Python 3.7+"
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Done"

# Check for .env file
echo ""
echo "🔐 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your credentials!"
else
    echo "✅ .env file found"
fi

echo ""
echo "========================================="
echo "✅ Setup completed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Add your links.txt file to this directory"
echo "3. Run: ./start_uploader.sh"
echo ""
