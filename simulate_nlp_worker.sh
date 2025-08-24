#!/bin/bash

# NLP Worker Service Simulator - Unix Shell Script
# This script runs the NLP Worker simulator

echo
echo "========================================"
echo "  NLP Worker Service Simulator"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.11+ and try again"
    exit 1
fi

# Check if the simulator script exists
if [ ! -f "simulate_nlp_worker.py" ]; then
    echo "❌ simulate_nlp_worker.py not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Make the script executable
chmod +x simulate_nlp_worker.py

echo "🚀 Starting NLP Worker Simulator..."
echo
echo "Available modes:"
echo "  1. Test Messages (default) - Run predefined test messages"
echo "  2. Interactive Mode - Enter your own feedback messages"
echo "  3. Help - Show usage information"
echo

read -p "Choose mode (1-3, or press Enter for default): " choice

case $choice in
    1)
        echo
        echo "🧪 Running predefined test messages..."
        python3 simulate_nlp_worker.py --test-messages
        ;;
    2)
        echo
        echo "💬 Starting interactive mode..."
        python3 simulate_nlp_worker.py --interactive
        ;;
    3)
        echo
        echo "📚 Showing help..."
        python3 simulate_nlp_worker.py --help
        ;;
    *)
        echo
        echo "🧪 Running predefined test messages (default)..."
        python3 simulate_nlp_worker.py --test-messages
        ;;
esac

echo
echo "========================================"
echo "  Simulation completed"
echo "========================================"
echo
