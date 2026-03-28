@echo off
echo ========================================
echo Starting MyAIStorybook Application
echo ========================================
echo.

:: Step 1: Start WebUI
::echo [1/3] Starting Stable Diffusion WebUI...
::start "Stable Diffusion WebUI" cmd /k "cd /d C:\Users\wahab\Downloads\FYP\storybook-fyp\stable-diffusion-webui && webui-user.bat"
::echo WebUI starting... waiting 10 seconds for initialization
::timeout /t 10 /nobreak

:: Step 2: Start Backend
echo.
echo [2/3] Starting Backend Server...
start "Backend Server" /D "backend" cmd /k "start_backend.bat"
echo Backend starting... waiting 3 seconds
timeout /t 3 /nobreak

:: Step 3: Start Frontend
echo.
echo [3/3] Starting Frontend Server...
start "Frontend Server" /D "frontend" cmd /k "start_frontend.bat"

echo.
echo ========================================
echo All servers started successfully!
echo ========================================
echo.
echo WebUI:     http://127.0.0.1:7860
echo Backend:   http://127.0.0.1:8000
echo Frontend:  http://localhost:3000
echo.
echo Press any key to exit this window...
pause > nul