#!/bin/bash

echo "Starting Wordle Game Setup..."

if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed. Please install Python3 first."
    exit 1
fi


if ! command -v npm &> /dev/null; then
    echo "npm is required but not installed. Please install Node.js and npm first."
    exit 1
fi

echo "Setting up backend..."
cd backend || exit
python3 -m venv venv
source venv/bin/activate
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setting up frontend..."
cd ../frontend || exit
echo "Installing Node dependencies..."
npm install

echo "Starting services..."
cd ../backend && source venv/bin/activate && python3 app.py & 
cd ../frontend && npm run dev
