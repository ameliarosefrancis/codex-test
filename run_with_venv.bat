@echo off
REM AmeliaRoseCo Toolkit - Launch with Virtual Environment
REM This script activates the venv and runs the application

echo.
echo ========================================
echo AmeliaRoseCo Toolkit - Launching...
echo ========================================
echo.

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo.
    echo To create venv, run:
    echo   python -m venv venv
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated
echo.

REM Run the application
echo Starting application...
python app_gui.py

REM Pause to see any errors
pause
