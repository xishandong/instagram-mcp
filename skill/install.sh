#!/bin/bash

# Instagram MCP Skill Installation Script for OpenClaw

set -e

echo "=========================================="
echo "Instagram MCP Skill Installation"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✓ pip3 found"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "✓ Dependencies installed successfully"
echo ""

# Create config directory
CONFIG_DIR="$HOME/.instagram-mcp"
mkdir -p "$CONFIG_DIR"

echo "✓ Config directory created: $CONFIG_DIR"
echo ""

# Check if mcporter is installed
if ! command -v mcporter &> /dev/null; then
    echo "Warning: mcporter CLI is not found. Please install mcporter to use this skill."
    echo "You can install it from: https://github.com/your-repo/mcporter"
    echo ""
else
    echo "✓ mcporter CLI found: $(mcporter --version 2>/dev/null || echo 'version unknown')"
    echo ""
fi

# Create default config
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    echo "Creating default config file..."
    cat > "$CONFIG_DIR/config.json" << EOF
{
  "proxy": {
    "url": ""
  },
  "browser": {
    "headless": true
  }
}
EOF
    echo "✓ Default config file created: $CONFIG_DIR/config.json"
    echo ""
fi

echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start the MCP server:"
echo "   python -m instagram_mcp.server"
echo ""
echo "2. Check service status:"
echo "   curl http://127.0.0.1:8000/health"
echo ""
echo "3. Configure proxy:"
echo "   mcporter call configure --proxy_url \"http://127.0.0.1:7890\""
echo ""
echo "4. Start using the skill:"
echo "   mcporter call search_users --query \"instagram\""
echo ""
