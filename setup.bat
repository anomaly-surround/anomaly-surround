@echo off
echo ==========================================
echo   Anomaly Surround - Setup
echo ==========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Download from https://python.org
    pause
    exit /b 1
)

:: Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
echo.

:: Check Equalizer APO
if exist "C:\Program Files\EqualizerAPO\config" (
    echo [OK] Equalizer APO is installed.
) else (
    echo [!!] Equalizer APO is NOT installed.
    echo      Download from: https://sourceforge.net/projects/equalizerapo/
    echo      After installing, run the Configurator and enable it for your
    echo      HyperX Cloud Alpha S headphones.
    echo.
)

echo.
echo Setup complete! Run the app with:
echo   python main.py          (GUI mode)
echo   python main.py --tray   (background/tray mode)
echo   python main.py --cli status   (CLI mode)
echo.
pause
