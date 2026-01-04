@echo off
title GPU Mining Suite
echo Starting GPU Mining Suite...
echo.
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop
echo.
cd ..
python backend/app.py
pause
