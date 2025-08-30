#!/usr/bin/env python3
"""
Test the PowerPoint summary tool specifically.
"""

import sys
import os
import json
sys.path.append('.')

from volute_ppt.powerpoint_tools import PowerPointMetadataExtractor, PPTX_AVAILABLE

def test_summary_tool():
    """Test PowerPoint summary functionality."""
    file_path = r'C:\Users\shrey\OneDrive\Desktop\docs\2024.10.27 Project Core - Valuation Analysis_v22.pptx'
    
    print("=" * 60)
    print("POWERPOINT SUMMARY TOOL TEST")
    print("=" * 60)
    
    if not PPTX_AVAILABLE:
        print("❌ python-pptx not available")
        return
    
    if not os.path.exists(file_path):
        print("❌ File does not exist")
        return
        
    try:
        with PowerPointMetadataExtractor() as extractor:
            extractor.open_presentation(file_path)
            
            print("🔍 Extracting detailed slide content...")
            
            # Get detailed analysis
            detailed_metadata = extractor.extract_presentation_metadata(
                include_slide_content=True,
                include_master_slides=False,
                include_layouts=False
            )
            
            print("✅ Analysis complete!")
            print(f"📊 Total Slides: {detailed_metadata.get('totalSlides', 0)}")
            
            # Show detailed info for each slide
            slides = detailed_metadata.get('slides', [])
            for slide in slides:
                slide_num = slide.get('slideNumber', 0)
                shapes = slide.get('shapes', [])
                
                print(f"\n🎯 Slide {slide_num}:")
                print(f"   • Total shapes: {len(shapes)}")
                
                # Categorize shapes
                text_shapes = []
                image_shapes = []
                table_shapes = []
                other_shapes = []
                
                for shape in shapes:
                    shape_type = shape.get('shapeType', '')
                    if 'TEXT' in shape_type or shape.get('textContent', {}).get('hasText', False):
                        text_shapes.append(shape)
                    elif 'PICTURE' in shape_type:
                        image_shapes.append(shape)
                    elif 'TABLE' in shape_type:
                        table_shapes.append(shape)
                    else:
                        other_shapes.append(shape)
                
                print(f"   • Text shapes: {len(text_shapes)}")
                print(f"   • Images: {len(image_shapes)}")
                print(f"   • Tables: {len(table_shapes)}")
                print(f"   • Other shapes: {len(other_shapes)}")
                
                # Show text content if available
                for i, text_shape in enumerate(text_shapes[:2]):  # Show first 2 text shapes
                    text_content = text_shape.get('textContent', {})
                    if text_content.get('hasText'):
                        text = text_content.get('text', '').strip()
                        if text:
                            preview = text[:100] + "..." if len(text) > 100 else text
                            print(f"   📝 Text {i+1}: {preview}")
                            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_summary_tool()
