@echo off
echo ================================================
echo GPU Mining Suite - Installation
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python --version

echo.
echo [2/4] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [3/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [4/4] Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "miners" mkdir miners

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Download mining software (see miners/README.md)
echo 2. Edit configs/settings.json with your wallet address
echo 3. Run: python backend/app.py
echo 4. Open browser: http://localhost:5000
echo.
pause
