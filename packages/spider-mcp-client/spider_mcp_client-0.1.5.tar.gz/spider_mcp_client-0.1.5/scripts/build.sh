#!/bin/bash
# Build script for spider-mcp-client

set -e

echo "🔨 Building spider-mcp-client package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade build twine

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Build package
echo "🏗️  Building package..."
python -m build

# Check package
echo "✅ Checking package..."
python -m twine check dist/*

echo "🎉 Build complete!"
echo "📦 Package files:"
ls -la dist/

echo ""
echo "🚀 To publish to PyPI:"
echo "   python -m twine upload dist/*"
echo ""
echo "🧪 To publish to Test PyPI:"
echo "   python -m twine upload --repository testpypi dist/*"
