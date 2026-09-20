@echo off
setlocal
set "DEMO_DIR=%~dp0"
cd /d "%DEMO_DIR%"
start "Royal Square Demo" "C:\Program Files\Google\Chrome\Application\chrome.exe" "http://localhost:5173"
node start-server.js
endlocal
