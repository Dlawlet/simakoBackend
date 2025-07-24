@echo off
REM Windows batch script for Flask backend setup

echo Setting up Flask backend for development...

cd flask

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

echo Flask backend setup complete!
echo To run the server:
echo cd flask
ECHO venv\Scripts\activate
echo python app.py

pause
