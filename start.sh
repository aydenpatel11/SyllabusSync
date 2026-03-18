#!/bin/bash

# Syllabus to Calendar - Start Script
# This script starts the FastAPI backend server

echo "🚀 Starting Syllabus to Calendar..."
echo ""
echo "Backend will be available at: http://localhost:8000"
echo "Frontend: Open frontend/index.html in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment and start server
cd "$(dirname "$0")"
source venv/bin/activate
python run_api.py
