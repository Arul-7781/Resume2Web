#!/bin/bash

# Portfolio Builder - Quick Start Script
# This script sets up your development environment

set -e  # Exit on error

echo "🚀 Portfolio Builder - Quick Start Setup"
echo "========================================"
echo ""

# Check Python version
echo "📌 Checking Python version..."
python3 --version || {
    echo "❌ Python 3.10+ is required"
    exit 1
}

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
echo ""
echo "🔑 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - GEMINI_API_KEY (get from https://makersuite.google.com/app/apikey)"
    echo "   - NETLIFY_ACCESS_TOKEN (get from https://app.netlify.com)"
    echo ""
else
    echo "✅ .env file exists"
fi

# Verify installation
echo ""
echo "🧪 Verifying installation..."
python3 -c "import fastapi, pydantic, google.generativeai, weasyprint" && {
    echo "✅ All dependencies installed correctly"
} || {
    echo "❌ Some dependencies failed to install"
    exit 1
}

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env and add your API keys"
echo "   2. Run: uvicorn app.main:app --reload"
echo "   3. Visit: http://localhost:8000/docs"
echo ""
echo "📚 Documentation:"
echo "   - SETUP_GUIDE.md - Detailed setup instructions"
echo "   - ARCHITECTURE.md - System design and patterns"
echo "   - CHAIN_OF_THOUGHT.md - AI prompting techniques"
echo "   - LEARNING_SUMMARY.md - Concepts and skills learned"
echo ""
echo "Happy coding! 🎉"
