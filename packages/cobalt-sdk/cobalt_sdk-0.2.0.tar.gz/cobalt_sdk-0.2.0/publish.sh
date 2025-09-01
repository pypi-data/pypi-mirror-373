#!/bin/bash

# Script to build and publish cobalt-py-sdk to PyPI
# Usage: ./publish.sh

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the cobalt-py-sdk directory."
    exit 1
fi

# Check if required tools are installed
print_status "Checking required tools..."
if ! command -v python3 &> /dev/null; then
    print_error "python3 is not installed or not in PATH"
    exit 1
fi

# Install/upgrade build tools
print_status "Installing/upgrading build tools..."
uv pip install --upgrade build twine

# Clean up previous builds
print_status "Cleaning up previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
print_status "Building the package..."
python3 -m build

# Check if build was successful
if [ ! -d "dist" ]; then
    print_error "Build failed - dist directory not created"
    exit 1
fi

# Verify the package
print_status "Verifying the package..."
python3 -m twine check dist/*

# Get package info
PACKAGE_NAME=$(grep '^name = ' pyproject.toml | cut -d'"' -f2)
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)

print_status "Package: $PACKAGE_NAME"
print_status "Version: $VERSION"

# Ask for confirmation before publishing
REGISTRY_NAME="PyPI"
UPLOAD_CMD="python3 -m twine upload dist/*"

echo
print_warning "About to publish $PACKAGE_NAME v$VERSION to $REGISTRY_NAME"
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Publishing cancelled."
    exit 0
fi

# Upload to PyPI
print_status "Uploading to $REGISTRY_NAME..."
eval "$UPLOAD_CMD"

if [ $? -eq 0 ]; then
    print_status "Successfully published $PACKAGE_NAME v$VERSION to $REGISTRY_NAME!"

    print_status "Installation command:"
    echo "uv pip install $PACKAGE_NAME"
else
    print_error "Publishing failed!"
    exit 1
fi
