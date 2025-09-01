#!/bin/bash

# Script to build maximum-continual package (without publishing)
# Usage: ./build_package.sh

set -e  # Exit on any error

echo "🔨 Building maximum-continual package..."

# Clean previous builds
if [ -d "dist" ]; then
    echo "🧹 Cleaning previous build artifacts..."
    rm -rf dist/
fi

# Install build tools if needed
echo "📦 Ensuring build tools are installed..."
python -m pip install build --quiet

# Build the package
echo "🔨 Building package..."
python -m build

# List the built files
echo "📋 Built files:"
ls -la dist/

echo "✅ Package built successfully!"
echo "💡 To publish to PyPI, run: ./publish_to_pypi.sh"
