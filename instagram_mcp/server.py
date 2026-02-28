#!/usr/bin/env python3
import asyncio
import json
import sys
from pathlib import Path

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent

    HAS_MCP = True
except ImportError:
    HAS_MCP = False

from instagram_mcp.tools import get_instagram_tools
from instagram_mcp.client import InstagramClient

CONFIG_DIR = Path.home() / ".instagram-mcp"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config():
    """Load configuration from config.json"""
    default_config = {
        "proxy": {
            "url": "",
            "enabled": False
        },
        "browser": {
            "headless": True
        }
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
    proxy_enabled = config.get("proxy", {}).get("enabled", False)
    proxy_url = config.get("proxy", {}).get("url", "")

    return proxy_enabled and bool(proxy_url)


def create_server():
    if not HAS_MCP:
        print("MCP not installed.", file=sys.stderr)
        sys.exit(1)

    server = Server("ins-mcp")

    # Check if proxy is configured
    proxy_configured = check_proxy_configured()

    # Load configuration
    config = load_config()

    # Initialize Instagram client with config
    proxy_url = config.get("proxy", {}).get("url", "")
    if not config.get("proxy", {}).get("enabled", False):
        proxy_url = ""

    headless = config.get("browser", {}).get("headless", True)

    client = InstagramClient(proxy_url=proxy_url, headless=headless)

    @server.list_tools()
    async def list_tools():
        """List all available Instagram tools"""
        tools = get_instagram_tools()

        # Add configuration tools based on proxy status
        if not proxy_configured:
            # First-time setup - only show configure_proxy
            config_tool = Tool(
                name="configure_proxy",
                description="Configure proxy settings for Instagram access (Required for first-time setup)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "proxy_url": {
                            "type": "string",
                            "description": "Proxy URL (e.g., http://127.0.0.1:7890 or http://user:pass@proxy.com:port)"
                        },
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable or disable proxy",
                            "default": True
                        }
                    },
                    "required": ["proxy_url"]
                }
            )
            tools.append(config_tool)
        else:
            # Proxy already configured - show update_proxy_config and browser management
            update_proxy_tool = Tool(
                name="update_proxy_config",
                description="Update or change proxy settings without restarting the server",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "proxy_url": {
                            "type": "string",
                            "description": "New proxy URL (e.g., http://127.0.0.1:7890 or http://user:pass@proxy.com:port)"
                        },
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable or disable proxy",
                            "default": True
                        }
                    },
                    "required": ["proxy_url"]
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
            tools.append(update_proxy_tool)
            tools.append(close_browser_tool)

        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool calls"""
        try:
            # Handle initial proxy configuration
            if name == "configure_proxy":
                new_proxy_url = arguments.get("proxy_url", "")
                enabled = arguments.get("enabled", True)

                new_config = load_config()
                new_config["proxy"]["url"] = new_proxy_url
                new_config["proxy"]["enabled"] = enabled

                if save_config(new_config):
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "message": "Proxy configuration saved successfully. Please restart the MCP server to apply changes.",
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

            # Handle proxy configuration update (no restart required)
            if name == "update_proxy_config":
                new_proxy_url = arguments.get("proxy_url", "")
                enabled = arguments.get("enabled", True)

                new_config = load_config()
                old_proxy_url = new_config["proxy"]["url"]
                new_config["proxy"]["url"] = new_proxy_url
                new_config["proxy"]["enabled"] = enabled

                if save_config(new_config):
                    # Close existing browser to apply new proxy settings
                    await client.close()

                    # Update client with new proxy settings
                    client.proxy_url = new_proxy_url if enabled else ""
                    client._proxy = None  # Will be recreated on next request

                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": True,
                            "message": "Proxy configuration updated successfully. Browser has been reset with new proxy settings.",
                            "old_proxy": old_proxy_url,
                            "new_proxy": new_proxy_url,
                            "enabled": enabled
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

            # Check if proxy is configured for Instagram tools
            if not proxy_configured:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "Proxy not configured. Please use the 'configure_proxy' tool first to set up your proxy settings.",
                        "message": "Instagram access requires a proxy to work properly. Please configure your proxy settings."
                    }, ensure_ascii=False, indent=2)
                )]

            # Handle Instagram tools
            if name == "search_users":
                result = await client.search_user(arguments.get("query"))
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            elif name == "get_user_profile":
                result = await client.get_profile(
                    arguments.get("username"),
                )
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            elif name == "get_user_posts":
                result = await client.get_user_posts(arguments.get("_id"), arguments.get("cursor"))
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            elif name == "get_post_details":
                result = await client.get_post_details(arguments.get("post_shortcode"))
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            error_result = {"error": str(e), "tool": name}
            return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]

    return server, client


async def main():
    server, client = create_server()

    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    finally:
        # Ensure browser is closed when server shuts down
        print("Shutting down, closing browser...", file=sys.stderr)
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
