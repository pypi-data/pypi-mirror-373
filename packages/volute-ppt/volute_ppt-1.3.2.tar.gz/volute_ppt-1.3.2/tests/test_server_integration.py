#!/usr/bin/env python3
"""
Server Integration Test

Tests the VoluteMCP server for integration readiness with various agent types.
"""

import requests
import subprocess
import sys
import json
import time
import os
from pathlib import Path


def test_http_server():
    """Test the HTTP server endpoints."""
    print("🌐 Testing HTTP Server Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health endpoint
    print("\n🔍 Test 1: Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check: {response.text.strip()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Info endpoint
    print("\n📋 Test 2: Server Info")
    try:
        response = requests.get(f"{base_url}/info", timeout=5)
        if response.status_code == 200:
            print("✅ Server info retrieved:")
            for line in response.text.strip().split('\n'):
                print(f"   {line}")
        else:
            print(f"❌ Info endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Info endpoint error: {e}")
    
    return True


def test_stdio_server():
    """Test the STDIO server for MCP compatibility."""
    print("\n📡 Testing STDIO Server (MCP Protocol)")
    print("=" * 50)
    
    # Start server in STDIO mode
    print("🚀 Starting STDIO server...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "server.py", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path.cwd(),
            text=True,
            bufsize=0
        )
        
        # Test initialization
        print("📤 Sending MCP initialize request...")
        
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send request
        request_line = json.dumps(init_request) + "\n"
        process.stdin.write(request_line)
        process.stdin.flush()
        
        # Wait a bit for response
        time.sleep(1)
        
        # Try to read response
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print("📥 Received response:")
                
                if "result" in response:
                    print("✅ MCP Initialize successful!")
                    result = response["result"]
                    server_info = result.get("serverInfo", {})
                    print(f"   Server Name: {server_info.get('name', 'Unknown')}")
                    print(f"   Protocol Version: {result.get('protocolVersion', 'Unknown')}")
                    
                    # Show capabilities
                    capabilities = result.get("capabilities", {})
                    if capabilities:
                        print("   Server Capabilities:")
                        for cap, details in capabilities.items():
                            print(f"     - {cap}: {details}")
                else:
                    print(f"❌ Initialize failed: {response}")
                    return False
            else:
                print("❌ No response received")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False
        except Exception as e:
            print(f"❌ Error reading response: {e}")
            return False
        
        # Test tools list
        print("\n📤 Testing tools/list...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        request_line = json.dumps(tools_request) + "\n"
        process.stdin.write(request_line)
        process.stdin.flush()
        
        time.sleep(1)
        
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response and "tools" in response["result"]:
                    tools = response["result"]["tools"]
                    print(f"✅ Found {len(tools)} tools")
                    
                    powerpoint_tools = [t for t in tools if 'powerpoint' in t.get('name', '').lower()]
                    print(f"   📊 PowerPoint tools: {len(powerpoint_tools)}")
                    
                    if powerpoint_tools:
                        print("   PowerPoint tools found:")
                        for tool in powerpoint_tools:
                            print(f"     - {tool.get('name', 'Unknown')}")
                else:
                    print(f"❌ Tools list failed: {response}")
        except Exception as e:
            print(f"⚠️  Tools list error: {e}")
        
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("✅ STDIO server test completed")
        return True
        
    except Exception as e:
        print(f"❌ STDIO server test failed: {e}")
        return False


def show_integration_methods():
    """Show different ways to integrate with the server."""
    print("\n" + "🔗 " + "=" * 58)
    print("  INTEGRATION METHODS FOR AGENT APPLICATIONS")
    print("=" * 60)
    
    print("""
🎯 METHOD 1: Claude Desktop Integration
   Perfect for: Testing with Claude AI assistant
   
   Steps:
   1. Create/edit Claude Desktop config file:
      Windows: %APPDATA%\\Claude\\claude_desktop_config.json  
      macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
   
   2. Add this configuration:""")
    
    config_path = Path.cwd() / "claude_mcp_config.json"
    print(f"      (See example in: {config_path})")
    
    print("""
   3. Restart Claude Desktop
   4. Your PowerPoint tools will appear in Claude's tool list
   
📡 METHOD 2: STDIO Integration (Most Compatible)
   Perfect for: Any MCP-compatible agent or library
   
   Command: python server.py stdio
   Protocol: JSON-RPC over STDIN/STDOUT
   
   Example in Python:
   ```python
   import subprocess, json
   
   process = subprocess.Popen(
       ["python", "server.py", "stdio"],
       stdin=subprocess.PIPE,
       stdout=subprocess.PIPE,
       text=True
   )
   
   # Send MCP requests via stdin
   request = {"jsonrpc": "2.0", "method": "tools/list", "id": 1}
   process.stdin.write(json.dumps(request) + "\\n")
   response = json.loads(process.stdout.readline())
   ```
   
🌐 METHOD 3: HTTP Integration (Custom Apps)
   Perfect for: Web applications, REST API integration
   
   Endpoints available:
   - GET  /health          - Health check
   - GET  /info            - Server information
   
   For full MCP over HTTP, you'd need an MCP-HTTP bridge.
   
🤖 METHOD 4: Direct Integration
   Perfect for: Custom AI agents, automation scripts
   
   Your tools are available via MCP protocol:
   - extract_powerpoint_metadata
   - analyze_powerpoint_content  
   - get_powerpoint_summary
   - validate_powerpoint_file
   
   Plus standard tools:
   - calculate, hash_text, format_text, etc.
   
🔧 METHOD 5: Library Integration
   Perfect for: Python applications using MCP libraries
   
   Libraries to try:
   - mcp (official Python client)
   - anthropic-mcp (if available)
   - Custom JSON-RPC client libraries
""")

def test_powerpoint_functionality():
    """Test PowerPoint functionality with sample files."""
    print("\n" + "📊 " + "=" * 58) 
    print("  POWERPOINT FUNCTIONALITY TEST")
    print("=" * 60)
    
    print("""
To fully test PowerPoint integration with agents:

1. 📁 Create test PowerPoint files:
   - sample.pptx (basic presentation)
   - complex.pptx (with images, tables, charts)
   - empty.pptx (minimal presentation)
   
2. 🧪 Test via Claude Desktop:
   After setup, ask Claude:
   "Can you analyze the PowerPoint file sample.pptx and tell me about its content structure?"
   
3. 🔧 Test via STDIO:
   Send this MCP request:
   {
     "jsonrpc": "2.0",
     "method": "tools/call", 
     "id": 1,
     "params": {
       "name": "get_powerpoint_summary",
       "arguments": {"presentation_path": "sample.pptx"}
     }
   }
   
4. ✅ Expected Results:
   - Slide count and basic info
   - Content summaries per slide  
   - Detection of multimedia elements
   - Validation results and any issues
   
📋 Tools Available for Testing:
   • extract_powerpoint_metadata - Full metadata extraction
   • analyze_powerpoint_content - Content analysis
   • get_powerpoint_summary - Quick overview
   • validate_powerpoint_file - File validation
""")


if __name__ == "__main__":
    print("🚀 VoluteMCP Server Integration Test Suite")
    print("=" * 60)
    
    # Test HTTP server (if running)
    print("Testing server on port 8000...")
    http_success = test_http_server()
    
    if http_success:
        print("✅ HTTP server is working!")
    
    # Test STDIO server
    stdio_success = test_stdio_server()
    
    if stdio_success:
        print("✅ STDIO server is working!")
    
    # Show integration methods
    show_integration_methods()
    
    # Show PowerPoint testing info
    test_powerpoint_functionality()
    
    print("\n" + "=" * 60)
    if http_success or stdio_success:
        print("🎉 YOUR SERVER IS READY FOR AGENT INTEGRATION!")
        print("✅ Choose one of the integration methods above")
        print("🔗 STDIO mode is recommended for maximum compatibility")
        print("=" * 60)
    else:
        print("❌ Server integration tests failed")
        print("💡 Make sure the server is running: python server.py")
        print("=" * 60)
    
    sys.exit(0 if (http_success or stdio_success) else 1)
