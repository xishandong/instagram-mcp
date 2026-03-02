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

# 2. 清理旧版本
if [ -d "$TARGET_DIR" ]; then
    echo "Removing existing installation..."
    rm -rf "$TARGET_DIR"
fi

# 3. 创建目录结构
mkdir -p "$TARGET_DIR"

# 4. 复制 Skill 配置文件
cp "${SOURCE_DIR}/skill/SKILL.md" "$TARGET_DIR/"
echo "✅ Successfully installed Instagram MCP to OpenClaw"
