#!/usr/bin/env python3
"""
Test script to convert a PowerPoint file to markdown using markitdown
"""

from markitdown import MarkItDown
import os

def test_pptx_conversion():
    """Test converting a PPTX file to markdown"""
    
    # Path to the PowerPoint file
    pptx_path = r"C:\Users\shrey\OneDrive\Desktop\docs\2024.10.27 Project Core - Valuation Analysis_v22.pptx"
    
    # Check if file exists
    if not os.path.exists(pptx_path):
        print(f"❌ File not found: {pptx_path}")
        return
    
    print(f"📄 Converting file: {pptx_path}")
    print(f"📊 File size: {os.path.getsize(pptx_path):,} bytes")
    print("=" * 80)
    
    try:
        # Initialize MarkItDown
        md = MarkItDown()
        
        # Convert the file
        print("🔄 Converting...")
        result = md.convert(pptx_path)
        
        # Print the results
        print("✅ Conversion successful!")
        print("=" * 80)
        print("MARKDOWN CONTENT:")
        print("=" * 80)
        print(result.text_content)
        
        # Also save to a file for easier viewing
        output_path = r"C:\Users\shrey\projects\volutemcp\converted_pptx_output.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.text_content)
        
        print("=" * 80)
        print(f"📁 Output also saved to: {output_path}")
        
        # Print some stats
        lines = result.text_content.split('\n')
        print(f"📈 Statistics:")
        print(f"   - Total characters: {len(result.text_content):,}")
        print(f"   - Total lines: {len(lines):,}")
        print(f"   - Non-empty lines: {len([l for l in lines if l.strip()]):,}")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pptx_conversion()
