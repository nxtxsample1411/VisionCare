@echo off
title VisionCare All-in-One Engine
setlocal enabledelayedexpansion
color 0A

echo ============================================================
echo      VisionCare - Starting All Features (One Command)
echo ============================================================
echo.

:: Step 1: Updating Python dependencies
echo [1/4] Updating Python dependencies...
python -m pip install -r requirements.txt --quiet 2>nul
echo      Done.

:: Step 2: Updating Node.js dependencies
echo [2/4] Updating Node.js dependencies...
cd VisionCare-Backend
call npm install --quiet 2>nul
cd ..
echo      Done.

echo.
echo [3/4] Launching Background Services...
echo.

:: 1. Express Backend (Auth & History) - Port 5000
echo   [*] Auth/History Service        ... Port 5000
start "VisionCare - Auth/History (5000)" /min cmd /c "cd VisionCare-Backend && node server.js"

:: 2. Flask Backend (Eye Disease - Local Model) - Port 5001
echo   [*] Eye Disease AI              ... Port 5001
start "VisionCare - Eye Disease AI (5001)" /min cmd /c "cd VisionCare-Backend && python app.py"

:: 3. FastAPI Backend (Chat & Doctor Finder) - Port 8000
echo   [*] AI Chat + Doctor Finder     ... Port 8000
start "VisionCare - AI Features (8000)" /min cmd /c "cd VisionCare-Backend && uvicorn main:app --port 8000"

:: 4. Calibration Backend (WebSocket) - Port 8080
echo   [*] Distance Calibration (WS)   ... Port 8080
start "VisionCare - Calibration (8080)" /min cmd /c "cd VisionCare-Backend && python server.py"

:: Give services 3 seconds to boot up
echo.
echo [4/4] Waiting for services to initialize...
timeout /t 3 /nobreak >nul
echo      Done.

echo.
echo ============================================================
echo   ALL SERVICES RUNNING:
echo.
echo   Auth/History API     : http://localhost:5000
echo   Eye Disease AI       : http://localhost:5001
echo   AI Chat/Doctor API   : http://localhost:8000
echo   Distance Calibration : ws://localhost:8080
echo.
echo   Opening Frontend in Browser...
echo ============================================================
echo.

:: Open the frontend in default browser via Live Server URL
:: If Live Server is running, use it; otherwise open the file directly
start "" "http://127.0.0.1:5501/VisionCare/index.html"

echo.
echo ============================================================
echo   VisionCare is LIVE! Press any key to STOP all services.
echo ============================================================
pause

:: Kill all services on exit
echo.
echo Shutting down all services...
taskkill /FI "WINDOWTITLE eq VisionCare - *" /F >nul 2>&1
echo All services stopped. Goodbye!
timeout /t 2 /nobreak >nul
