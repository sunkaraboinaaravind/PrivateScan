@echo off
title PrivateScan Desktop App
echo ===================================================
echo   🔒 PRIVATESCAN — DESKTOP APP (TKINTER)
echo ===================================================
echo.
echo Make sure Ollama is running ("ollama serve")
echo and you have pulled a model (e.g., "ollama pull llama3.2")
echo.
echo Launching application...
echo.

cd /d "%~dp0"
C:\Users\sunka\AppData\Local\Programs\Python\Python311\python.exe main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Something went wrong while running the desktop application.
    echo Please make sure dependencies are installed and Python 3.11 is configured.
)
pause
