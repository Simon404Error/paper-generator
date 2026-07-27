@echo off
chcp 65001 >nul 2>&1
title Paper Generator

echo.
echo   ============================
echo   Paper Generator v1.0
echo   ============================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ first.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing Flask...
    pip install flask -q
    if errorlevel 1 (
        echo [ERROR] Flask install failed. Run: pip install flask
        pause
        exit /b 1
    )
)

echo [START] http://localhost:5000
echo Press Ctrl+C to stop
echo.

start "" http://localhost:5000
python app.py
pause
