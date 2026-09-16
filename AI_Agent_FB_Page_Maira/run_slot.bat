@echo off
cd /d "%~dp0"
set SLOT=%1
if "%SLOT%"=="" set SLOT=morning
echo [%DATE% %TIME%] Running scheduled slot: %SLOT% >> logs\windows_task.log
.\venv\Scripts\python.exe main.py --post-now %SLOT% >> logs\windows_task.log 2>&1
