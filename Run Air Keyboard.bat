@echo off
title Cyber Air Keyboard
color 0A
echo.
echo  ============================================
echo   CYBER AIR KEYBOARD - Launching...
echo  ============================================
echo.

:: Change to the directory of this script
cd /d "%~dp0"

:: Create venv if it doesn't exist
if not exist "venv\Scripts\python.exe" (
    echo  [SETUP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo  [ERROR] Could not create venv. Is Python 3.11/3.12 installed?
        pause
        exit /b 1
    )
    echo  [SETUP] Installing dependencies (first run, please wait)...
    venv\Scripts\pip install -r requirements.txt
    if errorlevel 1 (
        echo  [ERROR] Dependency install failed. Check requirements.txt
        pause
        exit /b 1
    )
)

echo  [OK] Activating environment...
call venv\Scripts\activate.bat

echo  [OK] Starting Cyber Air Keyboard...
echo.
python air_keyboard.py

echo.
echo  [DONE] Session ended.
pause
