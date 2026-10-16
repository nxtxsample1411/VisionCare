@echo off
title VisionCare All-in-One Terminal
:: Step 1: Activate the virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist ..\venv\Scripts\activate.bat (
    call ..\venv\Scripts\activate.bat
)

:: Step 2: Navigate to backend
if exist VisionCare-Backend cd VisionCare-Backend

:: Step 3: Run all services with concurrently
npx concurrently --kill-others "node server.js" "python app.py" "uvicorn main:app --port 8000" "python server.py"
pause
