@echo off
title VisionCare All-in-One Launcher
echo ============================================================
echo           VisionCare All-in-One System Launcher
echo ============================================================
echo.

:: Check for Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js to continue.
    pause
    exit /b
)

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python to continue.
    pause
    exit /b
)

:: Activate Virtual Environment if it exists
if exist venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Install root dependencies (concurrently, serve)
echo [INFO] Installing system dependencies...
call npm install

:: Install backend Node dependencies
echo [INFO] Installing backend Node dependencies...
cd VisionCare-Backend
call npm install
cd ..

:: Install Python dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo ============================================================
echo  Starting all services...
echo  - Frontend: http://localhost:3000
echo  - Auth/History (Node): Port 5000
echo  - Prediction (Flask): Port 5001
echo  - AI/Groq (FastAPI): Port 8000
echo  - Calibration (WS): Port 8080
echo ============================================================
echo.

:: Run all services
npm start

pause
