#!/usr/bin/env python3
"""Diagnose MCP server startup issues"""

import asyncio
import subprocess
import os


def test_direct_launch():
    """Test if the server can be launched directly"""
    print("Testing direct server launch...")

    # Test 1: Direct uv run
    cmd = [
        "uv",
        "run",
        "--directory",
        "/Users/stankley/Development/video-jungle-mcp",
        "video-editor-mcp",
        "vj_KJD3NpMDQsVMC8tYgTRu4w",
    ]

    env = os.environ.copy()
    env["LOAD_EMBEDDING_MODEL"] = "0"

    print(f"Running: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Give it a moment to start
    import time

    time.sleep(2)

    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print(f"Process exited with code: {proc.returncode}")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False
    else:
        print("✓ Server started successfully")
        proc.terminate()
        return True


def test_uvx_launch():
    """Test if uvx can launch the server"""
    print("\nTesting uvx launch...")

    # Test 2: uvx launch
    cmd = [
        "uvx",
        "-p",
        "3.11",
        "--from",
        "video_editor_mcp@0.1.35",
        "video-editor-mcp",
        "vj_KJD3NpMDQsVMC8tYgTRu4w",
    ]

    env = os.environ.copy()
    env["LOAD_EMBEDDING_MODEL"] = "0"

    print(f"Running: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # Give it a moment to start
    import time

    time.sleep(3)

    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print(f"Process exited with code: {proc.returncode}")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False
    else:
        print("✓ Server started successfully")
        proc.terminate()
        return True


async def test_mcp_connection():
    """Test MCP connection with proper timeout handling"""
    print("\nTesting MCP client connection...")

    from mcp import ClientSession
    from mcp.client.stdio import stdio_client, StdioServerParameters

    server_params = StdioServerParameters(
        command="uv",
        args=[
            "run",
            "--directory",
            "/Users/stankley/Development/video-jungle-mcp",
            "video-editor-mcp",
            "vj_KJD3NpMDQsVMC8tYgTRu4w",
        ],
        env={"LOAD_EMBEDDING_MODEL": "0"},
    )

    try:
        # Use a longer timeout for slow startup
        async with asyncio.timeout(30):  # 30 second timeout
            async with stdio_client(server=server_params) as (
                read_stream,
                write_stream,
            ):
                async with ClientSession(read_stream, write_stream) as session:
                    # Try to initialize
                    await session.initialize()
                    print("✓ MCP connection successful!")

                    # Get server info
                    tools = await session.list_tools()
                    print(f"✓ Server has {len(tools.tools)} tools available")
                    return True
    except asyncio.TimeoutError:
        print("✗ Connection timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def main():
    print("=== MCP Server Diagnostic Tool ===\n")

    # Check if uvx is available
    try:
        subprocess.run(["uvx", "--version"], capture_output=True, check=True)
        print("✓ uvx is installed")
    except:
        print("✗ uvx is not installed or not in PATH")
        print("Install with: pip install uv")

    # Test direct launch
    direct_ok = test_direct_launch()

    # Test uvx launch
    uvx_ok = test_uvx_launch()

    # Test MCP connection
    mcp_ok = asyncio.run(test_mcp_connection())

    print("\n=== Summary ===")
    print(f"Direct launch: {'✓ OK' if direct_ok else '✗ Failed'}")
    print(f"UVX launch: {'✓ OK' if uvx_ok else '✗ Failed'}")
    print(f"MCP connection: {'✓ OK' if mcp_ok else '✗ Failed'}")

    if not direct_ok and not uvx_ok:
        print("\n⚠️  Server cannot start. Check:")
        print("1. API key is valid")
        print("2. Dependencies are installed")
        print("3. Python environment is correct")
    elif not mcp_ok:
        print(
            "\n⚠️  Server starts but MCP connection fails. This might be a timing issue."
        )
        print("Try increasing timeouts in your application.")


if __name__ == "__main__":
    main()
