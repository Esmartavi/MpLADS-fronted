@echo off
setlocal
cd /d "%~dp0"
echo ================================================================================
echo   BHARAT-DRISHTI // National MPLADS AI Vigilance System (PS 26102)
echo   Launching All Services (FastAPI + Vite + Pipeline Worker)...
echo ================================================================================
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
endlocal
