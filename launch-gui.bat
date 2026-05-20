@echo off
REM ThreatIntel Daily GUI Launcher for Windows

echo Launching ThreatIntel Daily...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements-gui.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Launch the GUI
python -m threatintel_daily.gui

pause
