#!/usr/bin/env python3
"""
Test the MCP tools directly by simulating the tool calls.
"""

import sys
import os
sys.path.append('.')

from server_local import mcp
from volute_ppt.powerpoint_tools import PowerPointAnalysisResult

def test_mcp_tools():
    """Test MCP PowerPoint tools directly."""
    file_path = r'C:\Users\shrey\OneDrive\Desktop\docs\2024.10.27 Project Core - Valuation Analysis_v22.pptx'
    
    print("=" * 60)
    print("MCP TOOLS DIRECT TEST")
    print("=" * 60)
    
    # Test the local file tools first
    print("\n🔍 Testing: list_local_files")
    try:
        result = mcp._tools['list_local_files'](
            directory=r'C:\Users\shrey\OneDrive\Desktop\docs',
            pattern='*.pptx'
        )
        print("✅ list_local_files succeeded:")
        for file_info in result[:3]:  # Show first 3 files
            print(f"   📄 {file_info['name']} ({file_info['size']:,} bytes)")
    except Exception as e:
        print(f"❌ list_local_files failed: {e}")
    
    print("\n🔍 Testing: get_local_system_info")
    try:
        result = mcp._tools['get_local_system_info']()
        print("✅ get_local_system_info succeeded:")
        print(f"   🖥️  Platform: {result.get('platform', 'N/A')}")
        print(f"   🐍 Python: {result.get('python_version', 'N/A')}")
        print(f"   📊 PowerPoint Available: {result.get('powerpoint_available', False)}")
        print(f"   🔧 COM Available: {result.get('com_available', False)}")
    except Exception as e:
        print(f"❌ get_local_system_info failed: {e}")
    
    # Test PowerPoint validation
    print("\n🔍 Testing: validate_powerpoint_file")
    try:
        result = mcp._tools['validate_powerpoint_file'](presentation_path=file_path)
        print("✅ validate_powerpoint_file succeeded:")
        print(f"   📋 Valid: {result.data.get('isValid', False)}")
        print(f"   📁 File exists: {result.data.get('fileExists', False)}")
        print(f"   📊 Slide count: {result.data.get('slideCount', 0)}")
        print(f"   📄 File format: {result.data.get('fileFormat', 'N/A')}")
        print(f"   💾 File size: {result.data.get('fileSize', 0):,} bytes")
    except Exception as e:
        print(f"❌ validate_powerpoint_file failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test PowerPoint summary
    print("\n🔍 Testing: get_powerpoint_summary")
    try:
        result = mcp._tools['get_powerpoint_summary'](presentation_path=file_path)
        if result.success:
            print("✅ get_powerpoint_summary succeeded:")
            summary = result.data.get('summary', {})
            quick_stats = result.data.get('quickStats', {})
            
            print(f"   📋 Title: {summary.get('title', 'N/A')}")
            print(f"   👤 Author: {summary.get('author', 'N/A')}")
            print(f"   📊 Total slides: {quick_stats.get('totalSlides', 0)}")
            print(f"   🖼️  Slides with images: {quick_stats.get('slidesWithImages', 0)}")
            print(f"   📊 Slides with tables: {quick_stats.get('slidesWithTables', 0)}")
            print(f"   📈 Slides with charts: {quick_stats.get('slidesWithCharts', 0)}")
            print(f"   🎯 Total shapes: {quick_stats.get('totalShapes', 0)}")
            print(f"   📏 Avg shapes/slide: {quick_stats.get('averageShapesPerSlide', 0):.1f}")
        else:
            print(f"❌ get_powerpoint_summary failed: {result.error}")
    except Exception as e:
        print(f"❌ get_powerpoint_summary failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test content analysis
    print("\n🔍 Testing: analyze_powerpoint_content (first slide only)")
    try:
        result = mcp._tools['analyze_powerpoint_content'](
            presentation_path=file_path,
            slide_numbers=[1],
            extract_text_only=True
        )
        if result.success:
            print("✅ analyze_powerpoint_content succeeded:")
            slides = result.data.get('slides', [])
            if slides:
                slide = slides[0]
                shapes = slide.get('shapes', [])
                print(f"   🎯 Slide 1 analysis:")
                print(f"   📊 Total shapes: {len(shapes)}")
                
                # Show text content
                for i, shape in enumerate(shapes[:3]):  # First 3 shapes
                    text_content = shape.get('textContent', {})
                    if text_content.get('hasText'):
                        text = text_content.get('text', '').strip()
                        if text:
                            preview = text[:50] + "..." if len(text) > 50 else text
                            print(f"   📝 Shape {i+1}: {preview}")
        else:
            print(f"❌ analyze_powerpoint_content failed: {result.error}")
    except Exception as e:
        print(f"❌ analyze_powerpoint_content failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_tools()
