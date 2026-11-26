@echo off
cd /d "%~dp0"
echo Smart Student Attendance - Setup
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Install from https://www.python.org/downloads/
    echo Check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Setup complete. Run: run.bat
pause
