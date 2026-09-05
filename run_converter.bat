@echo off
REM Automated Video Converter Batch Script
REM This script handles the entire video conversion workflow

echo ======================================
echo AI VIDEO CONVERTER - AUTOMATED
echo ======================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error activating virtual environment
    pause
    exit /b 1
)

REM Download the converter script
echo.
echo Downloading converter script...
curl -o auto_convert.py https://raw.githubusercontent.com/Squirrelz530/AI-Video-Generation-App/main/auto_convert.py
if %errorlevel% neq 0 (
    echo Error downloading script
    pause
    exit /b 1
)

REM Run the converter
echo.
echo Starting video conversion...
echo.
python auto_convert.py

REM Check if conversion succeeded
if %errorlevel% neq 0 (
    echo.
    echo Error during conversion
    pause
    exit /b 1
)

echo.
echo ======================================
echo ✓ COMPLETE!
echo ======================================
echo.
pause
