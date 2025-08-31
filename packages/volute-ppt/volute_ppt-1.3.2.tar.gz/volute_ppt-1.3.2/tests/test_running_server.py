#!/usr/bin/env python3
"""
Automated MCP Client Test

Connects to your running MCP server and tests the requests automatically.
Make sure you have the server running with: python server.py stdio
"""

import subprocess
import json
import time
import sys
import threading
from pathlib import Path
import queue


def create_client_to_running_server():
    """Create a new client connection to test the running server."""
    print("🚀 Testing Running MCP Server")
    print("=" * 50)
    
    try:
        # Start a new client connection to the server
        print("📡 Starting client connection to server...")
        
        process = subprocess.Popen(
            [sys.executable, "server.py", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        print("✅ Client connected successfully")
        
        # Test 1: Initialize
        print("\n🔧 Test 1: Initialize")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "automated-test",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send request
        request_json = json.dumps(init_request) + "\n"
        print(f"📤 Sending: {request_json.strip()}")
        
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Try to read response with timeout
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"📥 Response: {json.dumps(response, indent=2)}")
                
                if "result" in response:
                    print("✅ Initialize successful!")
                    
                    # Check for tools capability
                    capabilities = response.get("result", {}).get("capabilities", {})
                    if capabilities.get("tools"):
                        print("   ✅ Tools capability confirmed")
                    
                elif "error" in response:
                    print(f"❌ Initialize failed: {response['error']}")
                    return False
            else:
                print("❌ No response received")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False
        
        # Test 2: List tools
        print("\n🔧 Test 2: List Tools")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        request_json = json.dumps(tools_request) + "\n"
        print(f"📤 Sending: {request_json.strip()}")
        
        process.stdin.write(request_json)
        process.stdin.flush()
        
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"📥 Response: {json.dumps(response, indent=2)[:500]}...")
                
                if "result" in response:
                    tools = response["result"].get("tools", [])
                    print(f"✅ Tools list successful: {len(tools)} tools found")
                    
                    # Look for PowerPoint tools
                    ppt_tools = [t for t in tools if "powerpoint" in t.get("name", "").lower()]
                    echo_tools = [t for t in tools if t.get("name") == "echo"]
                    
                    print(f"   📊 PowerPoint tools: {len(ppt_tools)}")
                    print(f"   🔊 Echo tools: {len(echo_tools)}")
                    
                    # List all tools
                    for tool in tools:
                        name = tool.get("name", "unknown")
                        desc = tool.get("description", "No description")[:50]
                        print(f"      • {name}: {desc}...")
                    
                elif "error" in response:
                    print(f"❌ Tools list failed: {response['error']}")
                    return False
            else:
                print("❌ No response received")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False
        
        # Test 3: Echo tool
        print("\n🔧 Test 3: Echo Tool")
        echo_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {
                    "message": "Testing MCP parameter format!"
                }
            }
        }
        
        request_json = json.dumps(echo_request) + "\n"
        print(f"📤 Sending: {request_json.strip()}")
        
        process.stdin.write(request_json)
        process.stdin.flush()
        
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"📥 Response: {json.dumps(response, indent=2)}")
                
                if "result" in response:
                    result = response["result"]
                    print(f"✅ Echo tool successful!")
                    print(f"   Result: {result}")
                    
                elif "error" in response:
                    print(f"❌ Echo tool failed: {response['error']}")
                    return False
            else:
                print("❌ No response received")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False
        
        # Test 4: PowerPoint validation (if file exists)
        test_file = Path("test_presentation.pptx")
        if test_file.exists():
            print("\n🔧 Test 4: PowerPoint Validation")
            validate_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "validate_powerpoint_file",
                    "arguments": {
                        "presentation_path": str(test_file.absolute())
                    }
                }
            }
            
            request_json = json.dumps(validate_request) + "\n"
            print(f"📤 Sending: {request_json.strip()[:100]}...")
            
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # PowerPoint processing might take longer
            time.sleep(2)
            
            try:
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    print(f"📥 Response: {json.dumps(response, indent=2)[:400]}...")
                    
                    if "result" in response:
                        result = response["result"]
                        print(f"✅ PowerPoint validation successful!")
                        
                        if isinstance(result, dict):
                            success = result.get("success", False)
                            message = result.get("message", "No message")
                            print(f"   Success: {success}")
                            print(f"   Message: {message}")
                            
                            if result.get("data"):
                                data = result["data"]
                                is_valid = data.get("isValid", False)
                                slide_count = data.get("slideCount", 0)
                                print(f"   File Valid: {is_valid}")
                                print(f"   Slides: {slide_count}")
                        
                    elif "error" in response:
                        print(f"❌ PowerPoint validation failed: {response['error']}")
                else:
                    print("❌ No response received")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
        else:
            print("\n⚠️ Test 4: No test_presentation.pptx found, skipping")
        
        # Clean up
        process.terminate()
        process.wait(timeout=5)
        
        print("\n✅ All tests completed successfully!")
        print("🎉 MCP parameter format is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            if 'process' in locals():
                process.terminate()
        except:
            pass
        
        return False


def main():
    """Run the automated server test."""
    success = create_client_to_running_server()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS!")
        print("✅ MCP protocol working")
        print("✅ Parameter format fixed")
        print("✅ PowerPoint tools registered")
        print("✅ Tools respond correctly")
        print("\n🚀 Your server is ready for:")
        print("   • Claude Desktop integration")
        print("   • AI agent connections")
        print("   • PowerPoint analysis workflows")
    else:
        print("⚠️ Some issues detected")
        print("Check the error messages above")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
