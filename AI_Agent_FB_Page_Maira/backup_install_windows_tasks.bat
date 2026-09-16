@echo off
cd /d "%~dp0"
title Install Windows Scheduled Tasks - Facebook AI Agent (Maira Dash)
echo =======================================================================
echo     INSTALLING 5 DAILY SCHEDULED TASKS IN WINDOWS TASK SCHEDULER (IST)
echo                         FOR MAIRA DASH
echo =======================================================================
echo.
echo Project Directory: %~dp0
echo.

set VBS_RUNNER=%~dp0run_hidden.vbs

echo [1/5] Scheduling Good Morning at 06:30 AM IST...
schtasks /Create /TN "AI_Agent_FB_Page_Maira\01_GoodMorning" /TR "wscript.exe \"%VBS_RUNNER%\" morning" /SC DAILY /ST 06:30 /F >nul
if %errorlevel% equ 0 (
    echo     - Good Morning 06:30 scheduled successfully!
) else (
    echo     - Failed to schedule Good Morning!
)

echo [2/5] Scheduling Good Noon at 11:30 AM IST...
schtasks /Create /TN "AI_Agent_FB_Page_Maira\02_GoodNoon" /TR "wscript.exe \"%VBS_RUNNER%\" noon" /SC DAILY /ST 11:30 /F >nul
if %errorlevel% equ 0 (
    echo     - Good Noon 11:30 scheduled successfully!
) else (
    echo     - Failed to schedule Good Noon!
)

echo [3/5] Scheduling Good Afternoon at 03:30 PM (15:30) IST...
schtasks /Create /TN "AI_Agent_FB_Page_Maira\03_GoodAfternoon" /TR "wscript.exe \"%VBS_RUNNER%\" afternoon" /SC DAILY /ST 15:30 /F >nul
if %errorlevel% equ 0 (
    echo     - Good Afternoon 15:30 scheduled successfully!
) else (
    echo     - Failed to schedule Good Afternoon!
)

echo [4/5] Scheduling Good Evening at 06:30 PM (18:30) IST...
schtasks /Create /TN "AI_Agent_FB_Page_Maira\04_GoodEvening" /TR "wscript.exe \"%VBS_RUNNER%\" evening" /SC DAILY /ST 18:30 /F >nul
if %errorlevel% equ 0 (
    echo     - Good Evening 18:30 scheduled successfully!
) else (
    echo     - Failed to schedule Good Evening!
)

echo [5/5] Scheduling Good Night at 09:00 PM (21:00) IST...
schtasks /Create /TN "AI_Agent_FB_Page_Maira\05_GoodNight" /TR "wscript.exe \"%VBS_RUNNER%\" night" /SC DAILY /ST 21:00 /F >nul
if %errorlevel% equ 0 (
    echo     - Good Night 21:00 scheduled successfully!
) else (
    echo     - Failed to schedule Good Night!
)

echo.
echo =======================================================================
echo                     CURRENT REGISTERED TASKS
echo =======================================================================
schtasks /Query /TN "AI_Agent_FB_Page_Maira\01_GoodMorning" /FO TABLE
schtasks /Query /TN "AI_Agent_FB_Page_Maira\02_GoodNoon" /FO TABLE
schtasks /Query /TN "AI_Agent_FB_Page_Maira\03_GoodAfternoon" /FO TABLE
schtasks /Query /TN "AI_Agent_FB_Page_Maira\04_GoodEvening" /FO TABLE
schtasks /Query /TN "AI_Agent_FB_Page_Maira\05_GoodNight" /FO TABLE
echo.
echo All 5 daily automated tasks have been registered in Windows Task Scheduler!
echo The agent will now run on time automatically without keeping any terminal open.
echo.
pause
