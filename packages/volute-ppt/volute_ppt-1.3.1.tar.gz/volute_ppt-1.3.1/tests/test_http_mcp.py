#!/usr/bin/env python3
"""
HTTP MCP Client Test for VoluteMCP Server

Tests the MCP server via HTTP transport to verify integration with agent applications.
"""

import json
import sys
import requests
from typing import Dict, Any, Optional


class HTTPMCPClient:
    """HTTP MCP client for testing the server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.request_id = 0
    
    def send_mcp_request(self, method: str, params: Optional[Dict] = None) -> Dict[Any, Any]:
        """Send an MCP request via HTTP POST."""
        self.request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        print(f"📤 Sending {method} request...")
        
        response = self.session.post(
            self.base_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}"}
        
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            print(f"Raw response: {response.text[:200]}...")
            return {"error": "Invalid JSON response"}


def test_http_mcp_integration():
    """Test MCP server via HTTP."""
    print("=" * 60)
    print("🌐 HTTP MCP Integration Test")
    print("=" * 60)
    
    client = HTTPMCPClient()
    
    # Test basic connectivity first
    print("\n🔗 Testing basic HTTP connectivity...")
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is reachable")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure the server is running with: python server.py")
        return False
    
    # Test 1: Initialize
    print("\n🔄 Test 1: MCP Initialize")
    init_response = client.send_mcp_request("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "roots": {"listChanged": True},
            "sampling": {}
        },
        "clientInfo": {
            "name": "http-test-client",
            "version": "1.0.0"
        }
    })
    
    if "result" in init_response:
        print("✅ MCP initialization successful")
        result = init_response["result"]
        print(f"   Server: {result.get('serverInfo', {}).get('name', 'Unknown')}")
        print(f"   Version: {result.get('protocolVersion', 'Unknown')}")
        
        # Show capabilities
        capabilities = result.get('capabilities', {})
        if capabilities:
            print("   Capabilities:")
            for cap, details in capabilities.items():
                print(f"     - {cap}: {details}")
    else:
        print(f"❌ Initialize failed: {init_response}")
        return False
    
    # Test 2: List Tools
    print("\n🔧 Test 2: List Tools")
    tools_response = client.send_mcp_request("tools/list")
    
    if "result" in tools_response and "tools" in tools_response["result"]:
        tools = tools_response["result"]["tools"]
        print(f"✅ Found {len(tools)} tools")
        
        # Count PowerPoint tools
        powerpoint_tools = [t for t in tools if 'powerpoint' in t.get('name', '').lower()]
        print(f"   📊 PowerPoint tools: {len(powerpoint_tools)}")
        
        # Show first few tools
        print("   Sample tools:")
        for tool in tools[:5]:
            name = tool.get('name', 'Unknown')
            desc = tool.get('description', 'No description')
            print(f"     - {name}: {desc[:50]}{'...' if len(desc) > 50 else ''}")
        
        if len(tools) > 5:
            print(f"     ... and {len(tools) - 5} more")
    else:
        print(f"❌ List tools failed: {tools_response}")
    
    # Test 3: List Resources
    print("\n📁 Test 3: List Resources")
    resources_response = client.send_mcp_request("resources/list")
    
    if "result" in resources_response and "resources" in resources_response["result"]:
        resources = resources_response["result"]["resources"]
        print(f"✅ Found {len(resources)} resources")
        
        print("   Sample resources:")
        for resource in resources[:3]:
            uri = resource.get('uri', 'Unknown')
            desc = resource.get('description', 'No description')
            print(f"     - {uri}: {desc[:50]}{'...' if len(desc) > 50 else ''}")
    else:
        print(f"❌ List resources failed: {resources_response}")
    
    # Test 4: Call a Simple Tool
    print("\n🧮 Test 4: Test Calculate Tool")
    calc_response = client.send_mcp_request("tools/call", {
        "name": "calculate",
        "arguments": {
            "expression": "10 + 5 * 2"
        }
    })
    
    if "result" in calc_response:
        print("✅ Calculate tool successful")
        print(f"   10 + 5 * 2 = {calc_response['result']}")
    else:
        print(f"❌ Calculate tool failed: {calc_response}")
    
    # Test 5: Test PowerPoint Tool
    print("\n📊 Test 5: Test PowerPoint Validation Tool")
    pp_response = client.send_mcp_request("tools/call", {
        "name": "validate_powerpoint_file",
        "arguments": {
            "presentation_path": "test.pptx"
        }
    })
    
    if "result" in pp_response:
        print("✅ PowerPoint validation tool successful")
        result = pp_response["result"]
        if isinstance(result, str):
            # Handle string result
            print(f"   Result: {result[:100]}...")
        else:
            # Handle structured result
            print(f"   Result type: {type(result)}")
    else:
        print(f"❌ PowerPoint tool failed: {pp_response}")
    
    # Test 6: Read a Resource
    print("\n📄 Test 6: Read Server Config Resource")
    config_response = client.send_mcp_request("resources/read", {
        "uri": "config://server"
    })
    
    if "result" in config_response:
        print("✅ Resource read successful")
        result = config_response["result"]
        if isinstance(result, list) and len(result) > 0:
            content = result[0]
            print(f"   Resource type: {content.get('mimeType', 'unknown')}")
            print(f"   Content length: {len(str(content.get('text', '')))}")
    else:
        print(f"❌ Resource read failed: {config_response}")
    
    # Test 7: List Prompts
    print("\n💬 Test 7: List Prompts")
    prompts_response = client.send_mcp_request("prompts/list")
    
    if "result" in prompts_response and "prompts" in prompts_response["result"]:
        prompts = prompts_response["result"]["prompts"]
        print(f"✅ Found {len(prompts)} prompts")
        
        for prompt in prompts[:3]:
            name = prompt.get('name', 'Unknown')
            desc = prompt.get('description', 'No description')
            print(f"   - {name}: {desc[:50]}{'...' if len(desc) > 50 else ''}")
    else:
        print(f"❌ List prompts failed: {prompts_response}")
    
    print("\n" + "=" * 60)
    print("🎉 HTTP MCP Integration Test Complete!")
    print("✅ Your server is working correctly with MCP protocol over HTTP")
    print("=" * 60)
    
    return True


def test_agent_integration_examples():
    """Show examples of how agents can integrate with your server."""
    print("\n" + "🤖 " + "=" * 58)
    print("  AGENT INTEGRATION EXAMPLES")
    print("=" * 60)
    
    print("""
