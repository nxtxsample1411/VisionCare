@echo off
echo ========================================
echo VisionCare Installation for Python 3.12
echo ========================================
echo.

echo Step 1: Upgrading pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel
echo.

echo Step 2: Installing dependencies...
pip install -r requirements.txt
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To run the backend:
echo   python app.py
echo.
pause
