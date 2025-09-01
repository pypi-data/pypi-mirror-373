#!/usr/bin/env python3
"""
Fixed test script that properly handles ToolResult objects.
"""

import sys
import os
import asyncio
sys.path.append('.')

from server_local import mcp

async def test_tools_fixed():
    """Test MCP PowerPoint tools with proper ToolResult handling."""
    file_path = r'C:\Users\shrey\OneDrive\Desktop\docs\2024.10.27 Project Core - Valuation Analysis_v22.pptx'
    
    print("=" * 70)
    print("FIXED MCP TOOLS TEST")
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
        if hasattr(result, 'is_error') and result.is_error:
            print(f"❌ Failed: {result.content}")
        else:
            data = result.content
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
        if hasattr(result, 'is_error') and result.is_error:
            print(f"❌ Failed: {result.content}")
        else:
            files = result.content
            print(f"✅ Success: Found {len(files)} PowerPoint files")
            for file_info in files[:2]:  # Show first 2
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
        if hasattr(result, 'is_error') and result.is_error:
            print(f"❌ Failed: {result.content}")
        else:
            # Result.content should be a PowerPointAnalysisResult
            analysis_result = result.content
            if hasattr(analysis_result, 'success') and analysis_result.success:
                validation = analysis_result.data
                print("✅ Success:")
                print(f"   📋 Valid: {validation.get('isValid', False)}")
                print(f"   📊 Slide count: {validation.get('slideCount', 0)}")
                print(f"   💾 File size: {validation.get('fileSize', 0):,} bytes")
            else:
                print(f"❌ Failed: {getattr(analysis_result, 'error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: get_powerpoint_summary
    print("\n🔍 Testing: get_powerpoint_summary")
    try:
        params = {'presentation_path': file_path}
        result = await mcp._tool_manager.call_tool('get_powerpoint_summary', params)
        if hasattr(result, 'is_error') and result.is_error:
            print(f"❌ Failed: {result.content}")
        else:
            analysis_result = result.content
            if hasattr(analysis_result, 'success') and analysis_result.success:
                data = analysis_result.data
                summary = data.get('summary', {})
                quick_stats = data.get('quickStats', {})
                print("✅ Success:")
                print(f"   📋 Title: {summary.get('title', 'N/A')}")
                print(f"   👤 Author: {summary.get('author', 'N/A')}")
                print(f"   📊 Total slides: {quick_stats.get('totalSlides', 0)}")
                print(f"   🎯 Total shapes: {quick_stats.get('totalShapes', 0)}")
            else:
                print(f"❌ Failed: {getattr(analysis_result, 'error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 5: analyze_powerpoint_content (first slide, text only)
    print("\n🔍 Testing: analyze_powerpoint_content (slide 1, text only)")
    try:
        params = {
            'presentation_path': file_path,
            'slide_numbers': [1],
            'extract_text_only': True  # Use text-only mode to avoid serialization issues
        }
        result = await mcp._tool_manager.call_tool('analyze_powerpoint_content', params)
        if hasattr(result, 'is_error') and result.is_error:
            print(f"❌ Failed: {result.content}")
        else:
            analysis_result = result.content
            if hasattr(analysis_result, 'success') and analysis_result.success:
                data = analysis_result.data
                slides = data.get('slides', [])
                if slides:
                    slide = slides[0]
                    text_content = slide.get('textContent', [])
                    print("✅ Success:")
                    print(f"   🎯 Slide 1 text elements: {len(text_content)}")
                    
                    # Show sample text
                    for i, text_item in enumerate(text_content[:2]):
                        text = text_item.get('text', '').strip()
                        if text:
                            preview = text[:40] + "..." if len(text) > 40 else text
                            print(f"   📄 Text {i+1}: {preview}")
                else:
                    print("✅ Success: No slides found")
            else:
                print(f"❌ Failed: {getattr(analysis_result, 'error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 70)
    print("✅ FIXED TEST COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_tools_fixed())
