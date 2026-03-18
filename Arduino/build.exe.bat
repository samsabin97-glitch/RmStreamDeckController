@echo off
cd /d %~dp0

echo ================================
echo Installing dependencies...
echo ================================
py -m pip install --upgrade pip
py -m pip install pyinstaller flask pyserial

echo.
echo ================================
echo Building EXE...
echo ================================
py -m PyInstaller ^
  --onefile ^
  --name serial_bridge ^
  --console ^
  --hidden-import=serial ^
  --hidden-import=flask ^
  serial_bridge.py

echo.
echo ================================
echo BUILD COMPLETE
echo ================================
echo EXE location:
echo %~dp0dist\serial_bridge.exe
echo.

pause