#!/bin/bash

# Upload antonnia-conversations to PyPI Production
# This script cleans, builds, and uploads the package to PyPI

set -e  # Exit on any error

echo "🚀 Starting antonnia-conversations PyPI upload process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the antonnia-conversations directory."
    exit 1
fi

# Check if required tools are installed
print_status "Checking required tools..."

if ! command -v python3 &> /dev/null; then
    print_error "python3 is not installed or not in PATH"
    exit 1
fi

if ! python3 -c "import build" 2>/dev/null; then
    print_error "build package is not installed. Install with: pip install build"
    exit 1
fi

if ! python3 -c "import twine" 2>/dev/null; then
    print_error "twine package is not installed. Install with: pip install twine"
    exit 1
fi

print_success "All required tools are available"

# Get current version
CURRENT_VERSION=$(grep -E '^version = ' pyproject.toml | cut -d'"' -f2)
print_status "Current version: $CURRENT_VERSION"

# Confirm upload
echo ""
print_warning "You are about to upload antonnia-conversations v$CURRENT_VERSION to PyPI Production"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Upload cancelled by user"
    exit 0
fi

# Step 1: Clean up old build artifacts
print_status "Cleaning up old build artifacts..."

rm -rf dist/
rm -rf build/
rm -rf *.egg-info/
rm -rf antonnia_conversations.egg-info/

# Clean Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

print_success "Build artifacts cleaned"

# Step 2: Run basic validation
print_status "Running basic validation..."

# Check if version is valid
if [[ ! $CURRENT_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format: $CURRENT_VERSION (expected: x.y.z)"
    exit 1
fi

# Check if __init__.py version matches
INIT_VERSION=$(grep -E '^__version__ = ' antonnia/conversations/__init__.py | cut -d'"' -f2)
if [ "$CURRENT_VERSION" != "$INIT_VERSION" ]; then
    print_error "Version mismatch: pyproject.toml ($CURRENT_VERSION) vs __init__.py ($INIT_VERSION)"
    exit 1
fi

print_success "Version validation passed"

# Step 3: Build the package
print_status "Building the package..."

python3 -m build

if [ $? -ne 0 ]; then
    print_error "Build failed"
    exit 1
fi

print_success "Package built successfully"

# Step 4: Check the built package
print_status "Validating built package..."

python3 -m twine check dist/*

if [ $? -ne 0 ]; then
    print_error "Package validation failed"
    exit 1
fi

print_success "Package validation passed"

# Step 5: Show what will be uploaded
print_status "Files to be uploaded:"
ls -la dist/

# Step 6: Upload to PyPI
print_status "Uploading to PyPI..."

python3 -m twine upload dist/* --verbose

if [ $? -ne 0 ]; then
    print_error "Upload failed"
    exit 1
fi

print_success "Package uploaded successfully to PyPI!"

# Step 7: Final confirmation
echo ""
print_success "🎉 antonnia-conversations v$CURRENT_VERSION has been successfully uploaded to PyPI!"
print_status "You can now install it with: pip install antonnia-conversations==$CURRENT_VERSION"
print_status "PyPI URL: https://pypi.org/project/antonnia-conversations/$CURRENT_VERSION/"

# Optional: Clean up dist folder
read -p "Do you want to clean up the dist/ folder? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf dist/
    print_success "dist/ folder cleaned up"
fi

print_success "Upload process completed successfully!" 