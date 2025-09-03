#!/bin/bash
# publish.sh - Secure PyPI publishing script

set -e

echo "🚀 SimpleSpec PyPI Publishing Script"
echo "===================================="

# Check if token is provided
if [ -z "$PYPI_API_TOKEN" ]; then
    echo "❌ Error: PYPI_API_TOKEN environment variable is not set"
    echo ""
    echo "Options to set the token:"
    echo "1. In GitHub Codespaces (recommended):"
    echo "   - Go to GitHub Settings > Codespaces > Repository secrets"
    echo "   - Add PYPI_API_TOKEN with your token"
    echo "   - Restart Codespaces"
    echo ""
    echo "2. Set temporarily (this session only):"
    echo "   export PYPI_API_TOKEN=your_pypi_token_here"
    echo ""
    echo "3. Load from file (if you have it saved securely):"
    echo "   export PYPI_API_TOKEN=\$(cat ~/.pypi_token)"
    echo ""
    exit 1
fi

# Validate token format
if [[ ! "$PYPI_API_TOKEN" =~ ^pypi-.* ]]; then
    echo "⚠️  Warning: Token doesn't start with 'pypi-'. Make sure it's correct."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Token found and appears valid"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Are you in the simplespec directory?"
    exit 1
fi

# Run tests first
echo "🧪 Running tests..."
if ! uv run pytest; then
    echo "❌ Tests failed. Fix issues before publishing."
    exit 1
fi

echo "✅ Tests passed"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "📦 Building package..."
if ! uv build; then
    echo "❌ Build failed"
    exit 1
fi

echo "✅ Package built successfully"

# List what will be uploaded
echo "📋 Files to upload:"
ls -la dist/

# Confirm upload
echo ""
read -p "🚀 Upload to PyPI? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Upload cancelled"
    exit 1
fi

# Upload to PyPI
echo "⬆️  Uploading to PyPI..."
if uv run twine upload dist/* --username __token__ --password "$PYPI_API_TOKEN"; then
    echo ""
    echo "🎉 Successfully published to PyPI!"
    echo "📦 Package: https://pypi.org/project/simplespec/"
    echo "📖 Install with: pip install simplespec"
else
    echo "❌ Upload failed"
    exit 1
fi
