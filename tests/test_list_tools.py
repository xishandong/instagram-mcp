#!/usr/bin/env python3
"""
MCP Protocol Standard Test for Instagram MCP Server
Tests the server using MCP ClientSession and stdio transport
"""

import asyncio
import sys
import os

# Add parent directory to path to import ins_mcp module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    HAS_MCP = True
except ImportError:
    HAS_MCP = False


async def test_mcp_server():
    """Test Instagram MCP server using MCP ClientSession"""
    print("=" * 60)
    print("Instagram MCP Server - MCP Protocol Test")
    print("=" * 60)

    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=["/Users/dongxishan/XishanWork/PythonProjects/instagram-mcp/instagram_mcp/server.py"],
    )

    try:
        # Connect to the MCP server using stdio transport
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                print("\n1. Initializing MCP connection...")
                await session.initialize()
                print("   ✓ Connection initialized successfully")

                # Test 1: List available tools
                print("\n2. Listing available tools...")
                tools_response = await session.list_tools()
                print(f"   ✓ Found {len(tools_response.tools)} tools:")

                for tool in tools_response.tools:
                    print(f"     - {tool.name}: {tool.description}")

                # Expected tools
                expected_tools = {
                    "search_instagram_users",
                    "get_user_posts_initial",
                    "get_user_posts_next_page",
                    "get_post_details"
                }

                actual_tools = {tool.name for tool in tools_response.tools}

                # Verify all expected tools are present
                print("\n3. Verifying tool availability...")
                missing_tools = expected_tools - actual_tools
                if missing_tools:
                    print(f"   ❌ Missing tools: {missing_tools}")
                    return False
                else:
                    print(f"   ✓ All expected tools present")

                # Test 2: Try to call a tool (search_instagram_users)
                print("\n4. Testing tool call (search_instagram_users)...")
                try:
                    result = await session.call_tool(
                        "search_instagram_users",
                        {"query": "test"}
                    )
                    print(f"   ✓ Tool call succeeded")
                    if result.content:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            print(f"   Result preview: {content.text[:100]}...")
                except Exception as e:
                    print(f"   ⚠ Tool call returned error (expected): {str(e)[:100]}")

                # Test 3: Try to call get_user_posts_initial
                print("\n5. Testing tool call (get_user_posts_initial)...")
                try:
                    result = await session.call_tool(
                        "get_user_posts_initial",
                        {"username": "test_user", "limit": 5}
                    )
                    print(f"   ✓ Tool call succeeded")
                    if result.content:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            print(f"   Result preview: {content.text[:100]}...")
                except Exception as e:
                    print(f"   ⚠ Tool call returned error (expected): {str(e)[:100]}")

                print("\n" + "=" * 60)
                print("✓ MCP Protocol Test Completed Successfully!")
                print("=" * 60)
                return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the MCP protocol test"""
    print("\nStarting Instagram MCP Server Test...")
    print("This test uses the standard MCP protocol with ClientSession\n")

    success = await test_mcp_server()

    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
