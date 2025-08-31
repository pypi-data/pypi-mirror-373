#!/usr/bin/env python3
"""Test MCP connection to video-editor-mcp server"""

import asyncio
import sys
from mcp import ClientSession
from mcp.client.stdio import stdio_client


async def test_connection():
    """Test the MCP server connection"""
    # Set environment variable before running
    import os

    os.environ["LOAD_EMBEDDING_MODEL"] = "0"

    from mcp.client.stdio import StdioServerParameters

    server_params = StdioServerParameters(
        command="uv", args=["run", "video-editor-mcp", "vj_KJD3NpMDQsVMC8tYgTRu4w"]
    )

    async with stdio_client(server=server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            print("✓ Successfully connected to MCP server!")

            # List available tools
            tools_response = await session.list_tools()
            print(f"\n✓ Found {len(tools_response.tools)} tools:")
            for tool in tools_response.tools[:5]:  # Show first 5
                print(f"  - {tool.name}: {tool.description[:60]}...")

            # Test a simple tool call
            print("\n✓ Testing search-remote-videos tool...")
            result = await session.call_tool(
                "search-remote-videos", arguments={"query": "skateboarding", "limit": 3}
            )
            print(f"  Got response with {len(result.content)} content items")

            print("\n✓ All tests passed! Server is working correctly.")


if __name__ == "__main__":
    try:
        asyncio.run(test_connection())
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
