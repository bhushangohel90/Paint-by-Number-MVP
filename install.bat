@echo off
echo ===================================================
echo Paint by Number Generator - Installation
echo ===================================================
echo.
echo This script will install all required dependencies.
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher from https://www.python.org/downloads/
    echo and make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python is installed. Installing dependencies...
echo.

REM Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
if %errorlevel% neq 0 (
    echo There was an error installing dependencies.
    echo Please check the error messages above.
) else (
    echo All dependencies installed successfully!
    echo.
    echo You can now run the application with:
    echo run_app.bat
)

echo.
pause
