@echo off
title Valorant Watcher

:START
:: -------------------------------
:: Launch Valorant Tracker FIRST
:: -------------------------------
echo Starting Valorant Tracker...
start "" "C:\Users\username\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Overwolf\Valorant Tracker.lnk"

timeout /t 5 >nul

:: -------------------------------
:: Launch Valorant
:: -------------------------------
echo Starting Valorant...
start "" "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Riot Games\VALORANT.lnk"

echo Waiting for Valorant to start. If it doesn't, try running it manually...

:WAIT_START
tasklist | find /I "VALORANT.exe" >nul
if xerrorlevel 1 (
    timeout /t 5 >nul
    goto WAIT_START
)

echo Valorant detected!
echo Game is running. Waiting for it to close...

:WAIT_CLOSE
tasklist | find /I "VALORANT.exe" >nul
if not errorlevel 1 (
    timeout /t 5 >nul
    goto WAIT_CLOSE
)

echo Valorant has closed.
echo Python automation script is starting...

python "C:\Users\username\OneDrive\Desktop\valorant auto\valorant_auto.py"
if errorlevel 1 goto RESTART
echo Python automation script has ended.

:: -------------------------------
:: CLEAN UP FILES
:: -------------------------------
echo.
echo Cleaning temporary files...

del /q /f "%TEMP%\list.txt" 2>nul
del /q /f "%TEMP%\valorant_highlights_*.mp4" 2>nul

echo Cleaning Valorant clip folders...

for /d %%D in ("C:\Users\username\Videos\Overwolf\Valorant Tracker\VALORANT\*") do (
    rd /s /q "%%D"
)

echo Cleanup complete.

:: -------------------------------
:: SHUTDOWN IN 1 MIN
:: -------------------------------
echo.
echo ----------------------------------------
echo PC will shut down in 1 MIN.
echo ----------------------------------------

shutdown /s /t 60

goto END

:: -------------------------------
:: RESTART PROMPT
:: -------------------------------
:RESTART
echo.
echo Python script failed!
echo Do you want to restart the whole process? (Y/N)
choice /C YN /N
if errorlevel 2 goto END
if errorlevel 1 goto WAIT_CLOSE

:END
pause
