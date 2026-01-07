#!/bin/bash
# Build script for Linux
# This creates a portable folder with the game executable

echo "========================================"
echo "Building Simple Chess for Linux"
echo "========================================"

# Check if venv exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Ensure pyinstaller is installed
echo "Checking PyInstaller..."
if ! pip show pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Make sure Stockfish is executable
if [ -f "engine/stockfish/linux/stockfish-ubuntu-x86-64-avx2" ]; then
    echo "Setting Stockfish permissions..."
    chmod +x "engine/stockfish/linux/stockfish-ubuntu-x86-64-avx2"
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/SimpleChess
rm -rf build

# Build the executable
echo "Building executable..."
pyinstaller chess_linux.spec --noconfirm

echo ""
if [ -f "dist/SimpleChess/SimpleChess" ]; then
    # Make the output executable
    chmod +x "dist/SimpleChess/SimpleChess"
    
    # Also ensure bundled Stockfish is executable
    if [ -f "dist/SimpleChess/engine/stockfish/linux/stockfish-ubuntu-x86-64-avx2" ]; then
        chmod +x "dist/SimpleChess/engine/stockfish/linux/stockfish-ubuntu-x86-64-avx2"
    fi
    
    echo "========================================"
    echo "BUILD SUCCESSFUL!"
    echo "========================================"
    echo ""
    echo "Your portable game is in: dist/SimpleChess/"
    echo ""
    echo "To distribute:"
    echo "  1. Tar/zip the entire 'dist/SimpleChess' folder"
    echo "     tar -czvf SimpleChess-linux.tar.gz -C dist SimpleChess"
    echo "  2. Users can extract and run ./SimpleChess"
    echo ""
else
    echo "========================================"
    echo "BUILD FAILED - Check errors above"
    echo "========================================"
fi
