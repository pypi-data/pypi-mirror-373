#!/bin/bash
# Test script for spider-mcp-client

set -e

echo "🧪 Running spider-mcp-client tests..."

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -e ".[dev]"

# Run tests with coverage
echo "🔍 Running tests with coverage..."
python -m pytest tests/ -v --tb=short

# Run type checking
echo "🔍 Running type checking..."
python -m mypy spider_mcp_client/

# Run code formatting check
echo "🔍 Checking code formatting..."
python -m black --check spider_mcp_client/ tests/

# Run linting
echo "🔍 Running linting..."
python -m flake8 spider_mcp_client/ tests/

echo "✅ All tests passed!"
