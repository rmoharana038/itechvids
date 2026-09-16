@echo off
cd /d "%~dp0"
title Uninstall Windows Scheduled Tasks - Facebook AI Agent (Maira Dash)
echo =======================================================================
echo          UNINSTALLING WINDOWS SCHEDULED TASKS - MAIRA DASH
echo =======================================================================
echo.
echo Removing all 5 tasks from Windows Task Scheduler (AI_Agent_FB_Page_Maira)...

schtasks /Delete /TN "AI_Agent_FB_Page_Maira\01_GoodMorning" /F >nul 2>&1
schtasks /Delete /TN "AI_Agent_FB_Page_Maira\02_GoodNoon" /F >nul 2>&1
schtasks /Delete /TN "AI_Agent_FB_Page_Maira\03_GoodAfternoon" /F >nul 2>&1
schtasks /Delete /TN "AI_Agent_FB_Page_Maira\04_GoodEvening" /F >nul 2>&1
schtasks /Delete /TN "AI_Agent_FB_Page_Maira\05_GoodNight" /F >nul 2>&1

echo.
echo All scheduled tasks for AI_Agent_FB_Page_Maira have been deleted.
echo.
pause
