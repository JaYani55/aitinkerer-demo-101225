@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 Job Metadata Generator - Startup Script
echo ============================================================
echo.

:: Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo ⚠️  Virtual environment not found!
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment!
        echo    Make sure Python is installed and in PATH.
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created.
    echo.
)

:: Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated.
echo.

:: Check if requirements are installed
echo 📋 Checking installed packages...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Required packages not found!
    echo 📦 Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install requirements!
        pause
        exit /b 1
    )
    echo ✅ All packages installed.
    echo.
) else (
    echo ✅ Required packages are installed.
    echo.
)

:: Check for .env file
if not exist ".env" (
    echo ⚠️  Warning: .env file not found!
    echo    Create a .env file with OPENAI_API_KEY=your_key
    echo.
)

:: Run Streamlit
echo ============================================================
echo 🎨 Starting Streamlit App...
echo ============================================================
echo.
streamlit run main.py

pause
