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
mkdir -p "${TARGET_DIR}/instagram_mcp"

# 4. 复制核心文件
echo "Copying source files..."
cp "${SOURCE_DIR}/instagram_mcp/"*.py "${TARGET_DIR}/instagram_mcp/"
cp "${SOURCE_DIR}/requirements.txt" "$TARGET_DIR/"
touch "${TARGET_DIR}/instagram_mcp/__init__.py"

# 5. 复制 Skill 配置文件
cp "${SOURCE_DIR}/skill/SKILL.md" "$TARGET_DIR/"
cp "${SOURCE_DIR}/skill/mcporter.json" "$TARGET_DIR/"

# 6. 修改 mcp.json 中的路径为绝对路径
echo "Configuring paths..."
sed -i '' "s|\\\"cwd\\\": \\\"\\${workspaceFolder}\\\"|\\\"cwd\\\": \\\"${TARGET_DIR}\\\"|g" "${TARGET_DIR}/mcporter.json"

# 7. 创建启动脚本
cat > "${TARGET_DIR}/start-server.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"
python -m instagram_mcp.server
EOF
chmod +x "${TARGET_DIR}/start-server.sh"

# 8. 更新 mcporter.json 使用启动脚本
sed -i '' 's|"command": "python"|"command": "./start-server.sh"|g' "${TARGET_DIR}/mcporter.json"
sed -i '' 's|"args": \[.*\]|"args": []|g' "${TARGET_DIR}/mcporter.json"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Location: $TARGET_DIR"
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip install -r ${TARGET_DIR}/requirements.txt"
echo "2. Configure proxy: mkdir -p ~/.instagram-mcp && echo '{\"proxy\":{\"url\":\"http://127.0.0.1:7890\",\"enabled\":true}}' > ~/.instagram-mcp/config.json"
echo "3. Restart OpenClaw or reload skills"
echo ""
echo "The skill will be automatically loaded by OpenClaw on next start."
