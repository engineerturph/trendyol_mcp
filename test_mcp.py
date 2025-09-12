#!/usr/bin/env python3
"""
Test script for the Trendyol MCP Server
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path


async def test_mcp_server():
    """Test the MCP server functionality"""

    print("Testing Trendyol MCP Server...")

    # Test the server by running it with a simple request
    try:
        # Create a test request
        test_request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}

        print("Starting MCP server...")

        # Run the MCP server
        process = subprocess.Popen(
            [sys.executable, "mcp.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent,
        )

        # Send the initialization request first
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": True}, "sampling": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        print("Sending initialization request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Send the tools list request
        print("Sending tools list request...")
        process.stdin.write(json.dumps(test_request) + "\n")
        process.stdin.flush()

        # Close stdin to signal we're done
        process.stdin.close()

        # Wait for response with timeout
        try:
            stdout, stderr = process.communicate(timeout=30)

            if stderr:
                print(f"Server stderr: {stderr}")

            if stdout:
                print(f"Server response: {stdout}")

                # Try to parse the response
                lines = stdout.strip().split("\n")
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if "result" in response:
                                print(f"✅ Server responded successfully!")
                                print(f"Available tools: {response['result']}")
                                return True
                        except json.JSONDecodeError:
                            continue

            print("❌ No valid JSON response received")
            return False

        except subprocess.TimeoutExpired:
            print("❌ Server test timed out")
            process.kill()
            return False

    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    if success:
        print("\n🎉 MCP Server test completed successfully!")
        print("\nTo use this server:")
        print("1. Add the server configuration to your MCP client")
        print("2. Use the 'search_trendyol' tool with a query parameter")
        print("\nExample tool call:")
        print(
            '{"name": "search_trendyol", "arguments": {"query": "iPhone 15", "target_count": 10}}'
        )
    else:
        print("\n❌ MCP Server test failed!")
        sys.exit(1)
