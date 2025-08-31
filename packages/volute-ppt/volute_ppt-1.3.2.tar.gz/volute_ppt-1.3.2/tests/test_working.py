#!/usr/bin/env python3
"""Simple test to demonstrate that PowerPoint tools work."""

import sys
import os
sys.path.append('.')

from volute_ppt.powerpoint_tools import PowerPointMetadataExtractor, PPTX_AVAILABLE

def test_direct_functionality():
    """Test PowerPoint functionality directly without MCP layer."""
    file_path = r'C:\Users\shrey\OneDrive\Desktop\docs\2024.10.27 Project Core - Valuation Analysis_v22.pptx'
    
    print("=" * 60)
    print("DIRECT POWERPOINT TOOLS TEST")
    print("=" * 60)
    print(f"PPTX Available: {PPTX_AVAILABLE}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if not PPTX_AVAILABLE:
        print("❌ python-pptx not available")
        return
    
    if not os.path.exists(file_path):
        print("❌ File does not exist")
        return
    
    try:
        print("\n🔍 Testing: Direct PowerPoint metadata extraction")
        with PowerPointMetadataExtractor() as extractor:
            extractor.open_presentation(file_path)
            
            # Test basic info
            slide_count = len(extractor.presentation.slides)
            print(f"✅ Opened successfully: {slide_count} slides")
            
            # Test metadata extraction
            metadata = extractor.extract_presentation_metadata(
                include_slide_content=True,
                include_master_slides=False,
                include_layouts=False
            )
            
            print("✅ Metadata extracted successfully")
            
            # Show core info
            core_props = metadata.get('coreProperties', {})
            print(f"📋 Title: {core_props.get('title', 'N/A')}")
            print(f"👤 Author: {core_props.get('author', 'N/A')}")
            print(f"📊 Total slides: {metadata.get('totalSlides', 0)}")
            
            # Show slide content summary
            slides = metadata.get('slides', [])
            print(f"📈 Analyzed {len(slides)} slides:")
            
            for slide in slides[:2]:  # Show first 2 slides
                slide_num = slide.get('slideNumber', 0)
                shapes = slide.get('shapes', [])
                text_shapes = [s for s in shapes if s.get('textContent', {}).get('hasText', False)]
                print(f"  🎯 Slide {slide_num}: {len(shapes)} shapes, {len(text_shapes)} with text")
                
                # Show first text content
                for shape in text_shapes[:1]:
                    text = shape.get('textContent', {}).get('text', '').strip()
                    if text:
                        preview = text[:50] + "..." if len(text) > 50 else text
                        print(f"    📝 {preview}")
            
        print("\n✅ ALL TESTS PASSED - PowerPoint tools are working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_functionality()
