@echo off
cd /d "%~dp0"
call "%~dp0run_converter.bat"
if errorlevel 1 exit /b 1

call "%~dp0convert.bat" %*
