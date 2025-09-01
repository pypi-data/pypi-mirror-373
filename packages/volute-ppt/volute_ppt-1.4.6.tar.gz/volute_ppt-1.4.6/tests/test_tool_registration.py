#!/usr/bin/env python3
"""
Test script to verify that the slide capture tool is properly registered.
"""

import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'volute_ppt'))

from fastmcp import FastMCP
from volute_ppt.powerpoint_tools import register_powerpoint_tools
from volute_ppt.slide_capture_tools import register_slide_capture_tools

def test_tool_registration():
    """Test that all PowerPoint tools are properly registered."""
    
    # Create a test server
    mcp = FastMCP("Test-Server")
    
    print("🔧 Registering PowerPoint tools...")
    try:
        register_powerpoint_tools(mcp)
        print("✅ PowerPoint tools registered successfully")
    except Exception as e:
        print(f"❌ Error registering PowerPoint tools: {e}")
        return False
    
    print("\n🖼️ Registering slide capture tools...")
    try:
        register_slide_capture_tools(mcp)
        print("✅ Slide capture tools registered successfully")
    except Exception as e:
        print(f"❌ Error registering slide capture tools: {e}")
        return False
    
    # Get all registered tools
    print("\n📋 Checking registered tools:")
    tool_names = []
    try:
        # Use the get_tools() method to access registered tools
        tools = mcp.get_tools()
        for tool in tools:
            tool_name = tool.name
            tool_names.append(tool_name)
            print(f"  • {tool_name}")
    except Exception as e:
        print(f"❌ Error accessing tools with get_tools(): {e}")
        # Fallback: try to access tool manager directly
        try:
            if hasattr(mcp, '_tool_manager'):
                tools = mcp._tool_manager.tools
                for tool_name in tools.keys():
                    tool_names.append(tool_name)
                    print(f"  • {tool_name} (via _tool_manager)")
            else:
                print("Could not access tools via any method")
                return False
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            return False
    
    print(f"\n📊 Total tools registered: {len(tool_names)}")
    
    # Check for expected PowerPoint tools
    expected_tools = [
        "extract_powerpoint_metadata",
        "analyze_powerpoint_content", 
        "get_powerpoint_summary",
        "validate_powerpoint_file",
        "capture_powerpoint_slides"  # This should now be available
    ]
    
    print("\n🔍 Verifying expected tools:")
    all_found = True
    for tool in expected_tools:
        if tool in tool_names:
            print(f"  ✅ {tool} - FOUND")
        else:
            print(f"  ❌ {tool} - MISSING")
            all_found = False
    
    if all_found:
        print(f"\n🎉 SUCCESS: All {len(expected_tools)} PowerPoint tools are properly registered!")
        
        # Special check for the slide capture tool
        if "capture_powerpoint_slides" in tool_names:
            print("🆕 CRITICAL SUCCESS: capture_powerpoint_slides tool is now available for multimodal analysis!")
        
        return True
    else:
        print(f"\n❌ FAILURE: Some PowerPoint tools are missing from registration")
        return False

if __name__ == "__main__":
    print("🧪 Testing PowerPoint tool registration...\n")
    success = test_tool_registration()
    
    if success:
        print("\n✅ All tests passed! The slide capture tool registration issue has been resolved.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Tool registration issues still exist.")
        sys.exit(1)
