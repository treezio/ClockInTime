#!/bin/bash
# Build macOS application bundle

set -e

echo "🏗️  Building ClockInTime.app"
echo "============================"
echo ""

# Install py2app if not already installed
echo "📦 Installing py2app..."
./venv/bin/pip install py2app

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Build the app
echo "🔨 Building application bundle..."
./venv/bin/python setup.py py2app

echo ""
echo "✅ Build complete!"
echo ""
echo "📂 Application created at: dist/ClockInTime.app"
echo ""
echo "To test the app:"
echo "  open dist/ClockInTime.app"
echo ""
echo "To install:"
echo "  cp -r dist/ClockInTime.app /Applications/"
echo ""
echo "To create a DMG for distribution:"
echo "  ./create_dmg.sh"
