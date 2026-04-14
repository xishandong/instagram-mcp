from mcp.types import Tool


def get_instagram_tools():
    """
    Instagram MCP Tools - 无限制访问 Instagram 公开数据
    
    核心特性:
    - 🔓 Cloudflare 自动绕过 - 内置浏览器自动化，智能处理 CF 验证
    - 🌐 代理支持 - 支持 SOCKS5/HTTP 代理，网络环境无忧
    - 🚀 高并发 - 异步架构，支持多任务并行
    - 📊 完整数据 - 用户信息、帖子列表、帖子详情全覆盖
    - 🔄 分页支持 - 自动处理游标，轻松获取历史内容
    """
    return [
        Tool(
            name="search_users",
            description="🔍 搜索 Instagram 用户 | 支持用户名/昵称搜索 | Cloudflare 自动绕过",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "用户名或昵称，例如 'jennie' 或 'BLACKPINK'"},
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_user_profile",
            description="👤 获取用户资料 | 粉丝数/关注数/帖子数/简介 | CF 保护站点可用",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Instagram 用户名，例如 'jennierubyjane'"}
                },
                "required": ["username"]
            }
        ),
        Tool(
            name="get_user_posts",
            description="📸 获取用户帖子 | 支持分页/游标 | 自动处理 Cloudflare 验证 | 高清图片/视频链接",
            inputSchema={
                "type": "object",
                "properties": {
                    "_id": {"type": "string", "description": "用户 ID (从 get_user_profile 获取)"},
                    "cursor": {"type": "string", "description": "分页游标 (可选，用于获取下一页)"},
                },
                "required": ["_id"]
            }
        ),
        Tool(
            name="get_post_detail",
            description="🎯 帖子详情解析 | 多图/视频/点赞/评论 | 绕过 CF 获取完整数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_shortcode": {
                        "type": "string",
                        "description": "帖子短代码 (URL 中 /p/ 后的部分，例如 'C_xxxxxxx')"
                    },
                },
                "required": ["post_shortcode"]
            }
        )
    ]
