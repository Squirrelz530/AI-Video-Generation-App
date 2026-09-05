@echo off
cd /d "%~dp0"
call run_converter.bat
if errorlevel 1 exit /b 1
call convert.bat %*
