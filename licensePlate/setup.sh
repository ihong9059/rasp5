#!/bin/bash
# License Plate Recognition - Setup Script

echo "=================================="
echo "License Plate Recognition Setup"
echo "=================================="

# Check Python version
python3 --version

# Install system dependencies
echo ""
echo "[1/4] Installing system dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-venv libgl1-mesa-glx libglib2.0-0

# Create virtual environment
echo ""
echo "[2/4] Creating virtual environment..."
cd "$(dirname "$0")"
python3 -m venv venv

# Activate and install packages
echo ""
echo "[3/4] Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create captures directory
echo ""
echo "[4/4] Creating directories..."
mkdir -p captures

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "To run the application:"
echo "  cd $(pwd)"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Then open http://localhost:5000 in your browser"
echo "=================================="
