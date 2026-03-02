#!/usr/bin/env python3
import asyncio
import json
import sys
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from instagram_mcp.tools import get_instagram_tools
from instagram_mcp.client import InstagramClient

CONFIG_DIR = Path.home() / ".instagram-mcp"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config():
    """Load configuration from config.json"""
    default_config = {
        "proxy": {
            "url": "",
        },
        "browser": {
            "headless": True
        },
    }

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Merge with default config
                default_config.update(user_config)
        except Exception as e:
            print(f"Warning: Failed to load config file, using defaults: {e}", file=sys.stderr)

    return default_config


def save_config(config):
    """Save configuration to config.json"""
    try:
        # Ensure config directory exists
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}", file=sys.stderr)
        return False


def check_proxy_configured():
    """Check if proxy is properly configured"""
    config = load_config()
    proxy_url = config.get("proxy", {}).get("url", "")

    return bool(proxy_url)


def create_server():
    server = Server(name="instagram-mcp", version="1.0.0")
    init_config = load_config()

    init_proxy = init_config.get("proxy", {}).get("url", "")
    init_headless = init_config.get("browser", {}).get("headless", True)

    client = InstagramClient(proxy_url=init_proxy, headless=init_headless)

    @server.list_tools()
    async def list_tools():
        """List all available Instagram tools"""
        tools = get_instagram_tools()
        configure_tool = Tool(
            name="configure",
            description="Configure Instagram MCP settings (proxy and browser settings)",
            inputSchema={
                "type": "object",
                "properties": {
                    "proxy_url": {
                        "type": "string",
                        "description": "Proxy URL (e.g., http://127.0.0.1:7890 or http://user:pass@proxy.com:port)"
                    },
                    "headless": {
                        "type": "boolean",
                        "description": "Enable or disable headless mode (true = no GUI, false = show browser window, default: true)"
                    }
                }
            }
        )
        close_browser_tool = Tool(
            name="close_browser",
            description="Manually close the browser instance to free up resources",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
        tools.append(configure_tool)
        tools.append(close_browser_tool)

        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool calls"""
        nonlocal init_proxy, init_headless
        try:
            # Handle initial configuration
            if name == "configure":
                print("call_tool", name, arguments)
                proxy_url = arguments.get("proxy_url", "")
                headless = arguments.get("headless", True)

                new_config = load_config()
                new_config["proxy"]["url"] = proxy_url
                new_config["browser"]["headless"] = headless
                init_proxy = proxy_url
                init_headless = headless

                if save_config(new_config):
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "message": "Configuration saved successfully. Please restart the MCP server to apply changes.",
                            "config": new_config
                        }, ensure_ascii=False, indent=2)
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": "Failed to save configuration"
                        }, ensure_ascii=False, indent=2)
                    )]

            # Handle manual browser close
            if name == "close_browser":
                try:
                    print("call_tool", name, arguments)
                    await client.close()
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "message": "Browser closed successfully. It will be automatically reopened on the next request."
                        }, ensure_ascii=False, indent=2)
                    )]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": f"Failed to close browser: {str(e)}"
                        }, ensure_ascii=False, indent=2)
                    )]

            proxy_configured = check_proxy_configured()
            # Check if proxy is configured for Instagram tools
            if not proxy_configured:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "Proxy not configured. Please use the 'configure' tool first to set up your proxy settings.",
                        "message": "Instagram access requires a proxy to work properly. Please configure your proxy settings."
                    }, ensure_ascii=False, indent=2)
                )]

            config = load_config()
            proxy = config.get("proxy", {}).get("url", "")
            headless = config.get("browser", {}).get("headless", True)
            if proxy != init_proxy or headless != init_headless:
                print("用户配置了代理，重新初始化浏览器")
                await client.close()
                client.headless = headless
                client.proxy_url = proxy
            # Handle Instagram tools
            if name == "search_users":
                print("call_tool", name, arguments)
                result = await client.search_user(arguments.get("query"))
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            elif name == "get_user_profile":
                print("call_tool", name, arguments)
                result = await client.get_profile(
                    arguments.get("username"),
                )
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            elif name == "get_user_posts":
                print("call_tool", name, arguments)
                result = await client.get_user_posts(arguments.get("_id"), arguments.get("cursor"))
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            elif name == "get_post_details":
                print("call_tool", name, arguments)
                result = await client.get_post_details(arguments.get("post_shortcode"))
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            else:
                print("call_tool", name, arguments)
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            error_result = {"error": str(e), "tool": name}
            return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]

    return server, client


async def main():
    server, client = create_server()
    config = load_config()
    host = config.get("server", {}).get("host", "127.0.0.1")
    port = config.get("server", {}).get("port", 8000)

    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):

        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
            return JSONResponse({"status": "ok"})

    async def handle_health(request):
        return JSONResponse({"status": "ok", "server": "instagram-mcp"})

    starlette_app = Starlette(
        debug=False,
        routes=[
            Route("/health", endpoint=handle_health),
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )
    # Add CORS middleware to allow all origins
    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    config_uvicorn = uvicorn.Config(starlette_app, host=host, port=port, log_level="info")
    server_uvicorn = uvicorn.Server(config_uvicorn)

    try:
        await server_uvicorn.serve()
    finally:
        # Ensure browser is closed when server shuts down
        print("Shutting down, closing browser...", file=sys.stderr)
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
