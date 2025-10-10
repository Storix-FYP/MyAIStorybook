@echo off
echo ==================================
echo  🎨 Setting up & Starting Frontend
echo ==================================

echo Checking for Node.js dependencies...
IF NOT EXIST node_modules (
    echo   -> node_modules folder not found. Installing dependencies now...
    echo   -> This might take a few minutes.
    npm install
    echo   -> Dependencies installed successfully.
) ELSE (
    echo   -> node_modules found.
)

:: 2. Start the React development server
echo Starting React app at http://localhost:3000
npm start