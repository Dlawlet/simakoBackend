@echo off
REM Windows batch script for Node.js backend setup

echo Setting up Node.js backend for development...

cd nodejs

REM Install dependencies
echo Installing Node.js dependencies...
npm install

echo Node.js backend setup complete!
echo To run the server:
echo cd nodejs
echo npm run dev

pause
