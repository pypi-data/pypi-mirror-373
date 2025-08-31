#!/usr/bin/env python3
"""Example of correct MCP usage with video-editor-mcp server"""

import asyncio
import os
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def use_video_editor_mcp(api_key: str):
    """Example function showing correct MCP usage"""

    # Option 1: Skip embedding model loading for faster startup
    os.environ["LOAD_EMBEDDING_MODEL"] = "0"

    # Correct way to specify server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=[
            "run",
            "--directory",
            "/Users/stankley/Development/video-jungle-mcp",
            "video-editor-mcp",
            api_key,
        ],
    )

    # Keep everything in the same async context
    async with stdio_client(server=server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize with timeout (optional)
            await session.initialize()

            # Now you can use the session for all operations
            # Example: Search for videos
            result = await session.call_tool(
                "search-remote-videos", arguments={"query": "skateboarding", "limit": 5}
            )

            # Process results...
            return result


# For pydantic-ai style usage:
from pydantic_ai.mcp import MCPClient


async def use_with_pydantic_ai(api_key: str):
    """Example using pydantic-ai's MCP client"""

    os.environ["LOAD_EMBEDDING_MODEL"] = "0"

    # Create MCP client with proper parameters
    mcp_client = MCPClient(
        server=StdioServerParameters(
            command="uv",
            args=[
                "run",
                "--directory",
                "/Users/stankley/Development/video-jungle-mcp",
                "video-editor-mcp",
                api_key,
            ],
        )
    )

    # Use the client - it handles the context management
    async with mcp_client:
        # Your agent can now use the MCP tools
        # The key is to keep all operations within this context
        pass


if __name__ == "__main__":
    api_key = "vj_KJD3NpMDQsVMC8tYgTRu4w"
    asyncio.run(use_video_editor_mcp(api_key))
