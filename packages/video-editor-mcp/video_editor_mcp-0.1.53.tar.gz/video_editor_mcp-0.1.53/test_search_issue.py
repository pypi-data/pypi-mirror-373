#!/usr/bin/env python3
"""Test script to debug search-remote-videos issue"""

import asyncio
import json
import os
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def test_search(api_key: str):
    """Test the search-remote-videos tool"""

    # Skip embedding model for faster startup
    os.environ["LOAD_EMBEDDING_MODEL"] = "0"

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

    async with stdio_client(server=server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Test search with project_id
            print("Testing search-remote-videos with project_id...")
            result = await session.call_tool(
                "search-remote-videos",
                arguments={
                    "project_id": "797e132b-d937-4a5e-95e9-055dd12d608d",
                    "query": "skateboarding",
                    "include_segments": True,
                },
            )

            print(f"Result: {json.dumps(result, indent=2)}")

            # Also test without project_id
            print("\nTesting search-remote-videos WITHOUT project_id...")
            result2 = await session.call_tool(
                "search-remote-videos",
                arguments={"query": "skateboarding", "include_segments": True},
            )

            print(f"Result without project_id: {json.dumps(result2, indent=2)}")

            return result, result2


if __name__ == "__main__":
    # Use the API key from your environment or specify it here
    api_key = os.environ.get("VJ_API_KEY", "YOUR_API_KEY")
    results = asyncio.run(test_search(api_key))
