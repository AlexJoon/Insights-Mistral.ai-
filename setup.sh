#!/bin/bash

# Setup script for Mistral Chat Application
# This script sets up both backend and frontend

set -e

echo "================================================"
echo "Mistral Chat Application Setup"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check Node.js version
echo "Checking Node.js version..."
node_version=$(node --version 2>&1)
echo "Node.js version: $node_version"
echo ""

# Setup Backend
echo "================================================"
echo "Setting up Backend..."
echo "================================================"
cd backend

echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Backend setup complete!"
echo ""

# Return to root
cd ..

# Setup Frontend
echo "================================================"
echo "Setting up Frontend..."
echo "================================================"
cd frontend

echo "Installing Node.js dependencies..."
npm install

echo "Frontend setup complete!"
echo ""

# Return to root
cd ..

echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Configure your Mistral API key in backend/.env"
echo "2. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python -m backend.main"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "================================================"
