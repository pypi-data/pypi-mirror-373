#!/usr/bin/env python3
"""
Test script for PowerPoint tools with the specified file.
"""

import sys
import os
sys.path.append('.')

from volute_ppt.powerpoint_tools import PowerPointMetadataExtractor, PPTX_AVAILABLE

def test_powerpoint_file():
    """Test PowerPoint file analysis."""
    file_path = r'C:\Users\shrey\OneDrive\Desktop\docs\2024.10.27 Project Core - Valuation Analysis_v22.pptx'
    
    print("=" * 60)
    print("POWERPOINT FILE ANALYSIS TEST")
    print("=" * 60)
    print(f"File: {file_path}")
    print(f"PPTX Library Available: {PPTX_AVAILABLE}")
    print(f"File Exists: {os.path.exists(file_path)}")
    
    if os.path.exists(file_path):
        print(f"File Size: {os.path.getsize(file_path):,} bytes")
    
    print("\n" + "=" * 60)
    print("TESTING: File Validation")
    print("=" * 60)
    
    if not PPTX_AVAILABLE:
        print("❌ python-pptx not available")
        return
    
    if not os.path.exists(file_path):
        print("❌ File does not exist")
        return
    
    try:
        # Test opening the presentation
        print("🔍 Opening presentation...")
        with PowerPointMetadataExtractor() as extractor:
            extractor.open_presentation(file_path)
            print("✅ Successfully opened presentation")
            
            # Get basic info
            slide_count = len(extractor.presentation.slides)
            print(f"📊 Slide Count: {slide_count}")
            
            # Test metadata extraction
            print("\n" + "=" * 60)
            print("TESTING: Basic Metadata Extraction")
            print("=" * 60)
            
            metadata = extractor.extract_presentation_metadata(
                include_slide_content=False,
                include_master_slides=False,
                include_layouts=False
            )
            
            print("✅ Basic metadata extracted successfully")
            print(f"📋 Presentation Title: {metadata.get('coreProperties', {}).get('title', 'N/A')}")
            print(f"👤 Author: {metadata.get('coreProperties', {}).get('author', 'N/A')}")
            print(f"📅 Created: {metadata.get('coreProperties', {}).get('created', 'N/A')}")
            print(f"🔧 Modified: {metadata.get('coreProperties', {}).get('modified', 'N/A')}")
            
            # Test with slide content
            print("\n" + "=" * 60)
            print("TESTING: Full Content Analysis")
            print("=" * 60)
            
            full_metadata = extractor.extract_presentation_metadata(
                include_slide_content=True,
                include_master_slides=False,
                include_layouts=False
            )
            
            print("✅ Full content analysis completed")
            slides = full_metadata.get('slides', [])
            print(f"📊 Analyzed {len(slides)} slides")
            
            # Show summary for first few slides
            for i, slide in enumerate(slides[:3]):  # Show first 3 slides
                slide_num = slide.get('slideNumber', i+1)
                shape_count = len(slide.get('shapes', []))
                text_shapes = [s for s in slide.get('shapes', []) if s.get('hasText')]
                
                print(f"  🎯 Slide {slide_num}: {shape_count} shapes, {len(text_shapes)} with text")
            
            if len(slides) > 3:
                print(f"  ... and {len(slides) - 3} more slides")
                
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_powerpoint_file()
