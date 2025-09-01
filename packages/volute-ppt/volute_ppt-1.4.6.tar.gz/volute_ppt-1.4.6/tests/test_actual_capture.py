#!/usr/bin/env python3
"""
Test actual slide capture functionality.
"""

import sys
import os
import asyncio
sys.path.append('.')

from server_local import mcp

async def test_actual_capture():
    """Test actual slide image capture with the MCP tools."""
    file_path = r'C:\Users\shrey\OneDrive\Desktop\docs\2024.10.27 Project Core - Valuation Analysis_v22.pptx'
    
    print("=" * 70)
    print("ACTUAL SLIDE CAPTURE TEST")
    print("=" * 70)
    
    if not os.path.exists(file_path):
        print("❌ Test file not found")
        return
    
    try:
        # Test 1: Check capabilities first
        print("\n🔍 Testing: get_slide_capture_capabilities")
        result = await mcp._tool_manager.call_tool('get_slide_capture_capabilities', {})
        
        if hasattr(result, 'content'):
            capabilities = result.content
            print("✅ Capabilities retrieved:")
            print(f"   🖥️  COM Available: {capabilities.get('com_available', False)}")
            print(f"   📊 PowerPoint Available: {capabilities.get('powerpoint_available', False)}")
            print(f"   📏 Max slides per request: {capabilities.get('max_slides_per_request', 0)}")
            print(f"   🎯 Status: {capabilities.get('status', 'Unknown')}")
            
            if not capabilities.get('com_available', False):
                print("❌ COM not available - cannot test image capture")
                return
        else:
            print(f"❌ Unexpected result format: {result}")
            return
        
        # Test 2: Try to capture first slide
        print(f"\n🔍 Testing: capture_powerpoint_slide_images (slide 1 only)")
        params = {
            'presentation_path': file_path,
            'slide_numbers': [1],  # Just capture slide 1 for test
            'image_width': 800,
            'image_height': 600,
            'include_metadata': True
        }
        
        result = await mcp._tool_manager.call_tool('capture_powerpoint_slide_images', params)
        
        if hasattr(result, 'content'):
            capture_result = result.content
            
            if hasattr(capture_result, 'success') and capture_result.success:
                print("✅ Slide capture successful:")
                print(f"   📊 Slides captured: {capture_result.captured_count}")
                print(f"   📝 Message: {capture_result.message}")
                
                if capture_result.slide_images:
                    for slide_num, image_data in capture_result.slide_images.items():
                        image_size = len(image_data)
                        is_base64 = image_data.startswith('data:image/png;base64,')
                        print(f"   🖼️  Slide {slide_num}: {image_size:,} chars, Base64: {is_base64}")
                
                if capture_result.metadata:
                    metadata = capture_result.metadata
                    print(f"   📋 Capture time: {metadata.get('captureTime', 'N/A')}")
                    print(f"   📐 Image size: {metadata.get('imageWidth')}x{metadata.get('imageHeight')}")
                
                print("\n🎉 SUCCESS: Slide images captured and ready for multimodal LLM analysis!")
                print("   The captured images are base64-encoded PNG data URLs")
                print("   Compatible with OpenAI GPT-4 Vision, Claude 3, Gemini Pro Vision, etc.")
                
            else:
                print(f"❌ Capture failed: {getattr(capture_result, 'error', 'Unknown error')}")
                
        else:
            print(f"❌ Unexpected capture result: {result}")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_actual_capture())
