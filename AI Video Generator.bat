@echo off
title AI Video Converter
cd /d "C:\Users\pagen\1REP AI GENAPP"

echo ======================================
echo AI VIDEO CONVERTER - AUTOMATED
echo ======================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo Error creating virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install required packages
echo.
echo Installing required packages...
pip install pillow opencv-python -q

REM Run the converter directly
echo.
echo Starting video conversion...
echo.
python auto_convert.py

echo.
echo ======================================
echo ✓ COMPLETE!
echo ======================================
echo.
pause
