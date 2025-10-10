@echo off
echo Starting both servers in separate windows...

:: The 'start' command opens a new window.
:: The '/D "path"' flag sets the starting directory for the new window.

start "Backend Server" /D "backend" cmd /k "start_backend.bat"
start "Frontend Server" /D "frontend" cmd /k "start_frontend.bat"