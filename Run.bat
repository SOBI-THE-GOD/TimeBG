@echo off
echo Time-Based Background Changer
echo ===========================
echo.

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo After installation, please run this batch file again.
    pause
    exit /b 1
)

:: Check if tkinter is available (it should be built into Python)
python -c "import tkinter" >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo tkinter module is not available in your Python installation.
    echo This is unusual as tkinter should come with standard Python installations.
    echo.
    echo Please ensure you have a complete Python installation with tkinter.
    echo You might need to reinstall Python with the "tcl/tk and IDLE" option enabled.
    pause
    exit /b 1
)

:: Install required packages
echo Installing required packages...
pip install -r requirements.txt

:: Run the application
echo.
echo Starting Time-Based Background Changer...
echo The application will show up as an icon in your system tray.
echo Look for the clock icon near the clock in your taskbar.
echo Right-click on the icon to see available options.
echo.
python main.py

pause 