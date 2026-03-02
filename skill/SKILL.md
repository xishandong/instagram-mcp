---
name: instagram-mcp
type: mcp
description: |
  Instagram MCP Skill - 通过MCP协议访问Instagram公开数据
  支持搜索用户、查看用户资料、获取帖子、查看帖子详情、动态更新代理配置、管理浏览器资源等功能

triggers:
  # 搜索功能
  - "搜索ins用户"
  - "搜索instagram用户"
  - "搜ins账号"
  - "找ins博主"
  
  # 用户资料
  - "查看ins用户资料"
  - "查看ins主页"
  - "查看instagram用户"
  - "获取ins用户信息"
  
  # 帖子相关
  - "查看ins发帖历史"
  - "获取ins帖子"
  - "查看ins帖子详情"
  - "查看ins帖子内容"
  - "下载ins帖子图片"
  - "下载ins帖子视频"
  - "分析ins帖子数据"
  - "获取ins图文内容"
  
  # 代理配置
  - "配置代理"
  
  # 资源管理
  - "关闭浏览器"
  - "释放浏览器资源"
  - "清理浏览器"
  
tools:
  - instagram-mcp.search_users
  - instagram-mcp.get_user_profile
  - instagram-mcp.get_user_posts
  - instagram-mcp.get_post_details
  - instagram-mcp.configure
  - instagram-mcp.update_proxy_config
  - instagram-mcp.close_browser
---

# Instagram MCP Skill

通过 OpenClaw 调用 Instagram MCP 服务，实现 Instagram 数据的搜索和获取。

## 前置条件

### 1. 启动 MCP 服务

确保 Instagram MCP 服务已添加：

```bash
mcporter config add instagram-mcp http://localhost:8000/sse
```

### 2. 检查服务状态

通过健康检查接口确认服务是否正常运行：

```bash
curl http://127.0.0.1:8000/health
```

预期返回：
```json
{
  "status": "ok",
  "server": "instagram-mcp"
}
```

### 3. 配置代理

首次使用前必须配置代理：

```bash
mcporter call 'instagram-mcp.configure(proxy_url:"http://127.0.0.1:7890", headless: true)'
```

## 可用能力

### 1. configure

配置代理和浏览器设置。

**命令**：
```bash
mcporter call 'instagram-mcp.configure(proxy_url:<proxy_url>, headless: <true/false>)'
```

**参数**：
- `proxy_url`: 代理服务器地址（必需）
- `headless`: 是否启用无头模式（可选，默认 true）

**示例**：
```bash
mcporter call 'instagram-mcp.configure(proxy_url:"http://127.0.0.1:7890", headless: true)'
```

### 2. search_users

搜索 Instagram 用户。

**命令**：
```bash
mcporter call 'instagram-mcp.search_users(query: <query>)'
```

**参数**：
- `query`: 用户名或全名（必需）

**示例**：
```bash
mcporter call 'instagram-mcp.search_users(query: "iu")'
```

**返回值**：
```json
{
  "success": true,
  "data": []
}
```

### 3. get_user_profile

获取用户资料信息。

**命令**：
```bash
mcporter call 'instagram-mcp.get_user_profile(username: <username>)'
```

**参数**：
- `username`: Instagram 用户名（必需）

**示例**：
```bash
mcporter call 'instagram-mcp.get_user_profile(username: "dlwlrma")'
```

**返回值**：
```json
{
  "success": true,
  "data": {}
}
```

### 4. get_user_posts

获取用户的帖子列表。

**命令**：
```bash
mcporter call 'instagram-mcp.get_user_posts(_id: <user_id>, cursor: <cursor>)'
```

**参数**：
- `_id`: 用户ID（必需，从 get_user_profile 获取）
- `cursor`: 分页游标（可选，从上一次请求获取）

**示例**：
```bash
# 获取第一页
mcporter call 'instagram-mcp.get_user_posts(_id: "123456789", cursor: "")'

# 获取下一页
mcporter call 'instagram-mcp.get_user_posts(_id: "123456789", cursor: "QVFEMHlsV2M4Yl96QkxaM1BMTUJUaVBEZlZfZmFBakVpcTdGUFk3UDFwYjRmUlhXVWloWlpSdVRSWFNiSGFkQ29rOEJhQmFiMGhjVnpBdFJKNGhwWkNCXw==")'
```
翻页时需要注意使用最新的 cursor，否则会导致翻页失败

**返回值**：
```json
{
  "success": true,
  "data": {
    "posts": [],
    "cursor": "",
    "hasNext": true,
    "_id": "1692800026"
  }
}
```

### 5. get_post_details

获取帖子详细信息。

**命令**：
```bash
mcporter call 'instagram-mcp.get_post_details(post_shortcode: <shortcode>)'
```

**参数**：
- `post_shortcode`: 帖子短代码（必需，URL中 `/p/` 后面的部分）

**示例**：
```bash
mcporter call 'instagram-mcp.get_post_details(post_shortcode: "DVIdTG7kmiD")'
```

**返回值**：
```json
{
  "success": true,
  "data": {}
}
```

### 6. close_browser

手动关闭浏览器实例以释放资源。

**命令**：
```bash
mcporter call 'instagram-mcp.close_browser()'
```

**参数**：无

**示例**：
```bash
mcporter call 'instagram-mcp.close_browser()'
```

**返回值**：
```json
{
  "success": true,
  "message": "Browser closed successfully. It will be automatically reopened on the next request."
}
```

## 典型使用流程

### 1. 配置代理

```bash
# 检查服务状态
curl http://127.0.0.1:8000/health

# 配置代理
mcporter call 'instagram-mcp.configure(proxy_url:<proxy_url>, headless: true)'
```

### 2. 搜索用户

```bash
mcporter call 'instagram-mcp.search_users(query: "iu")'
```

### 3. 获取用户资料

```bash
mcporter call 'instagram-mcp.get_user_profile(username: "dlwlrma")'
```

### 4. 获取用户帖子

```bash
# 获取第一页
mcporter call 'instagram-mcp.get_user_posts(_id: "123456789", cursor: "")'

# 获取下一页
mcporter call 'instagram-mcp.get_user_posts(_id: "123456789", cursor: "QVFEMHlsV2M4Yl96QkxaM1BMTUJUaVBEZlZfZmFBakVpcTdGUFk3UDFwYjRmUlhXVWloWlpSdVRSWFNiSGFkQ29rOEJhQmFiMGhjVnpBdFJKNGhwWkNCXw==")'
```

### 5. 获取帖子详情

```bash
mcporter call 'instagram-mcp.get_post_details(post_shortcode: "DVIdTG7kmiD")'
```

### 6. 释放资源

```bash
mcporter call 'instagram-mcp.close_browser()'
```

## 注意事项

1. **代理配置**: 必须先配置代理才能使用 Instagram 相关功能。代理文件存储在 `~/.instagram-mco/config.json` 中
2. **服务检查**: 使用前确保服务正常运行
3. **分页查询**: 获取帖子列表时，使用返回的 cursor 进行分页，每次新的翻页都要使用上一页的 cursor
4. **资源管理**: 使用完毕后可调用 close_browser 释放资源
5. **配置热更新**: 代理配置更新后无需重启服务，自动应用新配置
6. **资源释放**: 在操作完成后，调用 close_browser 释放资源，切记！一定要释放资源，否则会导致资源泄漏

## 错误处理

### 代理未配置

```json
{
  "success": false,
  "error": "Proxy not configured. Please use the 'configure' tool first to set up your proxy settings.",
  "message": "Instagram access requires a proxy to work properly. Please configure your proxy settings."
}
```
