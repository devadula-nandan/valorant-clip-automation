@echo off
title Valorant Watcher

:: -------------------------------
:: Launch Valorant
:: -------------------------------
echo Starting Valorant...

:: Path to your Valorant game shortcut
start "" "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Riot Games\VALORANT.lnk"

echo Waiting for Valorant to start...

:: -------------------------------
:: Wait until Valorant is running
:: -------------------------------
:WAIT_START
tasklist | find /I "VALORANT.exe" >nul
if errorlevel 1 (
    timeout /t 5 >nul
    goto WAIT_START
)

echo Valorant detected!
echo Starting Valorant Tracker...

:: Path to your Valorant Tracker shortcut
start "" "C:\Users\username\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Overwolf\Valorant Tracker.lnk"

echo Game is running. Waiting for it to close...

:: -------------------------------
:: Wait until Valorant closes
:: -------------------------------
:WAIT_CLOSE
tasklist | find /I "VALORANT.exe" >nul
if not errorlevel 1 (
    timeout /t 5 >nul
    goto WAIT_CLOSE
)

echo Valorant has closed.
echo Launching highlight automation...

:: Run the Python automation script
python "C:\Users\username\OneDrive\Desktop\valorant auto\valorant_auto.py"

echo Process complete.
pause
