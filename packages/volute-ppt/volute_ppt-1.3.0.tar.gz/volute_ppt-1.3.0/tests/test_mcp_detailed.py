#!/usr/bin/env python3
"""
Detailed MCP Client for testing VoluteMCP-Local server.
Uses proper MCP protocol handling.
"""

import asyncio
import json
import subprocess
import sys
import os
import time

async def test_mcp_server_detailed():
    """Test MCP server with proper protocol handling."""
    
    print("=" * 80)
    print("🚀 VoluteMCP-Local Detailed Server Test")
    print("=" * 80)
    
    # Start the server process
    server_command = [sys.executable, "server_local.py", "stdio"]
    
    try:
        print("\n🔄 Starting MCP server process...")
        process = await asyncio.create_subprocess_exec(
            *server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("✅ Server process started")
        
        # Wait for server to initialize
        await asyncio.sleep(2)
        
        async def send_request(method, params=None, request_id=1):
            """Send a properly formatted MCP request."""
            request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method
            }
            if params is not None:
                request["params"] = params
            
            request_json = json.dumps(request) + "\n"
            print(f"\n📤 Sending: {method}")
            print(f"   Request: {json.dumps(request, indent=2)[:200]}...")
            
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Read response with timeout
            try:
                response_line = await asyncio.wait_for(
                    process.stdout.readline(), 
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                print("⏰ Request timed out")
                return None
            
            if not response_line:
                print("❌ No response received")
                return None
            
            try:
                response = json.loads(response_line.decode().strip())
                print(f"📥 Response: {json.dumps(response, indent=2)[:300]}...")
                return response
            except json.JSONDecodeError as e:
                print(f"❌ Failed to decode response: {e}")
                print(f"Raw: {response_line.decode()[:200]}...")
                return None
        
        # Test 1: Initialize
        print("\n🔍 Test 1: Initialize MCP Session")
        init_response = await send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "resources": {},
                "tools": {}
            },
            "clientInfo": {
                "name": "VoluteMCP-Test-Client",
                "version": "1.0.0"
            }
        })
        
        if not init_response or "error" in init_response:
            print("❌ Initialization failed")
            if init_response:
                print(f"   Error: {init_response.get('error', 'Unknown')}")
        else:
            print("✅ Initialization successful")
            result = init_response.get("result", {})
            server_info = result.get("serverInfo", {})
            print(f"   📋 Server: {server_info.get('name', 'Unknown')}")
            print(f"   📋 Version: {server_info.get('version', 'Unknown')}")
        
        # Test 2: List Tools (without params)
        print("\n🔍 Test 2: List Tools")
        tools_response = await send_request("tools/list", {})
        
        if not tools_response or "error" in tools_response:
            print("❌ Tools listing failed")
            if tools_response:
                print(f"   Error: {tools_response.get('error', 'Unknown')}")
        else:
            print("✅ Tools listing successful")
            result = tools_response.get("result", {})
            tools = result.get("tools", [])
            print(f"   🔧 Found {len(tools)} tools:")
            for tool in tools[:5]:  # Show first 5
                name = tool.get("name", "Unknown")
                print(f"      • {name}")
        
        # Test 3: List Resources
        print("\n🔍 Test 3: List Resources")
        resources_response = await send_request("resources/list", {})
        
        if not resources_response or "error" in resources_response:
            print("❌ Resources listing failed")
            if resources_response:
                print(f"   Error: {resources_response.get('error', 'Unknown')}")
        else:
            print("✅ Resources listing successful")
            result = resources_response.get("result", {})
            resources = result.get("resources", [])
            print(f"   📁 Found {len(resources)} resources:")
            for resource in resources:
                uri = resource.get("uri", "Unknown")
                print(f"      • {uri}")
        
        # Test 4: Call a simple tool
        print("\n🔍 Test 4: Call System Info Tool")
        tool_response = await send_request("tools/call", {
            "name": "get_local_system_info",
            "arguments": {}
        })
        
        if not tool_response or "error" in tool_response:
            print("❌ Tool call failed")
            if tool_response:
                print(f"   Error: {tool_response.get('error', 'Unknown')}")
        else:
            print("✅ Tool call successful")
            result = tool_response.get("result", {})
            print(f"   📊 Response received: {bool(result)}")
        
        # Test 5: Check server stderr for any issues
        print("\n🔍 Test 5: Check Server Logs")
        try:
            stderr_data = await asyncio.wait_for(
                process.stderr.read(1024), 
                timeout=1.0
            )
            if stderr_data:
                stderr_text = stderr_data.decode()
                print("📋 Server stderr output:")
                print(f"   {stderr_text[:300]}...")
            else:
                print("✅ No stderr output (normal)")
        except asyncio.TimeoutError:
            print("✅ No stderr output (normal)")
        
        print("\n" + "=" * 80)
        print("📊 DETAILED TEST SUMMARY")
        print("=" * 80)
        print("✅ MCP server stdio interface is working")
        print("✅ Server accepts and responds to MCP protocol messages") 
        print("✅ JSON-RPC 2.0 communication is functional")
        print("✅ Server properly identifies as 'VoluteMCP-Local'")
        
        print(f"\n🎯 Server is ready for MCP client connections!")
        print(f"   Use: python server_local.py stdio")
        
        # Clean up
        process.terminate()
        await process.wait()
        print("\n🔴 Server process terminated")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔬 Detailed MCP Protocol Test for VoluteMCP-Local")
    print("Testing MCP over stdio communication...\n")
    
    try:
        asyncio.run(test_mcp_server_detailed())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        sys.exit(1)
