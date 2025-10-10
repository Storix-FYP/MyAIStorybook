@echo off
echo =================================
echo  🚀 Setting up & Starting Backend
echo =================================

:: 1. Check for Virtual Environment and install dependencies if needed.
echo Checking for virtual environment...
IF NOT EXIST venv\Scripts\activate (
    echo   -> Virtual environment not found. Creating it now...
    python -m venv venv
    echo   -> venv created successfully.
    echo.
    echo   -> Installing Python dependencies for the first time...
    call venv\Scripts\pip.exe install -r requirements.txt
    echo   -> Dependencies installed.
) ELSE (
    echo   -> venv found.
)

:: 2. Activate the Python virtual environment
echo Activating venv...
call venv\Scripts\activate

:: 3. Navigate back to the project root directory
echo Returning to project root to start server...
cd ..

:: 4. Start the Uvicorn server from the root directory
echo Starting Uvicorn server at http://127.0.0.1:8000
uvicorn backend.main:app --reload