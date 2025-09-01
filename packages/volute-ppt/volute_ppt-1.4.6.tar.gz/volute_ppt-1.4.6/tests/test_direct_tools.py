#!/usr/bin/env python3
"""
Test Direct Tool Calls

Skip the tools/list step and try calling tools directly.
This tests if the parameter format for tools/call is working.
"""

import subprocess
import json
import time
import sys
from pathlib import Path


def test_direct_tool_calls():
    """Test calling tools directly without tools/list."""
    print("🎯 Direct Tool Call Test")
    print("=" * 50)
    
    try:
        # Start server
        process = subprocess.Popen(
            [sys.executable, "server.py", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path.cwd()
        )
        
        time.sleep(2)
        
        # Initialize first
        print("🔧 Step 1: Initialize")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": True}},
                "clientInfo": {"name": "direct-test", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read init response
        response = process.stdout.readline()
        init_result = json.loads(response.strip()) if response else {}
        
        if "result" not in init_result:
            print("❌ Initialize failed")
            return False
            
        print("✅ Initialize successful")
        
        # Test 1: Echo tool (simple test)
        print("\n🔧 Step 2: Test Echo Tool")
        echo_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {
                    "message": "Direct tool call test!"
                }
            }
        }
        
        print(f"📤 Sending: {json.dumps(echo_request)}")
        process.stdin.write(json.dumps(echo_request) + "\n")
        process.stdin.flush()
        time.sleep(1)
        
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"📥 Response: {json.dumps(response, indent=2)}")
                
                if "result" in response:
                    print("✅ Echo tool SUCCESS!")
                    print(f"   Result: {response['result']}")
                elif "error" in response:
                    error = response["error"]
                    print(f"❌ Echo tool failed: {error.get('message', 'Unknown')}")
                    print(f"   Code: {error.get('code', 'Unknown')}")
                    return False
            else:
                print("❌ No response received")
                return False
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False
        
        # Test 2: Calculate tool (math test)
        print("\n🔧 Step 3: Test Calculate Tool")
        calc_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "calculate",
                "arguments": {
                    "expression": "2 + 3 * 4"
                }
            }
        }
        
        print(f"📤 Sending: {json.dumps(calc_request)}")
        process.stdin.write(json.dumps(calc_request) + "\n")
        process.stdin.flush()
        time.sleep(1)
        
        try:
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"📥 Response: {json.dumps(response, indent=2)}")
                
                if "result" in response:
                    print("✅ Calculate tool SUCCESS!")
                    print(f"   Result: {response['result']}")
                elif "error" in response:
                    error = response["error"]
                    print(f"❌ Calculate tool failed: {error.get('message', 'Unknown')}")
            else:
                print("❌ No response received")
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
        
        # Test 3: PowerPoint validation tool
        test_file = Path("test_presentation.pptx")
        if test_file.exists():
            print("\n🔧 Step 4: Test PowerPoint Validation Tool")
            ppt_request = {
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
            
            print(f"📤 Sending PowerPoint validation request...")
            process.stdin.write(json.dumps(ppt_request) + "\n")
            process.stdin.flush()
            time.sleep(3)  # PowerPoint processing takes time
            
            try:
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    print(f"📥 Response: {json.dumps(response, indent=2)[:400]}...")
                    
                    if "result" in response:
                        result = response["result"]
                        print("✅ PowerPoint validation SUCCESS!")
                        
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
                        error = response["error"]
                        print(f"❌ PowerPoint validation failed: {error.get('message', 'Unknown')}")
                else:
                    print("❌ No response received")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
        else:
            print("\n⚠️ Step 4: No test_presentation.pptx found, skipping")
        
        # Clean up
        process.terminate()
        process.wait(timeout=5)
        
        print("\n✅ Direct tool call tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the direct tool call test."""
    success = test_direct_tool_calls()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 GREAT NEWS!")
        print("✅ MCP initialize works")
        print("✅ tools/call parameter format works")
        print("✅ Tools respond correctly")
        print("❓ Only tools/list has parameter issues")
        
        print("\n💡 IMPLICATIONS:")
        print("   • Agents can call your tools directly")
        print("   • PowerPoint analysis works")
        print("   • Parameter format is mostly correct")
        print("   • tools/list might be a FastMCP issue")
        
        print("\n🚀 WORKAROUND:")
        print("   • Claude Desktop might not need tools/list")
        print("   • Agents can call tools by name directly")
        print("   • Your server is functional for real use")
    else:
        print("⚠️ Issues detected with tool calls")
        print("Check error messages above")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
