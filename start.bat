@echo off
setlocal
cd /d "%~dp0"
echo ================================================================================
echo   BHARAT-DRISHTI // National MPLADS AI Vigilance System
echo   Launching All Services (FastAPI + Vite + Pipeline Worker)...
echo ================================================================================
REM ── Check if fraud_flags.csv exists; auto-run ML pipeline if missing ────────
if not exist "data\processed\fraud_flags.csv" (
    echo.
    echo [!] Missing dataset: data\processed\fraud_flags.csv
    echo [*] Automatically executing ML Fraud Detection Pipeline...
    
    set "PY_CMD=python"
    if exist "venv\Scripts\python.exe" (
        set "PY_CMD=venv\Scripts\python.exe"
    )

    REM Ensure clean data files exist; run clean_data.py if missing
    if not exist "data\processed\clean_sanctioned.csv" (
        echo [*] Clean datasets missing. Running clean_data.py first...
        "%PY_CMD%" pipelines\clean_data.py
    )

    echo [*] Executing pipelines\fraud_models.py...
    "%PY_CMD%" pipelines\fraud_models.py

    if errorlevel 1 (
        echo.
        echo [X] Error: ML Pipeline failed to execute!
        pause
        exit /b 1
    )
    echo [OK] Pipeline completed successfully. fraud_flags.csv generated.
    echo.
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
endlocal
