@echo off
echo Building VitalSign EXE...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Build EXE
echo Building EXE with PyInstaller...
pyinstaller VitalSign.spec

echo.
echo Build complete!
echo EXE file located in: dist\VitalSign.exe
pause
