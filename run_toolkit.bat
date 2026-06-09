@echo off
setlocal enabledelayedexpansion

:: ==========================================
::      GRIST ADMIN ^& DATA TOOLKIT
::      One-Click Launcher (v1.0)
:: ==========================================

echo.
echo [1/3] Checking environment...

:: 1. Check for Virtual Environment
if not exist "venv" (
    echo [SETUP] Creating virtual environment... this may take a minute...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Python not found in PATH. Please install Python 3.8+
        pause
        exit /b
    )
)

:: 2. Activate venv
call venv\Scripts\activate.bat

:: 3. Check/Install Dependencies
echo [2/3] Verifying dependencies...
pip install --quiet -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    pause
    exit /b
)

:: 4. Port Selection Menu
:MENU
cls
echo ==========================================
echo      GRIST ADMIN ^& DATA TOOLKIT
echo ==========================================
echo [v1.0] Ready to launch.
echo.
echo Choose a port to start the application:
echo [1] 8501 (Default Streamlit)
echo [2] 8080
echo [3] 8000
echo [4] 5000
echo [5] Custom Port
echo [0] Exit
echo.

set "choice="
set /p choice="Enter your choice (0-5): "

if "%choice%"=="" goto MENU
if "%choice%"=="0" exit /b
if "%choice%"=="1" set PORT=8501
if "%choice%"=="2" set PORT=8080
if "%choice%"=="3" set PORT=8000
if "%choice%"=="4" set PORT=5000
if "%choice%"=="5" (
    set /p PORT="Enter custom port number: "
    if "!PORT!"=="" (
        echo [ERROR] No port entered.
        pause
        goto MENU
    )
)
if "!PORT!"=="" goto MENU

:: 5. Check if port is free
echo Checking if port %PORT% is free...
netstat -ano | findstr /C:":%PORT% " > nul
if %errorlevel% equ 0 (
    echo.
    echo [WARNING] Port %PORT% seems to be in use.
    echo Please choose another one or free it up.
    pause
    goto MENU
)

:: 6. Start App
echo.
echo [3/3] Starting Toolkit on port %PORT%...
echo ------------------------------------------
streamlit run grist_admin_toolkit.py --server.port %PORT%

pause
