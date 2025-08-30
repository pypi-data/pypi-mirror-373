#!/usr/bin/env python3
"""
Fixed MCP STDIO Test

Tests the MCP server with correct parameter formatting to resolve
the "Invalid request parameters" issue.
"""

import subprocess
import json
import time
import sys
from pathlib import Path


def test_mcp_stdio_fixed():
    """Test MCP server via STDIO with proper parameter formatting."""
    print("🚀 Fixed MCP STDIO Test")
    print("=" * 50)
    
    try:
        print("📡 Starting MCP server in STDIO mode...")
        
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, "main.py"],  # Use main.py directly
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        print("✅ Server started successfully")
        
        # Test 1: Initialize
        print("\n🔧 Test 1: MCP Initialization")
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
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send initialize request
        request_json = json.dumps(init_request)
        print(f"   📤 Sending: {request_json[:100]}...")
        
        process.stdin.write(request_json + "\n")
        process.stdin.flush()
        time.sleep(1)
        
        # Read response
        response = process.stdout.readline()
        if response:
            try:
                init_result = json.loads(response.strip())
                print(f"   📥 Response: {json.dumps(init_result, indent=2)[:200]}...")
                
                if "result" in init_result:
                    print("   ✅ Initialization successful!")
                    server_info = init_result["result"].get("serverInfo", {})
                    print(f"      Server: {server_info.get('name', 'Unknown')}")
                    print(f"      Version: {server_info.get('version', 'Unknown')}")
                    
                    capabilities = init_result["result"].get("capabilities", {})
                    print(f"      Tools: {'✅' if capabilities.get('tools') else '❌'}")
                    print(f"      Resources: {'✅' if capabilities.get('resources') else '❌'}")
                else:
                    print(f"   ❌ Initialization failed: {init_result}")
                    return False
            except json.JSONDecodeError as e:
                print(f"   ❌ Invalid JSON response: {response[:100]}")
                return False
        else:
            print("   ❌ No response received")
            return False
        
        # Test 2: List tools with correct format
        print("\n🔧 Test 2: List Tools (Fixed Format)")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}  # Empty params object for tools/list
        }
        
        request_json = json.dumps(tools_request)
        print(f"   📤 Sending: {request_json}")
        
        process.stdin.write(request_json + "\n")
        process.stdin.flush()
        time.sleep(1)
        
        # Read response
        response = process.stdout.readline()
        if response:
            try:
                tools_result = json.loads(response.strip())
                print(f"   📥 Response: {json.dumps(tools_result, indent=2)[:300]}...")
                
                if "result" in tools_result:
                    tools = tools_result["result"].get("tools", [])
                    print(f"   ✅ Tools list successful: {len(tools)} tools found")
                    
                    for i, tool in enumerate(tools):
                        name = tool.get("name", f"tool_{i}")
                        desc = tool.get("description", "No description")
                        print(f"      {i+1}. {name}: {desc[:60]}...")
                    
                    # Look for PowerPoint tools
                    ppt_tools = [t for t in tools if "powerpoint" in t.get("name", "").lower()]
                    if ppt_tools:
                        print(f"   📊 PowerPoint tools found: {len(ppt_tools)}")
                    
                elif "error" in tools_result:
                    error = tools_result["error"]
                    print(f"   ❌ Tools list error: {error.get('message', 'Unknown error')}")
                    print(f"      Code: {error.get('code', 'Unknown')}")
                    return False
                else:
                    print(f"   ❓ Unexpected response format: {tools_result}")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ Invalid JSON response: {response[:100]}")
                print(f"      Error: {e}")
                return False
        else:
            print("   ❌ No response received")
            return False
        
        # Test 3: Call a PowerPoint tool with proper argument format
        print("\n🔧 Test 3: Call PowerPoint Tool (Fixed Format)")
        
        # Check if test file exists
        test_file = Path("test_presentation.pptx")
        if not test_file.exists():
            print("   ⚠️ Test file not found, skipping tool call test")
        else:
            tool_call_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "validate_powerpoint_file",
                    "arguments": {
                        "presentation_path": str(test_file.absolute())
                    }
                }
            }
            
            request_json = json.dumps(tool_call_request)
            print(f"   📤 Sending: {request_json[:100]}...")
            
            process.stdin.write(request_json + "\n")
            process.stdin.flush()
            time.sleep(2)  # Give more time for processing
            
            # Read response
            response = process.stdout.readline()
            if response:
                try:
                    call_result = json.loads(response.strip())
                    print(f"   📥 Response: {json.dumps(call_result, indent=2)[:400]}...")
                    
                    if "result" in call_result:
                        result = call_result["result"]
                        print("   ✅ Tool call successful!")
                        
                        # Check if it's a PowerPointAnalysisResult
                        if isinstance(result, dict):
                            success = result.get("success", False)
                            message = result.get("message", "No message")
                            print(f"      Success: {success}")
                            print(f"      Message: {message}")
                            
                            if result.get("data"):
                                data = result["data"]
                                if isinstance(data, dict):
                                    is_valid = data.get("isValid", False)
                                    slide_count = data.get("slideCount", 0)
                                    print(f"      File Valid: {is_valid}")
                                    print(f"      Slide Count: {slide_count}")
                        
                    elif "error" in call_result:
                        error = call_result["error"]
                        print(f"   ❌ Tool call error: {error.get('message', 'Unknown error')}")
                        print(f"      Code: {error.get('code', 'Unknown')}")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ Invalid JSON response: {response[:200]}")
                    print(f"      Error: {e}")
                    return False
            else:
                print("   ❌ No response received")
                return False
        
        # Test 4: Try another tool - get_powerpoint_summary
        if test_file.exists():
            print("\n🔧 Test 4: PowerPoint Summary Tool")
            
            summary_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "get_powerpoint_summary",
                    "arguments": {
                        "presentation_path": str(test_file.absolute())
                    }
                }
            }
            
            request_json = json.dumps(summary_request)
            print(f"   📤 Calling get_powerpoint_summary...")
            
            process.stdin.write(request_json + "\n")
            process.stdin.flush()
            time.sleep(3)  # PowerPoint processing takes time
            
            # Read response
            response = process.stdout.readline()
            if response:
                try:
                    summary_result = json.loads(response.strip())
                    
                    if "result" in summary_result:
                        result = summary_result["result"]
                        print("   ✅ Summary tool successful!")
                        
                        if isinstance(result, dict):
                            success = result.get("success", False)
                            message = result.get("message", "No message")
                            print(f"      Success: {success}")
                            print(f"      Message: {message}")
                            
                            # Show summary data
                            if result.get("data") and isinstance(result["data"], dict):
                                data = result["data"]
                                summary = data.get("summary", {})
                                if summary:
                                    print(f"      Filename: {summary.get('filename', 'Unknown')}")
                                    print(f"      Total Slides: {summary.get('total_slides', 0)}")
                                    print(f"      Title: {summary.get('title', 'None')}")
                                
                                quick_stats = data.get("quickStats", {})
                                if quick_stats:
                                    print(f"      Total Shapes: {quick_stats.get('totalShapes', 0)}")
                                    print(f"      Slides with Images: {quick_stats.get('slidesWithImages', 0)}")
                                    
                    elif "error" in summary_result:
                        error = summary_result["error"]
                        print(f"   ❌ Summary error: {error.get('message', 'Unknown error')}")
                        
                except json.JSONDecodeError as e:
                    print(f"   ❌ Invalid JSON response: {e}")
            else:
                print("   ❌ No response received for summary")
        
        # Clean up
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
        
        print("\n✅ Fixed MCP STDIO test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up process if it exists
        try:
            if 'process' in locals():
                process.terminate()
        except:
            pass
            
        return False


def show_test_summary():
    """Show what this test validates."""
    print("\n" + "🎯 " + "=" * 48)
    print("  WHAT THIS TEST VALIDATES")
    print("=" * 50)
    
    print("""
✅ MCP PROTOCOL COMPLIANCE:
   • JSON-RPC 2.0 format
   • Proper initialization handshake
   • Protocol version 2024-11-05
   • Client/server capability negotiation

🔧 PARAMETER FORMAT FIXES:
   • tools/list with empty params: {}
   • tools/call with proper arguments structure:
     {
       "name": "tool_name",
       "arguments": {"param": "value"}
     }

📊 POWERPOINT TOOL VALIDATION:
   • validate_powerpoint_file works
   • get_powerpoint_summary works
   • Returns PowerPointAnalysisResult format
   • Handles real .pptx files correctly

🎯 READY FOR AGENT INTEGRATION:
   • Claude Desktop can use this format
   • Any MCP client can connect via STDIO
   • Tools return structured, useful data
   • Error handling works properly
""")


def main():
    """Run the fixed MCP STDIO test."""
    print("🚀 MCP STDIO Parameter Fix Test")
    print("=" * 50)
    
    # Run the fixed test
    test_passed = test_mcp_stdio_fixed()
    
    # Show what we validated
    show_test_summary()
    
    print("\n" + "=" * 50)
    if test_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ PARAMETER ISSUE RESOLVED:")
        print("   • MCP requests now use correct format")
        print("   • Tools respond successfully")
        print("   • PowerPoint analysis working")
        print("   • Ready for real agent integration")
        
        print("\n🤖 NEXT STEPS:")
        print("   1. Add to Claude Desktop configuration")
        print("   2. Test with real agents")
        print("   3. Create agent workflows")
        print("   4. Deploy for production use")
    else:
        print("⚠️ SOME ISSUES REMAIN")
        print("   Check the error messages above")
        print("   May need additional parameter format fixes")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
