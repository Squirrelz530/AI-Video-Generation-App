@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" (
    echo Run run_converter.bat first to create the virtual environment.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
python auto_convert.py %*
pause
