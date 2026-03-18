@echo off
setlocal

echo Starting Serial Bridge...

REM =========================
REM OPTIONAL CONFIG
REM =========================
set SERIAL_BRIDGE_PORT1=\\.\COM3
set SERIAL_BRIDGE_PORT2=\\.\COM4
set SERIAL_BRIDGE_BAUD=9600
set SERIAL_BRIDGE_HTTP_PORT=8787
set SERIAL_BRIDGE_HOST=127.0.0.1

REM =========================
REM RUN EXE FROM SAME FOLDER
REM =========================
"%~dp0dist\serial_bridge.exe"

endlocal