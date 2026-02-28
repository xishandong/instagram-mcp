# Instagram MCP - OpenClaw 部署指南

本指南介绍如何将 Instagram MCP Server 集成到 **OpenClaw** 中使用。

## 📋 前提条件

1. **已安装 OpenClaw**
2. **Python 3.10+**
3. **可用的代理服务器**（访问 Instagram 必需）

## 🚀 快速安装

### 方式一：自动安装（推荐）

```bash
# 在项目目录下执行
bash .openclaw-install.sh
```

这将自动完成：
- ✅ 复制所有必要文件到 `~/.openclaw/skills/instagram-mcp/`
- ✅ 配置正确的路径
- ✅ 创建启动脚本

然后安装依赖：

```bash
pip install -r ~/.openclaw/skills/instagram-mcp/requirements.txt
```

### 方式二：手动安装

如果不想使用自动脚本，可以手动复制以下文件到 `~/.openclaw/skills/instagram-mcp/`:

```
~/.openclaw/skills/instagram-mcp/
├── instagram_mcp/
│   ├── __init__.py
│   ├── server.py
│   ├── instagram_client.py
│   ├── tools.py
│   ├── utils.py
│   └── post_parser.py
├── requirements.txt
├── SKILL.md          # 技能描述文档
└── mcporter.json          # MCP 配置
```

然后修改 `mcp.json` 中的路径为绝对路径。

## ⚙️ 配置代理

Instagram 服务需要代理才能访问。首次使用前必须配置：

### 方法 1：通过工具配置（推荐）

Agent 会自动提示你使用 `configure_proxy` 工具进行配置。

### 方法 2：手动创建配置文件

```bash
mkdir -p ~/.instagram-mcp
cat > ~/.instagram-mcp/config.json << 'EOF'
{
  "proxy": {
    "url": "http://127.0.0.1:7890",
    "enabled": true
  }
}
EOF
```

## 🔧 重启 OpenClaw

配置完成后，**重启 OpenClaw** 以加载新技能。

```bash
# 在 OpenClaw 中重新加载技能
reload skills
```

## 💬 使用方法

安装完成后，你可以直接对 Agent 说出以下指令：

| 自然语言指令 | 功能 |
|-------------|------|
| "搜索ins用户 natgeo" | 搜索 Instagram 用户 |
| "查看ins用户资料 natgeo" | 获取用户详细资料 |
| "查看natgeo的发帖历史" | 获取用户的帖子列表 |
| "查看这个帖子的详情 DOZirOEEkZ6" | 获取特定帖子详情 |
| "更新代理配置为 http://..." | 动态修改代理设置 |
| "关闭浏览器释放资源" | 手动关闭浏览器 |

## 📁 技能文件说明

- **`SKILL.md`** - 技能描述文档，包含触发词和工具定义
- **`mcp.json`** - MCP Server 启动配置
- **`mcporter-config.json`** - MCPorter 标准化配置（如使用 mcporter）

## 🔄 更新技能

当有新版本时，重新执行安装脚本即可：

```bash
bash /path/to/instagram-mcp/.openclaw-install.sh
```

然后重启 OpenClaw。

## ❓ 故障排查

### 问题：找不到技能
- 确认文件已正确复制到 `~/.openclaw/skills/instagram-mcp/`
- 检查 OpenClaw 是否支持 MCP 类型技能
- 重启 OpenClaw

### 问题：无法连接 Instagram
- 检查代理配置是否正确且可用
- 验证代理服务器是否正常工作

### 问题：Python 模块未找到
- 确保已在正确环境安装了依赖：`pip install -r requirements.txt`
- 检查 Python 版本是否为 3.10+

## 📝 注意事项

1. **首次使用**：必须先配置代理才能正常使用
2. **隐私合规**：仅获取公开的 Instagram 数据
3. **请求频率**：避免过于频繁的请求
4. **资源管理**：长时间不使用时，可使用 `close_browser` 释放资源

---

**Happy Instagramming!** 🎉
