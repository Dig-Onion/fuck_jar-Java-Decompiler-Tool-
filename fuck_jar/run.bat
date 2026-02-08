@echo off

title Fuck Jar - Java Decompiler Tool

cls
echo.
echo ========================================
echo   Fuck Jar - Java Decompiler Tool
echo ========================================
echo.  Author: dig_onion
echo.  Version: 1.0.0
echo ========================================
echo.

echo [1/4] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found!
    echo Please install Python 3.6 or higher
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Python installed

echo.
echo [2/4] Checking Java environment...
java -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Java not found!
    echo Java is required for CFR decompiler
    echo Download: https://www.oracle.com/java/technologies/downloads/
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "%CONTINUE%"=="y" (
        exit /b 1
    )
) else (
    echo [SUCCESS] Java installed
)

echo.
echo [3/4] Checking Python dependencies...
pip show tkinterdnd2 >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Dependency installation failed!
        echo Please install manually: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed
) else (
    echo [SUCCESS] Dependencies installed
)

echo.
echo [4/4] Checking CFR decompiler...
if exist "cfr-0.152.jar" (
    echo [SUCCESS] CFR decompiler found
) else (
    echo [INFO] CFR decompiler not found
    echo Will be downloaded automatically on first run
)

echo.
echo ========================================
echo   All checks passed, starting program...
echo ========================================
echo.

python fuck_jar_gui.py

if errorlevel 1 (
    echo.
    echo [ERROR] Program execution failed!
    echo Please check the error message above.
    echo.
    pause
    exit /b 1
)

endlocal
