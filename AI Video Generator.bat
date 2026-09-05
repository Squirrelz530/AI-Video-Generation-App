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

REM Download the converter script
echo.
echo Downloading converter script...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/Squirrelz530/AI-Video-Generation-App/main/auto_convert.py' -OutFile 'auto_convert.py'"

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
