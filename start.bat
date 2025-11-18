@echo off
REM Unitree G1 Windows Control Application Launcher
REM This script launches the application on Windows

echo ====================================
echo Unitree G1 Control Application
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Starting application...
echo.

REM Launch the application
python main.py

REM If the application exits with an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    echo Check the console output above for details.
    pause
)
