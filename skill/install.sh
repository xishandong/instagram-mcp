#!/bin/bash
# Instagram MCP OpenClaw 安装脚本
# 自动检测脚本位置，支持任意路径安装

set -e

SKILL_NAME="instagram-mcp"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TARGET_DIR="${HOME}/.openclaw/skills/${SKILL_NAME}"

echo "=========================================="
echo "🚀 Installing Instagram MCP to OpenClaw"
echo "=========================================="
echo "📁 Project root: ${PROJECT_ROOT}"
echo "📦 Target dir: ${TARGET_DIR}"
echo ""

# 1. 检查 OpenClaw 目录是否存在
if [ ! -d "${HOME}/.openclaw" ]; then
    echo "❌ Error: OpenClaw directory not found at ${HOME}/.openclaw"
    echo "Please install and run OpenClaw first."
    exit 1
fi

# 2. 检查 SKILL.md 是否存在
if [ ! -f "${SCRIPT_DIR}/SKILL.md" ]; then
    echo "❌ Error: SKILL.md not found at ${SCRIPT_DIR}/SKILL.md"
    exit 1
fi

# 3. 清理旧版本
if [ -d "$TARGET_DIR" ]; then
    echo "🗑️  Removing existing installation..."
    rm -rf "$TARGET_DIR"
fi

# 4. 创建目录结构
mkdir -p "$TARGET_DIR"

# 5. 复制 Skill 配置文件
echo "📋 Copying SKILL.md..."
cp "${SCRIPT_DIR}/SKILL.md" "$TARGET_DIR/"

# 6. 验证安装
if [ -f "$TARGET_DIR/SKILL.md" ]; then
    echo ""
    echo "✅ Successfully installed Instagram MCP to OpenClaw"
    echo "🎉 Skill location: $TARGET_DIR"
    echo "💡 Restart OpenClaw to activate the skill"
else
    echo "❌ Installation failed"
    exit 1
fi
