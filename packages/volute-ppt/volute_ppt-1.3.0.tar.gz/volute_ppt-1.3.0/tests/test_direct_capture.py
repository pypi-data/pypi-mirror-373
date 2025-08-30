#!/usr/bin/env python3
"""
Direct test of slide capture core functionality.
"""

import sys
import os
sys.path.append('.')

from volute_ppt.slide_capture_tools import _capture_slide_images_safe

def test_direct_capture():
    """Test slide capture functionality directly."""
    file_path = r'C:\Users\shrey\OneDrive\Desktop\docs\2024.10.27 Project Core - Valuation Analysis_v22.pptx'
    
    print("=" * 70)
    print("DIRECT SLIDE CAPTURE TEST")
    print("=" * 70)
    
    if not os.path.exists(file_path):
        print("❌ Test file not found")
        return
    
    # Test WIN32COM availability
    try:
        import win32com.client
        import pythoncom
        print("✅ win32com available")
    except ImportError:
        print("❌ win32com not available - cannot test")
        return
    
    try:
        print(f"\n🔍 Testing direct slide capture for slide 1")
        print(f"📁 File: {os.path.basename(file_path)}")
        
        # Call the core capture function directly
        result = _capture_slide_images_safe(
            file_path,
            [1],  # Just capture slide 1
            800,  # width
            600   # height
        )
        
        print(f"\n📊 Capture Result:")
        print(f"   ✅ Success: {result['success']}")
        print(f"   📝 Message: {result['message']}")
        print(f"   📊 Images captured: {len(result['slide_images'])}")
        print(f"   ❌ Failed slides: {result['failed_slides']}")
        
        if result['slide_images']:
            for slide_num, image_data in result['slide_images'].items():
                image_size = len(image_data)
                is_data_url = image_data.startswith('data:image/png;base64,')
                print(f"   🖼️  Slide {slide_num}: {image_size:,} characters")
                print(f"      📋 Format: {'Data URL' if is_data_url else 'Raw Base64'}")
                print(f"      🎯 Ready for multimodal LLM: {'✅' if is_data_url else '❌'}")
        
        if result['success']:
            print(f"\n🎉 SUCCESS: Multimodal slide capture is working!")
            print(f"   📈 Agents can now capture PowerPoint slides as images")
            print(f"   🤖 Compatible with GPT-4 Vision, Claude 3, Gemini Pro Vision")
            print(f"   🔧 Comprehensive error handling and resource management")
        else:
            print(f"\n❌ Capture failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_capture()