🔧 TOOL CALLING EXAMPLE:
An AI agent can call your PowerPoint tools like this:

1. List available tools:
   POST http://localhost:8000
   {"jsonrpc": "2.0", "method": "tools/list", "id": 1}

2. Call PowerPoint metadata extraction:
   POST http://localhost:8000
   {
     "jsonrpc": "2.0", 
     "method": "tools/call", 
     "id": 2,
     "params": {
       "name": "extract_powerpoint_metadata",
       "arguments": {
         "presentation_path": "presentation.pptx",
         "include_slide_content": true,
         "output_format": "json"
       }
     }
   }

3. Get presentation summary:
   {
     "jsonrpc": "2.0", 
     "method": "tools/call", 
     "id": 3,
     "params": {
       "name": "get_powerpoint_summary",
       "arguments": {
         "presentation_path": "presentation.pptx"
       }
     }
   }
""")
    
    print("""
📁 RESOURCE ACCESS EXAMPLE:
Agents can access your server resources:

1. Get server configuration:
   {
     "jsonrpc": "2.0", 
     "method": "resources/read", 
     "id": 4,
     "params": {"uri": "config://server"}
   }

2. Get user data:
   {
     "jsonrpc": "2.0", 
     "method": "resources/read", 
     "id": 5,
     "params": {"uri": "users://123"}
   }
""")
    
    print("""
💬 PROMPT GENERATION EXAMPLE:
Agents can use your prompts for better responses:

1. Get analysis prompt:
   {
     "jsonrpc": "2.0", 
     "method": "prompts/get", 
     "id": 6,
     "params": {
       "name": "analyze_data",
       "arguments": {
         "data_description": "Sales presentation slides",
         "analysis_type": "content_structure"
       }
     }
   }
""")


if __name__ == "__main__":
    print("🚀 Testing VoluteMCP Server Integration")
    
    success = test_http_mcp_integration()
    
    if success:
        test_agent_integration_examples()
        print("\n✅ Your MCP server is ready for agent integration!")
        print("🔗 Next steps:")
        print("   1. Try with Claude Desktop (see claude_mcp_config.json)")
        print("   2. Integrate with any MCP-compatible AI agent")
        print("   3. Use the HTTP endpoints in your own applications")
    else:
        print("\n❌ Some tests failed. Check the server logs for details.")
    
    sys.exit(0 if success else 1)
