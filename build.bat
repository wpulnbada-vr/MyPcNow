@echo off
echo ============================================
echo   MyPcNow v1.1.0 - Build Script
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
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Generate icon
echo [2/4] Generating icon...
python create_icon.py
if errorlevel 1 (
    echo [ERROR] Failed to generate icon
    pause
    exit /b 1
)

REM Build exe with PyInstaller (using spec file for full config)
echo [3/4] Building executable...
pyinstaller --noconfirm mypcnow.spec
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed
    pause
    exit /b 1
)

echo [4/4] Build complete!
echo.

REM Verify output
if exist "dist\MyPcNow.exe" (
    echo ============================================
    echo   SUCCESS: dist\MyPcNow.exe
    echo ============================================
) else (
    echo [ERROR] Build output not found
    pause
    exit /b 1
)

echo.

REM Check if Inno Setup is available
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo Building installer...
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
    if not errorlevel 1 (
        echo Installer: dist\installer\MyPcNow_setup_v1.1.0.exe
    )
) else (
    echo [INFO] Inno Setup not found. Skipping installer.
    echo        https://jrsoftware.org/isdl.php
)

echo.
echo Done!
pause
