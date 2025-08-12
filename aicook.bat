@ECHO OFF
CHCP 65001 > NUL
TITLE AI-Cook Quick Start

:: =================================================================
::  AI-Cook & AI-Meal-Coach - Quick Start Script
::  Activates the existing venv and starts all services without installing dependencies.
::  NOTE: Run firststart.bat first if the .venv directory does not exist.
:: =================================================================

ECHO.
ECHO [AI-Cook] Quick starting all services...
ECHO.

:: Check Virtual Environment
IF NOT EXIST ".venv\Scripts\activate.bat" (
    ECHO [ERROR] Virtual environment not found. Please run firststart.bat first to set it up.
    PAUSE
    EXIT /B 1
)

:: Update recipes.json from CSV (background)
ECHO [INFO] Updating recipes.json from CSV...
node --version >NUL 2>&1
IF NOT ERRORLEVEL 1 (
    START /MIN CMD /C "node src\scripts\convertRecipes.js"
    ECHO [OK] CSV update started in background
) ELSE (
    ECHO [WARN] Node.js not found, skipping CSV update
)

:: Start all services
ECHO.
ECHO [INFO] Starting all services...

START "AI-Cook Main API" CMD /K "CALL .venv\Scripts\activate.bat && cd aire-backend && python -m app.main"

TIMEOUT /T 2 /NOBREAK >NUL

START "AI-Cook Search API" CMD /K "CALL .venv\Scripts\activate.bat && uvicorn searchbackend.main:app --host 0.0.0.0 --port 8080"

TIMEOUT /T 2 /NOBREAK >NUL

START "AI-Cook Frontend" CMD /K "npm run dev"

:: Final message
ECHO.
ECHO =================================================================
ECHO  [SUCCESS] All services are launching!
ECHO.
ECHO  - Main Application: http://localhost:3001
ECHO  - Main API Docs:    http://localhost:8000/docs
ECHO  - Search API Docs:  http://localhost:8080/docs
ECHO.
ECHO  Please wait for all services to start completely.
ECHO =================================================================
ECHO.

PAUSE