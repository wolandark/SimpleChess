@echo off
REM Build script for Windows
REM This creates a portable folder with the game executable

echo ========================================
echo Building Simple Chess for Windows
echo ========================================

REM Check if venv exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Ensure pyinstaller is installed
echo Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist\SimpleChess" rmdir /s /q "dist\SimpleChess"
if exist "build" rmdir /s /q "build"

REM Build the executable
echo Building executable...
pyinstaller chess_windows.spec --noconfirm

echo.
if exist "dist\SimpleChess\SimpleChess.exe" (
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your portable game is in: dist\SimpleChess\
    echo.
    echo To distribute:
    echo   1. Zip the entire "dist\SimpleChess" folder
    echo   2. Users can extract and run SimpleChess.exe
    echo.
) else (
    echo ========================================
    echo BUILD FAILED - Check errors above
    echo ========================================
)

pause
