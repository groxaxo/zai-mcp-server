#!/usr/bin/env python3
"""
Test script for ZAI MCP Server
"""

import json
import subprocess
import os
import sys

if not os.environ.get("ZAI_API_KEY"):
    print("Error: ZAI_API_KEY environment variable is required", file=sys.stderr)
    print("Set it with: export ZAI_API_KEY='your-api-key'", file=sys.stderr)
    sys.exit(1)


def send_to_server(message):
    """Send JSON-RPC message to server"""
    server_path = os.environ.get(
        "ZAI_SERVER_PATH", "/home/op/zai-mcp-server/src/server.py"
    )

    server_process = subprocess.Popen(
        ["python3", server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Send message
    server_process.stdin.write(json.dumps(message) + "\n")
    server_process.stdin.flush()

    # Read response
    response_line = server_process.stdout.readline()
    server_process.terminate()
    server_process.wait()

    return json.loads(response_line)


def test_initialize():
    """Test server initialization"""
    print("Testing initialization...")
    request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}

    response = send_to_server(request)
    print(
        f"✓ Initialize: {response['result']['serverInfo']['name']} v{response['result']['serverInfo']['version']}\n"
    )


def test_list_tools():
    """Test listing tools"""
    print("Testing tools list...")
    request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

    response = send_to_server(request)
    tools = response["result"]["tools"]

    print(f"✓ Available tools ({len(tools)}):")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    print()


def test_list_resources():
    """Test listing resources"""
    print("Testing resources list...")
    request = {"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}

    response = send_to_server(request)
    resources = response["result"]["resources"]

    print(f"✓ Available resources ({len(resources)}):")
    for resource in resources:
        print(f"  - {resource['uri']}: {resource['description']}")
    print()


def test_read_resource():
    """Test reading a resource"""
    print("Testing resource read...")
    request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "resources/read",
        "params": {"uri": "zai://status"},
    }

    response = send_to_server(request)
    status = json.loads(response["result"]["contents"][0]["text"])

    print(f"✓ Server status:")
    print(f"  Status: {status['status']}")
    print(f"  Model: {status['model']}")
    print(f"  API Endpoint: {status['api_endpoint']}")
    print(f"  Tools: {', '.join(status['tools'])}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("ZAI MCP Server Test Suite")
    print("=" * 60)
    print()

    try:
        test_initialize()
        test_list_tools()
        test_list_resources()
        test_read_resource()

        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
