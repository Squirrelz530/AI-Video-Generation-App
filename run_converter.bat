@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1

python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

if not exist "input\images" (
    mkdir "input\images"
    if errorlevel 1 exit /b 1
)

if not exist "output" (
    mkdir "output"
    if errorlevel 1 exit /b 1
)

echo Setup complete. Put scene images in input\images\ and run AI Video Generator.bat.
exit /b 0
