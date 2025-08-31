#!/usr/bin/env python3
"""
Final comprehensive test of all MCP tools.
"""

import sys
import os
import asyncio
sys.path.append('.')

from server_local import mcp

async def test_all_tools():
    """Test all registered MCP tools."""
    file_path = r'C:\Users\shrey\OneDrive\Desktop\docs\2024.10.27 Project Core - Valuation Analysis_v22.pptx'
    
    print("=" * 70)
    print("COMPREHENSIVE MCP TOOLS TEST")
    print("=" * 70)
    
    # Get all registered tools
    tools = mcp._tool_manager._tools
    print(f"Found {len(tools)} registered tools:")
    for tool_name in tools.keys():
        print(f"  • {tool_name}")
    
    print("\n" + "=" * 70)
    print("TESTING EACH TOOL")
    print("=" * 70)
    
    # Test 1: get_local_system_info
    print("\n🔍 Testing: get_local_system_info")
    try:
        result = await mcp._tool_manager.call_tool('get_local_system_info', {})
        if result.get('isError', False):
            print(f"❌ Failed: {result.get('content', 'Unknown error')}")
        else:
            data = result.get('content', {})
            print("✅ Success:")
            print(f"   🖥️  Platform: {data.get('platform', 'N/A')}")
            print(f"   🐍 Python: {data.get('python_version', 'N/A')}")
            print(f"   📊 PowerPoint: {data.get('powerpoint_available', False)}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: list_local_files
    print("\n🔍 Testing: list_local_files")
    try:
        params = {
            'directory': r'C:\Users\shrey\OneDrive\Desktop\docs',
            'pattern': '*.pptx'
        }
        result = await mcp._tool_manager.call_tool('list_local_files', params)
        if result.get('isError', False):
            print(f"❌ Failed: {result.get('content', 'Unknown error')}")
        else:
            files = result.get('content', [])
            print(f"✅ Success: Found {len(files)} PowerPoint files")
            for file_info in files[:3]:  # Show first 3
                name = file_info.get('name', 'Unknown')
                size = file_info.get('size', 0)
                print(f"   📄 {name} ({size:,} bytes)")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: validate_powerpoint_file
    print("\n🔍 Testing: validate_powerpoint_file")
    try:
        params = {'presentation_path': file_path}
        result = await mcp._tool_manager.call_tool('validate_powerpoint_file', params)
        if result.get('isError', False):
            print(f"❌ Failed: {result.get('content', 'Unknown error')}")
        else:
            data = result.get('content', {})
            if hasattr(data, 'data'):  # PowerPointAnalysisResult
                validation = data.data
                print("✅ Success:")
                print(f"   📋 Valid: {validation.get('isValid', False)}")
                print(f"   📊 Slide count: {validation.get('slideCount', 0)}")
                print(f"   💾 File size: {validation.get('fileSize', 0):,} bytes")
            else:
                print(f"✅ Success: {data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: get_powerpoint_summary
    print("\n🔍 Testing: get_powerpoint_summary")
    try:
        params = {'presentation_path': file_path}
        result = await mcp._tool_manager.call_tool('get_powerpoint_summary', params)
        if result.get('isError', False):
            print(f"❌ Failed: {result.get('content', 'Unknown error')}")
        else:
            data = result.get('content', {})
            if hasattr(data, 'data'):  # PowerPointAnalysisResult
                analysis_data = data.data
                summary = analysis_data.get('summary', {})
                quick_stats = analysis_data.get('quickStats', {})
                print("✅ Success:")
                print(f"   📋 Title: {summary.get('title', 'N/A')}")
                print(f"   👤 Author: {summary.get('author', 'N/A')}")
                print(f"   📊 Total slides: {quick_stats.get('totalSlides', 0)}")
                print(f"   🎯 Total shapes: {quick_stats.get('totalShapes', 0)}")
            else:
                print(f"✅ Success: {data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 5: analyze_powerpoint_content (first slide)
    print("\n🔍 Testing: analyze_powerpoint_content (slide 1)")
    try:
        params = {
            'presentation_path': file_path,
            'slide_numbers': [1],
            'extract_text_only': False
        }
        result = await mcp._tool_manager.call_tool('analyze_powerpoint_content', params)
        if result.get('isError', False):
            print(f"❌ Failed: {result.get('content', 'Unknown error')}")
        else:
            data = result.get('content', {})
            if hasattr(data, 'data'):  # PowerPointAnalysisResult
                analysis_data = data.data
                slides = analysis_data.get('slides', [])
                if slides:
                    slide = slides[0]
                    shapes = slide.get('shapes', [])
                    print("✅ Success:")
                    print(f"   🎯 Slide 1 shapes: {len(shapes)}")
                    
                    # Count text shapes
                    text_shapes = [s for s in shapes if s.get('textContent', {}).get('hasText', False)]
                    print(f"   📝 Text shapes: {len(text_shapes)}")
                    
                    # Show sample text
                    for i, shape in enumerate(text_shapes[:2]):
                        text = shape.get('textContent', {}).get('text', '').strip()
                        if text:
                            preview = text[:40] + "..." if len(text) > 40 else text
                            print(f"   📄 Text {i+1}: {preview}")
            else:
                print(f"✅ Success: {data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE - All tools have been tested!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_all_tools())
