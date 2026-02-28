#!/bin/bash

set -e

echo "=================================="
echo "Instagram MCP Server Installation"
echo "=================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python 3.10+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version check passed ($PYTHON_VERSION)"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "=================================="
echo "Installation completed successfully!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Configure your proxy in ~/.instagram-mcp/config.json"
echo "   Example: {\"proxy\": {\"url\": \"http://127.0.0.1:7890\", \"enabled\": true}}"
echo ""
echo "2. Or use the configure_proxy tool after starting the server"
echo ""
