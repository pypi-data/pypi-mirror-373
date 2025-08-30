@echo off
REM Sage LLM Test Setup Script for Windows
REM This script helps set up the testing environment

echo 🚀 Setting up Sage LLM Test Environment

REM Configuration is now handled via tests/config.ts
echo 📝 Configuration is managed in tests/config.ts
echo ⚠️  IMPORTANT: Please edit tests/config.ts and set your API key before running tests!
echo    Update SAGE_API_KEY in tests/config.ts with your actual API key

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
) else (
    echo ✅ Dependencies already installed
)

REM Create screenshots directory
if not exist "screenshots" (
    echo 📁 Creating screenshots directory...
    mkdir screenshots\states\idle
    mkdir screenshots\states\diff_approval
    mkdir screenshots\states\interaction
    mkdir screenshots\states\generation
    mkdir screenshots\test_runs
) else (
    echo ✅ Screenshots directory already exists
)

echo.
echo 🎯 Setup complete! To run the tests:
echo    1. Make sure your API key is set in tests/config.ts
echo    2. Start JupyterLab: npm run start
echo    3. In another terminal, run tests: npm test
echo.
echo 📸 Screenshots will be saved in the screenshots\ directory
