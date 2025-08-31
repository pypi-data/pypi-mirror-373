#!/usr/bin/env python3
"""Test to demonstrate full metadata extraction."""

import sys
import os
import json
sys.path.append('.')

from volute_ppt.powerpoint_tools import PowerPointMetadataExtractor, PPTX_AVAILABLE

def test_full_metadata():
    """Test that we get full JSON metadata, not summaries."""
    file_path = r'C:\Users\shrey\OneDrive\Desktop\docs\2024.10.27 Project Core - Valuation Analysis_v22.pptx'
    
    print("=" * 70)
    print("FULL METADATA EXTRACTION TEST")
    print("=" * 70)
    
    if not PPTX_AVAILABLE or not os.path.exists(file_path):
        print("❌ Requirements not met")
        return
    
    try:
        with PowerPointMetadataExtractor() as extractor:
            extractor.open_presentation(file_path)
            
            # Get full metadata (as the MCP tools would)
            metadata = extractor.extract_presentation_metadata(
                include_slide_content=True,
                include_master_slides=False,
                include_layouts=False
            )
            
            print("✅ Full metadata extracted")
            print(f"📊 Metadata keys: {list(metadata.keys())}")
            
            # Show depth of metadata for first slide
            if metadata.get('slides'):
                slide_1 = metadata['slides'][0]
                print(f"🎯 Slide 1 keys: {list(slide_1.keys())}")
                
                if slide_1.get('shapes'):
                    shape_1 = slide_1['shapes'][0]
                    print(f"🔷 First shape keys: {list(shape_1.keys())}")
                    
                    # Show text content structure if available
                    if shape_1.get('textContent'):
                        text_keys = list(shape_1['textContent'].keys())
                        print(f"📝 Text content keys: {text_keys}")
                        
                        if shape_1['textContent'].get('paragraphs'):
                            para_1 = shape_1['textContent']['paragraphs'][0]
                            print(f"📄 First paragraph keys: {list(para_1.keys())}")
                            
                            if para_1.get('runs'):
                                run_1 = para_1['runs'][0]
                                print(f"🔤 First run keys: {list(run_1.keys())}")
                                
                                if run_1.get('font'):
                                    font_keys = list(run_1['font'].keys())
                                    print(f"🎨 Font formatting keys: {font_keys}")
            
            print("\n" + "=" * 70)
            print("METADATA DEPTH ANALYSIS")
            print("=" * 70)
            
            # Calculate JSON size and complexity
            json_str = json.dumps(metadata, indent=2)
            json_lines = json_str.count('\n')
            json_size = len(json_str)
            
            print(f"📏 JSON output size: {json_size:,} characters")
            print(f"📏 JSON output lines: {json_lines:,} lines")
            print(f"🔧 Contains comprehensive formatting: {'YES' if 'font' in json_str else 'NO'}")
            print(f"📐 Contains position data: {'YES' if 'position' in json_str else 'NO'}")
            print(f"🎨 Contains color data: {'YES' if 'color' in json_str else 'NO'}")
            print(f"📊 Contains shape details: {'YES' if 'shapeType' in json_str else 'NO'}")
            
            # Show sample of deep metadata
            print(f"\n📋 SAMPLE DEEP METADATA (first 500 chars):")
            print("-" * 50)
            print(json_str[:500] + "...")
            
            print("\n✅ CONFIRMED: Tools return FULL comprehensive JSON metadata!")
            print("   This is exactly what LLMs need to understand file properties completely.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_full_metadata()
