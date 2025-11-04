@echo off
REM GRNet UV Setup Script for Windows
REM This script automates the setup process

echo.
echo ===============================================
echo   GRNet Project Setup with UV Package Manager
echo ===============================================
echo.

REM Check if UV is installed
echo Checking if UV is installed...
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] UV is not installed!
    echo.
    echo Please install UV first:
    echo   Run in PowerShell: 
    echo   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    pause
    exit /b 1
)

echo [OK] UV is installed
echo.

REM Create virtual environment
echo Creating virtual environment with Python 3.8...
uv venv --python 3.8
if %errorlevel% neq 0 (
    echo [WARNING] Virtual environment creation had issues
)
echo.

REM Sync dependencies
echo Installing project dependencies...
uv sync
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies might have failed
)
echo.

echo ===============================================
echo   Setup Complete!
echo ===============================================
echo.
echo Next steps:
echo   1. Activate the environment:
echo      .venv\Scripts\activate
echo.
echo   2. Start Jupyter Lab:
echo      uv run jupyter lab
echo.
echo   3. Open: code/GRNet_approach.ipynb
echo.
echo For more info, see UV_SETUP.md or UV_QUICKREF.md
echo.
pause
