@echo off
REM Installation script for Unitree G1 Windows Control Application

echo ====================================
echo Unitree G1 Control Application
echo Installation Script
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

echo Python found:
python --version
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install requirements
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
echo.

REM Try to install Unitree SDK
echo Installing Unitree SDK (this may fail if not available)...
pip install unitree_sdk2py
if errorlevel 1 (
    echo.
    echo WARNING: Unitree SDK installation failed
    echo The application will run in simulation mode
    echo.
    echo To install manually, follow instructions at:
    echo https://github.com/unitreerobotics/unitree_sdk2_python
    echo.
)

REM Install PyAudio for Windows (optional)
echo.
echo Installing PyAudio for voice control (optional)...
pip install pipwin
pipwin install pyaudio
if errorlevel 1 (
    echo PyAudio installation failed, voice control may not work
)

echo.
echo ====================================
echo Installation Complete!
echo ====================================
echo.
echo To start the application, run: start.bat
echo Or run: python main.py
echo.
pause
