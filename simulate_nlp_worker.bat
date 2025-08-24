@echo off
REM NLP Worker Service Simulator - Windows Batch File
REM This script runs the NLP Worker simulator

echo.
echo ========================================
echo   NLP Worker Service Simulator
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if the simulator script exists
if not exist "simulate_nlp_worker.py" (
    echo ❌ simulate_nlp_worker.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo 🚀 Starting NLP Worker Simulator...
echo.
echo Available modes:
echo   1. Test Messages (default) - Run predefined test messages
echo   2. Interactive Mode - Enter your own feedback messages
echo   3. Help - Show usage information
echo.

set /p choice="Choose mode (1-3, or press Enter for default): "

if "%choice%"=="1" (
    echo.
    echo 🧪 Running predefined test messages...
    python simulate_nlp_worker.py --test-messages
) else if "%choice%"=="2" (
    echo.
    echo 💬 Starting interactive mode...
    python simulate_nlp_worker.py --interactive
) else if "%choice%"=="3" (
    echo.
    echo 📚 Showing help...
    python simulate_nlp_worker.py --help
) else (
    echo.
    echo 🧪 Running predefined test messages (default)...
    python simulate_nlp_worker.py --test-messages
)

echo.
echo ========================================
echo   Simulation completed
echo ========================================
echo.
pause
