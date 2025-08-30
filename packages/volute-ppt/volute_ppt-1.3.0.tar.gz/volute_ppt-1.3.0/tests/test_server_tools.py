#!/usr/bin/env python3
"""
Test script to connect to the local MCP server and list available tools.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_server_tools():
    """Test the local MCP server and list available tools."""
    try:
        # Start the server with stdio transport
        server_process = subprocess.Popen(
            [sys.executable, "server_local.py", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Send initialize request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": False
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send the request
        request_line = json.dumps(initialize_request) + "\n"
        server_process.stdin.write(request_line)
        server_process.stdin.flush()
        
        # Read the response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print("Initialize Response:")
            print(json.dumps(response, indent=2))
            print()
        
        # Send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        request_line = json.dumps(tools_request) + "\n"
        server_process.stdin.write(request_line)
        server_process.stdin.flush()
        
        # Read the tools response
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print("Available Tools:")
            print("=" * 60)
            
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"Found {len(tools)} tools:")
                print()
                
                for i, tool in enumerate(tools, 1):
                    print(f"{i}. {tool['name']}")
                    print(f"   Description: {tool.get('description', 'No description')}")
                    
                    # Show input schema if available
                    if 'inputSchema' in tool:
                        schema = tool['inputSchema']
                        if 'properties' in schema:
                            props = list(schema['properties'].keys())
                            print(f"   Parameters: {', '.join(props)}")
                    
                    print()
            else:
                print("No tools found or error in response")
                print(json.dumps(response, indent=2))
        
        # Check stderr for any error messages
        stderr_output = server_process.stderr.read()
        if stderr_output:
            print("Server Messages:")
            print(stderr_output)
        
        # Terminate the server
        server_process.terminate()
        server_process.wait()
        
    except Exception as e:
        print(f"Error testing server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_server_tools())
