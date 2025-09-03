@echo off
setlocal enabledelayedexpansion

REM Reasoning Kernel Installation Script for Windows
REM Supports Windows 10/11 with PowerShell 5.1+

REM Color codes for output (using PowerShell)
set "RED=Write-Host -ForegroundColor Red"
set "GREEN=Write-Host -ForegroundColor Green"
set "YELLOW=Write-Host -ForegroundColor Yellow"
set "BLUE=Write-Host -ForegroundColor Blue"

REM Logging functions
set "LOG=%BLUE% '[INFO]'"
set "SUCCESS=%GREEN% '[SUCCESS]'"
set "WARNING=%YELLOW% '[WARNING]'"
set "ERROR=%RED% '[ERROR]'"

echo ========================================
echo   Reasoning Kernel Installer
echo ========================================
echo.

REM Check if running on supported Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%VERSION%" LSS "10.0" (
    powershell -Command "%ERROR% 'Unsupported Windows version. This script requires Windows 10 or later.'"
    exit /b 1
)

REM Check if PowerShell is available
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "%ERROR% 'PowerShell not found. Please install PowerShell 5.1 or later.'"
    exit /b 1
)

powershell -Command "%LOG% 'Checking Python installation...'"

REM Check if Python 3.12 is installed
python --version 2>nul | findstr "3.12" >nul
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    powershell -Command "%SUCCESS% 'Python 3.12 already installed'"
) else (
    python -V 2>nul | findstr "Python 3.12" >nul
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=python"
        powershell -Command "%SUCCESS% 'Python 3.12 already installed'"
    ) else (
        powershell -Command "%LOG% 'Installing Python 3.12...'"
        
        REM Check if Chocolatey is installed
        where choco >nul 2>&1
        if %errorlevel% equ 0 (
            choco install python312 -y
            set "PYTHON_CMD=python"
        ) else (
            powershell -Command "%ERROR% 'Chocolatey not found. Please install Python 3.12 manually from https://www.python.org/downloads/'"
            exit /b 1
        )
        
        powershell -Command "%SUCCESS% 'Python 3.12 installed'"
    )
)

REM Install uv package manager
powershell -Command "%LOG% 'Installing uv package manager...'"
where uv >nul 2>&1
if %errorlevel% equ 0 (
    powershell -Command "%SUCCESS% 'uv already installed'"
) else (
    REM Use the official installation method
    powershell -Command "Invoke-WebRequest -Uri 'https://astral.sh/uv/install.ps1' -UseBasicParsing | Invoke-Expression"
    if %errorlevel% neq 0 (
        powershell -Command "%ERROR% 'Failed to install uv'"
        exit /b 1
    )
    powershell -Command "%SUCCESS% 'uv installed'"
)

REM Create virtual environment
powershell -Command "%LOG% 'Creating virtual environment...'"
if not exist ".msa-venv" (
    %PYTHON_CMD% -m venv .msa-venv
    powershell -Command "%SUCCESS% 'Virtual environment created'"
) else (
    powershell -Command "%WARNING% 'Virtual environment already exists'"
)

REM Activate virtual environment
powershell -Command "%LOG% 'Activating virtual environment...'"
call .msa-venv\Scripts\activate.bat
powershell -Command "%SUCCESS% 'Virtual environment activated'"

REM Install Reasoning Kernel
powershell -Command "%LOG% 'Installing Reasoning Kernel...'"

REM Check if we're in a git repository
if exist ".git" (
    powershell -Command "%LOG% 'Installing in development mode (editable install)...'"
    where uv >nul 2>&1
    if %errorlevel% equ 0 (
        uv pip install -e ".[all]"
    ) else (
        pip install -e ".[all]"
    )
) else (
    powershell -Command "%LOG% 'Installing from PyPI...'"
    where uv >nul 2>&1
    if %errorlevel% equ 0 (
        uv pip install "reasoning-kernel[all]"
    ) else (
        pip install "reasoning-kernel[all]"
    )
)

if %errorlevel% equ 0 (
    powershell -Command "%SUCCESS% 'Reasoning Kernel installed'"
) else (
    powershell -Command "%ERROR% 'Failed to install Reasoning Kernel'"
    exit /b 1
)

REM Configure Daytona API key
powershell -Command "%LOG% 'Configuring Daytona API key...'"
echo To configure Daytona, please set the following environment variables:
echo   set DAYTONA_API_KEY=your_api_key_here
echo   set DAYTONA_API_URL=https://app.daytona.io
echo.
echo You can get your Daytona API key from: https://www.daytona.io/
echo.

REM Verify installation
powershell -Command "%LOG% 'Verifying installation...'"
where reasoning-kernel >nul 2>&1
if %errorlevel% equ 0 (
    reasoning-kernel --help >nul 2>&1
    if %errorlevel% equ 0 (
        powershell -Command "%SUCCESS% 'Reasoning Kernel CLI verified'"
    ) else (
        powershell -Command "%ERROR% 'Installation verification failed'"
        exit /b 1
    )
) else (
    powershell -Command "%ERROR% 'Installation verification failed'"
    exit /b 1
)

echo.
echo ========================================
powershell -Command "%SUCCESS% 'Reasoning Kernel installed successfully!'"
echo ========================================
echo.
echo To use the Reasoning Kernel:
echo 1. Activate the virtual environment: .msa-venv\Scripts\activate.bat
echo 2. Run the CLI: reasoning-kernel --help
echo.