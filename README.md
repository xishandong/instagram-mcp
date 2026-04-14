# Instagram MCP Server

🚀 **无限制访问 Instagram 公开数据** | 🔓 **Cloudflare 自动绕过** | 🌐 **代理友好**

一个基于 MCP (Model Context Protocol) 的 Instagram 服务器，提供访问 Instagram 用户、帖子和详细信息的工具。

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🔓 **Cloudflare 绕过** | 内置浏览器自动化，智能处理 CF 5 秒验证，无需手动干预 |
| 🌐 **代理支持** | SOCKS5/HTTP 代理全支持，Docker 环境自动适配 |
| 🚀 **异步高并发** | 基于 asyncio 架构，支持多任务并行处理 |
| 📊 **完整数据** | 用户资料、帖子列表、帖子详情、高清图片/视频链接 |
| 🔄 **智能分页** | 自动处理游标，轻松获取历史内容 |
| 🛡️ **指纹伪装** | TLS 指纹模拟真实浏览器，绕过反爬虫检测 |
| 🐳 **Docker 部署** | 一键容器化部署，配置持久化 |
| 🔧 **热更新** | 代理配置实时更新，无需重启服务 |

## 🎯 适用场景

- 📈 **社交媒体分析** - 获取网红/竞品账号数据
- 🔍 **市场调研** - 分析热门话题和用户反馈
- 📸 **内容采集** - 批量获取高清图片/视频素材
- 🤖 **AI 训练数据** - 为多模态模型提供真实数据
- 📊 **舆情监控** - 跟踪品牌/产品相关讨论

## 安装

1. 克隆项目：
```bash
git clone <repository-url>
cd instagram-mcp
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 配置

### 代理配置

Instagram 访问需要配置代理。使用 `configure` 工具进行配置：

```json
{
  "proxy_url": "http://127.0.0.1:7890",
  "headless": true
}
```

**参数说明**：
- `proxy_url`: 代理服务器地址（必需，格式：`http://127.0.0.1:7890` 或 `http://user:pass@proxy.com:port`）
- `headless`: 是否启用无头模式（可选，默认：true，true=无GUI，false=显示浏览器窗口）

### 配置文件位置

配置文件保存在：`~/.instagram-mcp/config.json`

```json
{
  "proxy": {
    "url": "http://127.0.0.1:7890"
  },
  "browser": {
    "headless": true
  }
}
```

## 使用方法

### 启动服务器

```bash
python -m instagram_mcp.server
```

服务器默认运行在 `http://127.0.0.1:8000/sse`

### 可用工具

#### 1. configure
配置代理和浏览器设置。

**参数**：
- `proxy_url`: 代理服务器地址
- `headless`: 是否启用无头模式（默认：true）

**示例**：
```json
{
  "proxy_url": "http://127.0.0.1:7890",
  "headless": false
}
```

#### 2. search_users
搜索 Instagram 用户。

**参数**：
- `query`: 用户名或全名

**示例**：
```json
{
  "query": "instagram"
}
```

#### 3. get_user_profile
获取用户资料信息。

**参数**：
- `username`: Instagram 用户名

**示例**：
```json
{
  "username": "instagram"
}
```

#### 4. get_user_posts
获取用户的帖子列表。

**参数**：
- `_id`: 用户ID（从 get_user_profile 获取）
- `cursor`: 分页游标（从上一次请求获取，可选）

**示例**：
```json
{
  "_id": "123456789"
}
```

**获取下一页**：
```json
{
  "_id": "123456789",
  "cursor": "QVFB..."
}
```

#### 5. get_post_details
获取帖子详细信息。

**参数**：
- `post_shortcode`: 帖子短代码（URL中 `/p/` 后面的部分）

**示例**：
```json
{
  "post_shortcode": "C1234567890"
}
```

#### 6. close_browser
手动关闭浏览器实例以释放资源。

**参数**：无

## 工作流程

1. **配置代理**：首次使用前，使用 `configure` 工具配置代理
2. **搜索用户**：使用 `search_users` 搜索目标用户
3. **获取用户资料**：使用 `get_user_profile` 获取用户详细信息
4. **获取帖子列表**：使用 `get_user_posts` 获取用户帖子
5. **获取帖子详情**：使用 `get_post_details` 获取特定帖子的详细信息

## 技术架构

- **MCP Server**: 基于 Model Context Protocol 构建
- **浏览器自动化**: 使用 zendriver 进行浏览器控制
- **HTTP 请求**: 使用 noble-tls 进行 TLS 指纹伪装
- **HTML 解析**: 使用 BeautifulSoup4 解析 HTML
- **Web 服务器**: 使用 Starlette 和 Uvicorn 提供 SSE 服务

## 依赖项

- mcp>=1.0.0,<2.0.0
- uvicorn>=0.24.0
- starlette>=0.27.0
- zendriver>=0.5.0,<1.0.0
- noble-tls>=0.1.0
- beautifulsoup4>=4.12.0

## 注意事项

1. **代理要求**: Instagram 访问必须配置代理，否则无法正常使用
2. **Cloudflare 挑战**: 服务器会自动处理 Cloudflare 验证挑战
3. **浏览器资源**: 使用完毕后可以使用 `close_browser` 工具释放资源
4. **配置热更新**: 代理配置更新后无需重启服务器，会自动应用新配置

## 项目结构

```
instagram-mcp/
├── instagram_mcp/
│   ├── __init__.py
│   ├── client.py          # Instagram 客户端
│   ├── server.py          # MCP 服务器
│   ├── tools.py           # MCP 工具定义
│   ├── post_parser.py     # 帖子解析
│   └── utils.py           # 工具函数
├── requirements.txt
└── README.md
```

## 许可证

请查看项目许可证文件。
