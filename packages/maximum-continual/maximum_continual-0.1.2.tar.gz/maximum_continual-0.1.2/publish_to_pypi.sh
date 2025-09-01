#!/bin/bash

# Script to build and publish maximum-continual package to PyPI
# Usage: ./publish_to_pypi.sh

set -e  # Exit on any error

echo "🚀 Publishing maximum-continual to PyPI..."

# Clean previous builds
if [ -d "dist" ]; then
    echo "🧹 Cleaning previous build artifacts..."
    rm -rf dist/
fi

# Install build tools if needed
echo "📦 Ensuring build tools are installed..."
python -m pip install build twine --quiet

# Build the package
echo "🔨 Building package..."
python -m build

# List the built files
echo "📋 Built files:"
ls -la dist/

# Upload to PyPI
echo "🚀 Uploading to PyPI..."
python -m twine upload dist/*

echo "✅ Package successfully published to PyPI!"
echo "🎉 Install with: pip install maximum-continual"
