@echo off
echo ================================================
echo GPU Mining Suite - Setup Autostart
echo ================================================
echo.
echo This script will configure GPU Mining Suite to start
echo automatically when Windows boots.
echo.
echo WARNING: Mining will start automatically on boot!
echo Make sure your configuration is correct first.
echo.
pause

REM Get current directory
set SCRIPT_DIR=%~dp0
set APP_DIR=%SCRIPT_DIR%..

REM Create VBS script to run without window
set VBS_FILE=%TEMP%\start_mining_hidden.vbs
echo Set WshShell = CreateObject("WScript.Shell") > %VBS_FILE%
echo WshShell.Run "cmd /c cd /d %APP_DIR% && python backend/app.py", 0, False >> %VBS_FILE%

REM Create startup shortcut
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT=%STARTUP_DIR%\GPU Mining Suite.lnk

echo Creating startup shortcut...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%VBS_FILE%'; $s.WorkingDirectory = '%APP_DIR%'; $s.Save()"

echo.
echo ================================================
echo Autostart Configured!
echo ================================================
echo.
echo GPU Mining Suite will now start automatically when Windows boots.
echo.
echo To disable: Delete the shortcut from:
echo %STARTUP_DIR%
echo.
pause
