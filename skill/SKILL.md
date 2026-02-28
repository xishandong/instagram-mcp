---
name: instagram-mcp
type: mcp
description: |
  Instagram MCP Skill - 通过MCP协议访问Instagram公开数据
  支持搜索用户、查看用户资料、获取帖子、查看帖子详情等功能

triggers:
  - "搜索ins用户"
  - "搜索INS用户"
  - "查看ins用户资料"
  - "查看INS用户资料"
  - "查看ins发帖历史"
  - "查看INS发帖历史"
  - "查看ins帖子详情"
  - "查看INS帖子详情"
  - "下载ins帖子图片"
  - "下载ins帖子视频"
  - "分析ins帖子数据"
  - "关闭浏览器"
  - "更新代理配置"
  
tools:
  - search_users
  - get_user_profile
  - get_user_posts
  - get_post_details
  - configure_proxy
  - close_browser
  - update_proxy_config
---

# Instagram MCP Skill

用于让 AI Agent 通过MCP协议访问Instagram数据的Skill。

## 概述

本Skill允许AI Agent访问Instagram的公开数据，包括：
- 搜索Instagram用户
- 查看用户资料和发帖历史
- 获取帖子详细内容（图片、视频、文字）

## 前置要求

1. **Python环境**: Python 3.10+
2. **依赖安装**: 
   ```bash
   pip install -r requirements.txt
   ```
3. **代理配置**: 由于网络原因，需要配置代理才能正常访问

## 首次配置

Agent会自动检测是否需要配置代理。如果需要，会提示用户使用 `configure_proxy` 工具进行配置：

```json
{
  "proxy_url": "http://127.0.0.1:7890",
  "enabled": true
}
```

配置完成后需要重启MCP Server。

## 工具列表

### 1. search_users - 搜索Instagram用户

**用途**: 通过用户名或昵称搜索Instagram用户

**参数**:
- `query` (string): 搜索关键词，可以是用户名或真实姓名

**返回**: 匹配的用户列表，包含用户名、头像、认证状态等信息

**使用场景**:
- 用户想查找某个特定的Instagram账号
- 不知道准确用户名时进行模糊搜索

---

### 2. get_user_profile - 获取用户资料

**用途**: 获取指定用户的详细资料信息

**参数**:
- `username` (string): 准确的Instagram用户名

**返回**: 完整的用户资料，包括：
- 用户ID (用于获取帖子)
- 用户名和显示名称
- 头像链接
- 粉丝数和关注数
- 简介信息

**使用场景**:
- 确认用户身份
- 获取用户ID以便后续获取帖子

---

### 3. get_user_posts - 获取用户帖子

**用途**: 分页获取指定用户的帖子列表

**参数**:
- `_id` (string, required): 用户ID，从 `get_user_profile` 获取
- `cursor` (string, optional): 分页游标，用于加载更多帖子

**返回**: 
- 帖子列表（每个帖子包含缩略图、短码、时间戳等）
- 下一页游标（如有更多内容）
- hasNext标记

**使用场景**:
- 查看用户最近的发帖
- 浏览用户的历史内容

**分页说明**:
第一次调用不需要cursor，如果返回hasNext=true，可以继续传入cursor获取下一页。

---

### 4. get_post_details - 获取帖子详情

**用途**: 获取单个Instagram帖子的完整信息

**参数**:
- `post_shortcode` (string): 帖子短码，从URL `/p/SHORTCODE/` 中提取

**返回**: 帖子的详细信息：
- 帖子类型（图片/视频）
- 高清图片/视频链接
- 文字内容
- 点赞数和评论数
- 发布时间

**使用场景**:
- 查看特定帖子的详细内容
- 下载帖子中的图片或视频
- 分析帖子互动数据

---

### 5. configure_proxy - 配置代理

**用途**: 首次使用或需要更改代理时进行配置

**参数**:
- `proxy_url` (string): 代理服务器地址，如 `http://127.0.0.1:7890`
- `enabled` (boolean): 是否启用代理，默认true

**返回**: 配置状态和提示信息

**注意**: 修改配置后需要重启MCP Server才能生效

## 典型工作流程

### 场景1: 查找并查看用户主页

```
1. search_users(query="目标用户名") → 找到用户
2. get_user_profile(username="确切用户名") → 获取用户资料和ID
3. get_user_posts(_id="用户ID") → 获取该用户最近的帖子
```

### 场景2: 查看特定帖子详情

```
1. 从帖子URL提取shortcode (如 https://instagram.com/p/ABC123/ → ABC123)
2. get_post_details(post_shortcode="ABC123") → 获取帖子完整信息
```

### 场景3: 浏览用户历史帖子

```
1. get_user_profile(username="用户名") → 获取用户ID
2. posts = get_user_posts(_id="用户ID") → 第一页帖子
3. while posts.hasNext:
   posts = get_user_posts(_id="用户ID", cursor=posts.cursor) → 下一页
```

## 数据字段说明

### 用户信息
| 字段 | 类型 | 说明 |
|------|------|------|
| username | string | Instagram用户名 |
| full_name | string | 用户显示名称 |
| avatar_url | string | 头像图片URL |
| is_verified | boolean | 是否认证账号 |
| profile_url | string | 个人主页链接 |
| pk/id | string | 用户唯一ID |

### 帖子信息
| 字段 | 类型 | 说明 |
|------|------|------|
| post_url | string | 帖子链接 |
| images | array | 图片URL列表（多图帖） |
| video_url | string | 视频URL（如是视频帖） |
| post_content | string | 帖子文字内容 |
| likes | number | 点赞数 |
| comments | number | 评论数 |
| timestamp | string | 发布时间 |
| post_type | string | image/video/unknown |

## 常见问题

**Q: 为什么需要使用代理？**
A: Instagram和imginn.com对部分地区有限制访问，代理可以绕过这些限制。

**Q: 搜索不到想要的结果？**
A: 
- 检查拼写是否正确
- 尝试使用不同的关键词（真实姓名、昵称等）
- 确认用户账号是否公开

**Q: 获取帖子失败？**
A: 
- 确认用户ID正确（必须从get_user_profile获取）
- 检查网络连接和代理是否正常
- 部分私密账号可能无法获取内容

**Q: 如何获取帖子的shortcode？**
A: 从Instagram帖子URL中提取：
- URL格式: `https://www.instagram.com/p/SHORTCODE/`
- 例如: `https://www.instagram.com/p/DOZirOEEkZ6/` → shortcode为 `DOZirOEEkZ6`

## 注意事项

1. **隐私合规**: 只获取公开的Instagram数据，尊重用户隐私设置
2. **频率控制**: 避免过于频繁的请求，建议添加适当的延迟
3. **数据缓存**: 对于不变的数据（如历史帖子），可以适当缓存以减少请求
4. **错误处理**: 某些用户或帖子可能被删除或设为私密，需要妥善处理异常情况

## 技术支持

如遇到问题，请检查：
1. 代理配置是否正确且可用
2. 依赖是否完整安装（特别是playwright）
3. 日志输出中的具体错误信息
