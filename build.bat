@echo off
echo ============================================
echo   MyPcNow - Build Script
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Install dependencies
echo [1/4] Installing dependencies...
pip install -r requirements.txt --quiet

REM Generate icon
echo [2/4] Generating icon...
python create_icon.py

REM Build exe with PyInstaller (using spec file for full config)
echo [3/4] Building executable...
pyinstaller --noconfirm mypcnow.spec

echo [4/4] Build complete!
echo.
echo Executable: dist\MyPcNow.exe
echo.

REM Check if Inno Setup is available
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo Building installer...
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
    echo Installer built successfully!
) else (
    echo [INFO] Inno Setup not found. Install it to build the installer.
    echo        https://jrsoftware.org/isdl.php
)

echo.
echo Done!
pause
