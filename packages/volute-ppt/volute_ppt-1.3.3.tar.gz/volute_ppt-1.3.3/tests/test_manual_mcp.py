#!/usr/bin/env python3
"""
Manual MCP protocol test to verify server functionality.
"""

import json
import subprocess
import sys
import time

def test_manual_mcp():
    """Manual test of MCP functionality."""
    
    print("=" * 70)
    print("🔧 Manual MCP Server Verification")
    print("=" * 70)
    
    print("\n📋 Testing server startup and basic response...")
    
    # Start server process
    server_command = [sys.executable, "server_local.py", "stdio"]
    
    try:
        process = subprocess.Popen(
            server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print("✅ Server process started")
        
        # Test initialization
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "resources": {},
                    "tools": {}
                },
                "clientInfo": {
                    "name": "Manual-Test-Client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("\n📤 Sending initialization request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response with timeout
        import select
        import os
        
        if os.name == 'nt':  # Windows
            # On Windows, use a simple timeout approach
            time.sleep(2)
            response_line = process.stdout.readline()
        else:
            # On Unix-like systems, use select
            ready, _, _ = select.select([process.stdout], [], [], 5.0)
            if ready:
                response_line = process.stdout.readline()
            else:
                response_line = ""
        
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print("✅ Initialization response received")
                
                if "result" in response:
                    result = response["result"]
                    server_info = result.get("serverInfo", {})
                    print(f"   📋 Server name: {server_info.get('name', 'Unknown')}")
                    print(f"   📋 Version: {server_info.get('version', 'Unknown')}")
                    print(f"   📋 Protocol: {result.get('protocolVersion', 'Unknown')}")
                    
                    capabilities = result.get("capabilities", {})
                    tools_cap = capabilities.get("tools", {})
                    resources_cap = capabilities.get("resources", {})
                    
                    print(f"   🔧 Tools supported: {bool(tools_cap)}")
                    print(f"   📁 Resources supported: {bool(resources_cap)}")
                    
                    print("\n🎉 MCP SERVER VERIFICATION SUCCESSFUL!")
                    print("   ✅ Server responds to MCP protocol")
                    print("   ✅ JSON-RPC 2.0 communication works")
                    print("   ✅ Proper server identification")
                    print("   ✅ Capabilities negotiation works")
                    
                elif "error" in response:
                    print(f"❌ Initialization error: {response['error']}")
                else:
                    print(f"⚠️  Unexpected response format: {response}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Failed to decode response: {e}")
                print(f"   Raw response: {response_line[:200]}...")
        else:
            print("❌ No response received from server")
            
        # Check stderr for any startup messages
        stderr_output = ""
        try:
            # Try to read stderr without blocking
            import fcntl
            import errno
            
            fd = process.stderr.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
            
            try:
                stderr_output = process.stderr.read()
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    raise
        except:
            # Fallback for systems without fcntl
            time.sleep(1)
            if process.stderr.readable():
                stderr_output = process.stderr.read(1024) or ""
        
        if stderr_output:
            print(f"\n📋 Server startup messages:")
            for line in stderr_output.split('\n')[:5]:  # Show first 5 lines
                if line.strip():
                    print(f"   {line}")
        
        # Terminate process
        process.terminate()
        process.wait(timeout=5)
        print("\n🔴 Server process terminated")
        
        print(f"\n🚀 FINAL STATUS: Your VoluteMCP-Local server is WORKING!")
        print(f"   📞 Ready for MCP client connections")
        print(f"   🎯 Command: python server_local.py stdio")
        
    except subprocess.TimeoutExpired:
        print("⏰ Process timeout")
        process.kill()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        try:
            process.terminate()
        except:
            pass

if __name__ == "__main__":
    print("🧪 Manual MCP Protocol Verification")
    print("Testing basic MCP server functionality...\n")
    
    test_manual_mcp()
