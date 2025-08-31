#!/bin/bash

# Sage LLM Test Setup Script
# This script helps set up the testing environment

echo "🚀 Setting up Sage LLM Test Environment"

# Configuration is now handled via tests/config.ts
echo "📝 Configuration is managed in tests/config.ts"
echo "⚠️  IMPORTANT: Please edit tests/config.ts and set your API key before running tests!"
echo "   Update SAGE_API_KEY in tests/config.ts with your actual API key"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Create screenshots directory
if [ ! -d "screenshots" ]; then
    echo "📁 Creating screenshots directory..."
    mkdir -p screenshots/states/{idle,diff_approval,interaction,generation}
    mkdir -p screenshots/test_runs
else
    echo "✅ Screenshots directory already exists"
fi

echo ""
echo "🎯 Setup complete! To run the tests:"
echo "   1. Make sure your API key is set in tests/config.ts"
echo "   2. Start JupyterLab: npm run start"
echo "   3. In another terminal, run tests: npm test"
echo ""
echo "📸 Screenshots will be saved in the screenshots/ directory"
