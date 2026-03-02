from mcp.types import Tool


def get_instagram_tools():
    return [
        Tool(
            name="search_users",
            description="Search Instagram users by username or name",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Username or full name to search for"},
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_user_profile",
            description="Get profile information about a specific Instagram user",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Instagram username"}
                },
                "required": ["username"]
            }
        ),
        Tool(
            name="get_user_posts",
            description="Get posts from a specific Instagram user, need user id from get_user_profile. if need next page, pass cursor from previous post request",
            inputSchema={
                "type": "object",
                "properties": {
                    "_id": {"type": "string", "description": "ID from the initial posts request"},
                    "cursor": {"type": "string", "description": "Cursor from the previous posts request"},
                },
                "required": ["_id"]
            }
        ),
        Tool(
            name="get_post_detail",
            description="Get detailed information about a specific Instagram post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_shortcode": {
                        "type": "string",
                        "description": "Instagram post shortcode (the part after /p/ in URL)"
                    },
                },
                "required": ["post_shortcode"]
            }
        )
    ]
