# Instagram MCP Server

一个基于MCP协议的Instagram数据获取服务，支持搜索用户、获取用户资料、获取帖子等功能。

## 功能特性

- 🔍 **搜索用户** - 通过用户名或昵称搜索Instagram用户
- 👤 **获取用户资料** - 获取指定用户的详细资料信息
- 📱 **获取用户帖子** - 分页获取用户的所有帖子
- 📄 **获取帖子详情** - 获取单个帖子的详细信息（图片、视频、点赞数、评论等）

## 技术架构

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│   MCP Client    │◄───►│  Instagram MCP   │◄───►│  imginn.com │
│   (Cursor/Cline)│     │    Server        │     │  Instagram  │
└─────────────────┘     └──────────────────┘     └─────────────┘
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置代理（必须）

首次使用前需要配置代理：

```json
{
  "proxy": {
    "enabled": true,
    "url": "http://127.0.0.1:7890"
  },
  "browser": {
    "headless": true
  }
}
```

### 启动MCP Server

```bash
# 直接运行
python -m instagram_mcp.server

# 或使用stdio模式（推荐）
python instagram_mcp/server.py
```

### 添加mcp

```bash
mcporter config add instagram-mcp http://localhost:8000/sse

```

## 可用工具

| 工具名                | 描述            | 必需参数                             |
|--------------------|---------------|----------------------------------|
| `search_users`     | 搜索Instagram用户 | `query`: 搜索关键词                   |
| `get_user_profile` | 获取用户资料        | `username`: 用户名                  |
| `get_user_posts`   | 获取用户帖子        | `_id`: 用户ID（从get_user_profile获取） |
| `get_post_details` | 获取帖子详情        | `post_shortcode`: 帖子短码           |
| `configure_proxy`  | 配置代理设置        | `proxy_url`: 代理地址                |

## 使用示例

### 1. 搜索用户

```python
result = await client.call_tool("search_users", {"query": "dlwlrma"})
```

### 2. 获取用户资料

```python
result = await client.call_tool("get_user_profile", {"username": "dlwlrma"})
```

### 3. 获取用户帖子

```python
result = await client.call_tool("get_user_posts", {"_id": "1692800026"})
```

### 4. 获取帖子详情

```python
result = await client.call_tool("get_post_details", {"post_shortcode": "DOZirOEEkZ6"})
```

## 数据结构

### 用户信息

```json
{
  "username": "string",
  "full_name": "string",
  "avatar_url": "string",
  "is_verified": true,
  "profile_url": "string"
}
```

### 帖子信息

```json
{
  "post_url": "string",
  "images": [
    "url1",
    "url2"
  ],
  "video_url": "string",
  "likes": 1234,
  "comments": 56,
  "user_info": {
    ...
  },
  "post_content": "string",
  "timestamp": "string",
  "post_type": "image/video/unknown"
}
```

## Skill配置

本项目包含Skill配置，可以与支持MCP的AI Agent集成使用。

在Cursor或Cline中添加配置：

- **MCP Server**: 指向本项目的server.py
- **Skill**: 参考skill/SKILL.md

## 开发

### 运行测试

```bash
pytest tests/
```

### 项目结构

```
instagram-mcp/
├── instagram_mcp/
│   ├── __init__.py
│   ├── server.py          # MCP Server入口
│   ├── tools.py           # 工具定义
│   ├── instagram_client.py # Instagram数据抓取
│   ├── post_parser.py     # 帖子解析
│   └── utils.py           # 工具函数
├── skill/
│   ├── SKILL.md           # Skill使用文档
│   └── mcporter-config.json # MCPorter配置
├── tests/                 # 测试文件
├── pyproject.toml         # 项目配置
├── requirements.txt       # 依赖
└── README.md             # 本文档
```

## 注意事项

1. **代理必需**：由于网络限制，必须通过代理访问Instagram相关服务
2. **Cloudflare保护**：imginn.com有Cloudflare防护，可能需要等待挑战完成
3. **频率限制**：请合理控制请求频率，避免被封禁

## License

MIT License
