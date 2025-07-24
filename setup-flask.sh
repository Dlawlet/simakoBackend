#!/bin/bash
# Development setup script for Flask backend

echo "Setting up Flask backend for development..."

# Navigate to flask directory
cd flask

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Flask backend setup complete!"
echo "To run the server:"
echo "cd flask"
echo "venv\Scripts\activate"
echo "python app.py"
