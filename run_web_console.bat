@echo off
title PrivateScan Web Console
echo ===================================================
echo   🔒 PRIVATESCAN — WEB CONSOLE
echo ===================================================
echo.
echo Make sure Ollama is running ("ollama serve")
echo and you have pulled a model (e.g., "ollama pull llama3.2")
echo.
echo Launching server...
echo.

cd /d "%~dp0"
C:\Users\sunka\AppData\Local\Programs\Python\Python311\python.exe web_app.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Something went wrong while running the web application.
    echo Please make sure dependencies are installed and Python 3.11 is configured.
)
pause
