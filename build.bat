@echo off
REM Build mbvr_launcher.exe with PyInstaller
REM Run this on Windows with Python installed

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building mbvr_launcher.exe...
pyinstaller --noconsole --onefile --name mbvr_launcher launcher.py

echo.
echo Done! Output: dist\mbvr_launcher.exe
