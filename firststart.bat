@echo off
title AI-Cook Setup Launcher

echo.
echo ==========================================
echo AI-Cook Setup Launcher  
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found in PATH
    echo.
    echo Please install Python 3.9+ and make sure it's in your PATH
    echo You can download Python from: https://python.org/downloads/
    echo.
    echo After installing Python, restart this script.
    echo.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "setup.py" (
    echo setup.py not found
    echo.
    echo Please make sure you're running this from the AI-Cook root directory
    echo.
    pause
    exit /b 1
)

REM Run Python setup script for dependencies only
echo Running dependency installation and verification...
echo.

python setup.py --no-services

REM Check if setup was successful
if errorlevel 1 (
    echo.
    echo Dependency setup failed. Please check the errors above.
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Starting AI-Cook Services...
echo ==========================================
echo.

REM Update recipes.json from CSV first
echo Updating recipes.json from CSV...
node --version >nul 2>&1
if not errorlevel 1 (
    node src\scripts\convertRecipes.js
    if not errorlevel 1 (
        echo [OK] recipes.json updated successfully
    ) else (
        echo [WARN] CSV update failed, continuing with service startup
    )
) else (
    echo [WARN] Node.js not found, skipping CSV update
)

REM Start AI Backend in new window
echo Starting AI Backend API...
start "AI-Cook Main API" cmd /k "cd /d "%~dp0\aire-backend" && "%~dp0.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait a moment between service starts
timeout /t 3 /nobreak >nul

REM Start Search Backend in new window  
echo Starting Search Backend API...
start "AI-Cook Search API" cmd /k "cd /d "%~dp0" && .venv\Scripts\python.exe -m uvicorn searchbackend.main:app --host 0.0.0.0 --port 8080 --reload"

REM Wait a moment between service starts
timeout /t 3 /nobreak >nul

REM Start Frontend in new window
echo Starting Frontend...
start "AI-Cook Frontend" cmd /k "cd /d "%~dp0" && npm run dev"

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo All services are starting in separate windows:
echo.
echo * AI Backend API:    http://localhost:8000/docs
echo * Search Backend:    http://localhost:8080/docs  
echo * Frontend:          http://localhost:3001
echo.
echo Services may take a moment to start up completely.
echo Check the opened windows for any error messages.
echo.
echo Press any key to exit this launcher...
pause >nul