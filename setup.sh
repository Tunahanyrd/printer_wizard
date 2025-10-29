#!/bin/bash

# Universal Printer Wizard - Quick Start Script
# This script helps users quickly set up and run the wizard

set -e

echo "=========================================="
echo "Universal Printer Wizard - Quick Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Note: You'll need sudo privileges to install printers."
    echo "   This script will prompt for sudo when needed."
    echo ""
fi

# Check Python version
echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "   Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Check CUPS
echo "🔍 Checking CUPS installation..."
if ! command -v cupsd &> /dev/null; then
    echo "❌ Error: CUPS is not installed."
    echo ""
    echo "Please install CUPS for your distribution:"
    echo "  Ubuntu/Debian: sudo apt install cups cups-client"
    echo "  Fedora/RHEL:   sudo dnf install cups"
    echo "  Arch Linux:    sudo pacman -S cups"
    exit 1
fi

# Check if CUPS is running
if ! systemctl is-active --quiet cups 2>/dev/null; then
    echo "⚠️  CUPS service is not running."
    echo "   Attempting to start CUPS..."
    sudo systemctl start cups
    if systemctl is-active --quiet cups; then
        echo "✅ CUPS service started successfully."
    else
        echo "❌ Failed to start CUPS. Please start it manually:"
        echo "   sudo systemctl start cups"
        exit 1
    fi
else
    echo "✅ CUPS service is running"
fi
echo ""

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found."
    echo "   Please run this script from the printer_wizard directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Verify imports
echo "🔍 Verifying installation..."
python3 -c "import rich, pyipp, pysnmp, zeroconf; print('✅ All required modules are available')"
echo ""

# Show system info
echo "=========================================="
echo "System Information"
echo "=========================================="
echo "Python Version: $PYTHON_VERSION"
echo "CUPS Status:    $(systemctl is-active cups)"
echo "Network:        $(hostname -I | awk '{print $1}')"
echo ""

# Offer to run the wizard
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "You can now run the Universal Printer Wizard:"
echo ""
echo "  Option 1: Run with sudo (recommended)"
echo "    sudo ./venv/bin/python3 tui.py"
echo ""
echo "  Option 2: Test discovery without installation"
echo "    ./venv/bin/python3 core.py"
echo ""

read -p "Would you like to run the wizard now? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting Universal Printer Wizard..."
    echo "=========================================="
    echo ""
    sudo ./venv/bin/python3 tui.py
else
    echo ""
    echo "Run the wizard whenever you're ready:"
    echo "  sudo ./venv/bin/python3 tui.py"
    echo ""
fi

echo "For help and documentation, see README.md"
echo ""
