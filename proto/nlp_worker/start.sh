#!/bin/bash

# NLP Worker Service Startup Script

echo "🚀 Starting NLP Worker Service..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Try clean installation first
echo "📚 Installing clean dependencies..."
if pip install -r requirements-clean.txt; then
    echo "✅ Clean dependencies installed successfully"
else
    echo "⚠️  Clean installation failed, trying minimal requirements..."
    if pip install -r requirements-minimal.txt; then
        echo "✅ Minimal dependencies installed successfully"
    else
        echo "❌ Failed to install dependencies. Please check your Python environment."
        exit 1
    fi
fi

# Download NLTK data (required)
echo "🤖 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"

# Try to download spaCy model (optional)
echo "🔍 Checking for spaCy..."
if python -c "import spacy" 2>/dev/null; then
    echo "📥 Downloading spaCy model..."
    python -m spacy download en_core_web_sm || echo "⚠️  Could not download spaCy model, continuing with NLTK only"
else
    echo "ℹ️  spaCy not available, will use NLTK only"
fi

# Check if MongoDB is accessible
echo "🗄️  Checking MongoDB connection..."
if ! python -c "import pymongo; pymongo.MongoClient('mongodb://localhost:27017').server_info()" 2>/dev/null; then
    echo "⚠️  Warning: MongoDB connection failed. Make sure MongoDB is running."
    echo "   You can start MongoDB with: docker run -d -p 27017:27017 mongo:latest"
fi

# Start the service
echo "🎯 Starting service..."
echo "   - gRPC Server: localhost:5003"
echo "   - Health Checks: localhost:3003"
echo "   - Metrics: localhost:8003"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

python cmd/main.py
