#!/bin/bash
# Instagram MCP OpenClaw 安装脚本

set -e

SKILL_NAME="instagram-mcp"
SOURCE_DIR="/Users/dongxishan/XishanWork/PythonProjects/instagram-mcp"
TARGET_DIR="${HOME}/.openclaw/skills/${SKILL_NAME}"

echo "=========================================="
echo "Installing Instagram MCP to OpenClaw"
echo "=========================================="

# 1. 检查 OpenClaw 目录是否存在
if [ ! -d "${HOME}/.openclaw" ]; then
    echo "❌ Error: OpenClaw directory not found at ${HOME}/.openclaw"
    echo "Please install and run OpenClaw first."
    exit 1
fi

cp "${SOURCE_DIR}/skill/SKILL.md" "$TARGET_DIR/"

