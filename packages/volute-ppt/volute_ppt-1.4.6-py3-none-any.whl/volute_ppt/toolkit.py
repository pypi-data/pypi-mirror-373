"""
PowerPoint toolkit providing direct access to all PowerPoint automation functions.

This module exposes all PowerPoint tools as direct Python functions that can be imported
and used without MCP server setup.

Example Usage:
    from volute_ppt.toolkit import (
        extract_powerpoint_metadata, 
        capture_slide_images,
        edit_slide_text_content
    )
    
    # Extract metadata from a presentation
    metadata = extract_powerpoint_metadata("presentation.pptx")
    
    # Capture slides as images
    images = capture_slide_images("presentation.pptx", slide_numbers=[1, 2, 3])
"""

import os
import base64
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path

# Import core dependencies
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Core PowerPoint Analysis Functions
# =============================================================================

def extract_powerpoint_metadata(
    presentation_path: str,
    include_slide_content: bool = True,
    include_master_slides: bool = False,
    include_layouts: bool = False,
    output_format: str = "summary"
) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from a PowerPoint presentation.
    
    Args:
        presentation_path: Path to the PowerPoint file
        include_slide_content: Include detailed slide content analysis
        include_master_slides: Include slide master information
        include_layouts: Include slide layout information
        output_format: Output format ('json' or 'summary')
    
    Returns:
        Dictionary containing complete presentation metadata
    """
    from .powerpoint_metadata import PowerPointMetadataExtractor
    
    with PowerPointMetadataExtractor(presentation_path) as extractor:
        return extractor.extract_presentation_metadata(
            include_slide_content=include_slide_content,
            include_master_slides=include_master_slides,
            include_layouts=include_layouts
        )

def analyze_powerpoint_content(
    presentation_path: str,
    slide_numbers: Optional[List[int]] = None,
    extract_text_only: bool = False
) -> Dict[str, Any]:
    """
    Analyze content of specific slides in a PowerPoint presentation.
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_numbers: Specific slide numbers to analyze (1-based). If None, analyzes all slides
        extract_text_only: Extract only text content, skip formatting details
    
    Returns:
        Dictionary containing slide content analysis
    """
    from .powerpoint_metadata import PowerPointMetadataExtractor
    
    with PowerPointMetadataExtractor(presentation_path) as extractor:
        extractor.open_presentation(presentation_path)
        if extract_text_only:
            content = extractor.extract_text_content(slide_numbers)
        else:
            metadata = extractor.extract_presentation_metadata(
                include_slide_content=True,
                include_master_slides=False,
                include_layouts=False
            )
            
            if slide_numbers:
                # Filter to specific slides
                filtered_slides = []
                for slide_data in metadata.get("slides", []):
                    if slide_data.get("slideNumber") in slide_numbers:
                        filtered_slides.append(slide_data)
                metadata["slides"] = filtered_slides
                metadata["analyzedSlides"] = slide_numbers
            
            content = metadata
        
        return content

def validate_powerpoint_file(presentation_path: str) -> Dict[str, Any]:
    """
    Validate a PowerPoint file and check for common issues.
    
    Args:
        presentation_path: Path to the PowerPoint file to validate
    
    Returns:
        Dictionary containing validation results
    """
    from .powerpoint_metadata import PowerPointMetadataExtractor
    
    with PowerPointMetadataExtractor(presentation_path) as extractor:
        return extractor.validate_file()

def analyze_slide_text(
    filepath: str,
    slide_numbers: List[int]
) -> Dict[str, Any]:
    """
    Extract text content from specific PowerPoint slides using markitdown.
    
    This function uses the markitdown package to extract clean text content from specified slides.
    It focuses on extracting readable text content without formatting details, making it ideal
    for text analysis, content review, or AI processing workflows.
    
    Args:
        filepath: Path to the PowerPoint presentation file
        slide_numbers: List of slide numbers to process (1-based, e.g., [1, 3, 5])
    
    Returns:
        Dictionary containing extracted text content for each slide
        
    Raises:
        FileNotFoundError: If the PowerPoint file doesn't exist
        ValueError: If file format is not supported
        ImportError: If required packages are not available
    """
    import os
    from .powerpoint_metadata import PowerPointMetadataExtractor
    
    # Validate file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"PowerPoint file not found: {filepath}")
    
    # Check file extension
    file_ext = os.path.splitext(filepath)[1].lower()
    if file_ext not in ['.pptx', '.ppt']:
        raise ValueError(f"Unsupported file format: {file_ext}. Only .pptx and .ppt files are supported.")
    
    # Import markitdown
    try:
        from markitdown import MarkItDown
    except ImportError:
        raise ImportError("markitdown package is not installed. Please install it with: pip install markitdown")
    
    # Initialize markitdown converter
    md_converter = MarkItDown()
    
    try:
        # Convert the entire presentation to markdown first (for reference)
        result = md_converter.convert(filepath)
        full_text = result.text_content if hasattr(result, 'text_content') else str(result)
        
        slide_texts = {}
        
        # Use our existing metadata extractor to get slide-specific content
        with PowerPointMetadataExtractor(filepath) as extractor:
            for slide_num in slide_numbers:
                if slide_num < 1 or slide_num > len(extractor.presentation.slides):
                    logger.warning(f"Slide number {slide_num} is out of range. Skipping.")
                    continue
                
                slide = extractor.presentation.slides[slide_num - 1]  # Convert to 0-based
                
                # Extract text content from the slide
                slide_text_parts = []
                
                # Extract text from all shapes
                for shape in slide.shapes:
                    if hasattr(shape, 'text_frame') and shape.has_text_frame:
                        text = shape.text_frame.text.strip()
                        if text:
                            slide_text_parts.append(text)
                    
                    # Extract text from tables
                    if hasattr(shape, 'table'):
                        try:
                            table = shape.table
                            for row in table.rows:
                                row_texts = []
                                for cell in row.cells:
                                    cell_text = cell.text.strip()
                                    if cell_text:
                                        row_texts.append(cell_text)
                                if row_texts:
                                    slide_text_parts.append(" | ".join(row_texts))
                        except:
                            pass  # Skip if not a table or has issues
                
                # Combine all text from the slide
                combined_text = "\n\n".join(slide_text_parts)
                
                # Apply markitdown-style cleaning
                cleaned_text = _clean_text_markitdown_style(combined_text)
                
                slide_texts[slide_num] = {
                    "slide_number": slide_num,
                    "text_content": cleaned_text,
                    "word_count": len(cleaned_text.split()) if cleaned_text else 0,
                    "character_count": len(cleaned_text) if cleaned_text else 0
                }
        
        # Prepare response data
        return {
            "success": True,
            "filepath": filepath,
            "requested_slides": slide_numbers,
            "extracted_slides": list(slide_texts.keys()),
            "slide_texts": slide_texts,
            "summary": {
                "total_slides_requested": len(slide_numbers),
                "slides_successfully_extracted": len(slide_texts),
                "total_word_count": sum(slide["word_count"] for slide in slide_texts.values()),
                "total_character_count": sum(slide["character_count"] for slide in slide_texts.values())
            }
        }
        
    except Exception as e:
        raise RuntimeError(f"Failed to extract text content: {str(e)}")

def _clean_text_markitdown_style(text: str) -> str:
    """
    Apply markitdown-style text cleaning to extracted text.
    
    This function mimics the text cleaning approach used by markitdown
    to produce clean, readable text content.
    """
    if not text:
        return ""
    
    import re
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Clean up bullet points and list markers
    text = re.sub(r'^[•\-\*]\s*', '', text, flags=re.MULTILINE)
    
    # Remove excessive punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\"\'\/\-]', '', text)
    
    # Normalize line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove trailing/leading whitespace from lines
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    
    return text.strip()

# =============================================================================
# Slide Management Functions
# =============================================================================

def manage_presentation_slides(
    presentation_path: str,
    dsl_operations: str
) -> Dict[str, Any]:
    """
    Manage PowerPoint slides using a domain-specific language (DSL).
    
    Operations supported:
    - add_slide: position=1, layout="Title Slide"
    - delete_slide: slide_number=3
    - move_slide: from=1, to=5 
    - duplicate_slide: source=2, position=end
    
    Args:
        presentation_path: Path to the PowerPoint file
        dsl_operations: Slide operations in DSL format
    
    Returns:
        Dictionary containing operation results
    """
    from .powerpoint.slide_executor import execute_slide_operations
    return execute_slide_operations(presentation_path, dsl_operations)

def bulk_slide_operations(
    presentation_path: str,
    operations: List[str],
    validate_before_execute: bool = True,
    stop_on_error: bool = True
) -> Dict[str, Any]:
    """
    Execute multiple slide operations with validation and error handling.
    
    Args:
        presentation_path: Path to the PowerPoint file
        operations: List of DSL operations to execute
        validate_before_execute: Validate operations before execution
        stop_on_error: Stop execution on first error
    
    Returns:
        Dictionary containing operation results
    """
    from .powerpoint.slide_executor import execute_bulk_operations
    return execute_bulk_operations(
        presentation_path,
        operations,
        validate_before_execute,
        stop_on_error
    )

# =============================================================================
# Visual & Multimodal Functions
# =============================================================================

def capture_slide_images(
    presentation_path: str,
    slide_numbers: List[int],
    image_width: int = 1024,
    image_height: int = 768,
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Capture PowerPoint slides as base64-encoded PNG images for AI analysis.
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_numbers: Slide numbers to capture (1-based)
        image_width: Width of captured images in pixels
        image_height: Height of captured images in pixels
        include_metadata: Include capture metadata
    
    Returns:
        Dictionary containing slide images and metadata
    """
    from .slide_capture_tools import _capture_slide_images_safe
    
    result = _capture_slide_images_safe(
        presentation_path,
        slide_numbers,
        image_width,
        image_height
    )
    
    if include_metadata:
        result["metadata"] = {
            "captureTime": datetime.now().isoformat(),
            "presentationPath": presentation_path,
            "presentationName": os.path.basename(presentation_path),
            "requestedSlides": slide_numbers,
            "imageFormat": "PNG",
            "imageWidth": image_width,
            "imageHeight": image_height,
            "totalRequested": len(slide_numbers),
            "capturedSuccessfully": len(result["slide_images"]),
            "failedSlides": result["failed_slides"]
        }
    
    return result

def compare_presentation_versions(
    original_path: str,
    modified_path: str,
    include_visual_comparison: bool = False,
    max_slides_to_compare: int = 10
) -> Dict[str, Any]:
    """
    Compare two versions of a PowerPoint presentation.
    
    Args:
        original_path: Path to original presentation
        modified_path: Path to modified presentation
        include_visual_comparison: Include visual slide comparisons
        max_slides_to_compare: Maximum slides to compare
    
    Returns:
        Dictionary containing comparison results
    """
    from .powerpoint_metadata import PowerPointMetadataExtractor
    
    # Extract metadata from both presentations
    with PowerPointMetadataExtractor(original_path) as extractor:
        original_metadata = extractor.extract_presentation_metadata(
            include_slide_content=True,
            include_master_slides=False,
            include_layouts=False
        )
    
    with PowerPointMetadataExtractor(modified_path) as extractor:
        modified_metadata = extractor.extract_presentation_metadata(
            include_slide_content=True,
            include_master_slides=False,
            include_layouts=False
        )
    
    # Compare metadata
    comparison = compare_metadata(original_metadata, modified_metadata)
    
    # Add visual comparison if requested
    if include_visual_comparison:
        comparison["visual_diffs"] = compare_slide_visuals(
            original_path,
            modified_path,
            max_slides=max_slides_to_compare
        )
    
    return comparison

# =============================================================================
# Content Editing Functions
# =============================================================================

def edit_slide_text_content(
    presentation_path: str,
    slide_number: int,
    text_updates: Dict[str, str],
    convert_bullets: bool = True,
    preserve_formatting: bool = True,
    auto_resize: bool = True
) -> Dict[str, Any]:
    """
    Edit text content with intelligent bullet conversion.
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_number: Slide number to edit (1-based)
        text_updates: Map of shape names to new text content
        convert_bullets: Convert bullet text to native PowerPoint bullets
        preserve_formatting: Preserve existing text formatting
        auto_resize: Automatically resize shapes to fit content
    
    Returns:
        Dictionary containing edit results
    """
    from .shape_editing_tools import edit_slide_text
    return edit_slide_text(
        presentation_path,
        slide_number,
        text_updates,
        convert_bullets,
        preserve_formatting,
        auto_resize
    )

def apply_shape_formatting(
    presentation_path: str,
    slide_number: int,
    shape_formatting: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Apply comprehensive shape formatting.
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_number: Slide number to edit (1-based)
        shape_formatting: Map of shape names to formatting properties
    
    Returns:
        Dictionary containing formatting results
    """
    from .shape_editing_tools import apply_formatting
    return apply_formatting(
        presentation_path,
        slide_number,
        shape_formatting
    )

def manage_slide_shapes(
    presentation_path: str,
    slide_number: int,
    shape_operations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add, delete, copy, transform shapes.
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_number: Slide number to edit (1-based)
        shape_operations: List of shape operations to perform
    
    Returns:
        Dictionary containing operation results
    """
    from .shape_editing_tools import manage_shapes
    return manage_shapes(
        presentation_path,
        slide_number,
        shape_operations
    )

# =============================================================================
# Utility Functions
# =============================================================================

def get_system_capabilities() -> Dict[str, Any]:
    """
    Get information about PowerPoint capabilities and requirements.
    
    Returns:
        Dictionary containing system capabilities
    """
    # Get win32com availability
    WIN32COM_AVAILABLE = False
    try:
        import win32com.client
        import pythoncom
        WIN32COM_AVAILABLE = True
        logger.info("win32com available for PowerPoint operations")
    except ImportError as e:
        logger.warning(f"win32com not available: {e}")

    capabilities = {
        "com_available": WIN32COM_AVAILABLE,
        "supported_formats": [".pptx", ".ppt"],
        "supported_image_format": "PNG",
        "min_image_size": {"width": 100, "height": 100},
        "max_image_size": {"width": 2048, "height": 2048},
        "default_image_size": {"width": 1024, "height": 768},
        "multimodal_ready": True,
        "data_url_format": True,
        "requirements": {
            "windows_os": True,
            "powerpoint_installed": "Required for COM automation",
            "pywin32": "Required Python package"
        }
    }
            
    # Test PowerPoint availability if COM is available
    if WIN32COM_AVAILABLE:
        try:
            pythoncom.CoInitialize()
            try:
                win32com.client.Dispatch("PowerPoint.Application")
                capabilities["powerpoint_available"] = True
                capabilities["status"] = "Ready for PowerPoint operations"
            except Exception as e:
                capabilities["powerpoint_available"] = False
                capabilities["status"] = f"PowerPoint not available: {str(e)}"
            finally:
                pythoncom.CoUninitialize()
        except Exception:
            capabilities["powerpoint_available"] = False
            capabilities["status"] = "COM initialization failed"
    else:
        capabilities["powerpoint_available"] = False
        capabilities["status"] = "win32com not available"
            
    return capabilities

def compare_metadata(original: Dict[str, Any], modified: Dict[str, Any]) -> Dict[str, Any]:
    """Compare PowerPoint metadata dictionaries."""
    differences = {
        "slide_count_diff": len(modified.get("slides", [])) - len(original.get("slides", [])),
        "changes": [],
        "added_slides": [],
        "removed_slides": [],
        "modified_slides": []
    }
    
    # Compare slides
    original_slides = {slide.get("slideNumber"): slide for slide in original.get("slides", [])}
    modified_slides = {slide.get("slideNumber"): slide for slide in modified.get("slides", [])}
    
    # Find added and removed slides
    for slide_num in modified_slides:
        if slide_num not in original_slides:
            differences["added_slides"].append(slide_num)
            
    for slide_num in original_slides:
        if slide_num not in modified_slides:
            differences["removed_slides"].append(slide_num)
            
    # Compare content of slides present in both versions
    for slide_num in original_slides:
        if slide_num in modified_slides:
            orig_slide = original_slides[slide_num]
            mod_slide = modified_slides[slide_num]
            
            # Compare basic properties
            if orig_slide.get("layout") != mod_slide.get("layout"):
                differences["changes"].append(f"Slide {slide_num}: Layout changed")
            
            if orig_slide.get("title") != mod_slide.get("title"):
                differences["changes"].append(f"Slide {slide_num}: Title changed")
                differences["modified_slides"].append(slide_num)
                
            # Deep comparison would be done here
            
    # Add summary
    differences["summary"] = {
        "total_changes": len(differences["changes"]),
        "slides_added": len(differences["added_slides"]),
        "slides_removed": len(differences["removed_slides"]),
        "slides_modified": len(differences["modified_slides"])
    }
    
    return differences

def compare_slide_visuals(original_path: str, modified_path: str, max_slides: int) -> Dict[str, Any]:
    """Compare slide visuals between presentations."""
    # This would implement actual visual comparison
    # For now, just capture and return the images
    from .slide_capture_tools import _capture_slide_images_safe
    
    slides_to_compare = list(range(1, max_slides + 1))
    
    original_images = _capture_slide_images_safe(original_path, slides_to_compare)
    modified_images = _capture_slide_images_safe(modified_path, slides_to_compare)
    
    return {
        "original_images": original_images.get("slide_images", {}),
        "modified_images": modified_images.get("slide_images", {})
    }

# Export all functions
__all__ = [
    # Core Analysis
    'extract_powerpoint_metadata',
    'analyze_powerpoint_content',
    'validate_powerpoint_file',
    'analyze_slide_text',
    
    # Slide Management
    'manage_presentation_slides',
    'bulk_slide_operations',
    
    # Visual & Multimodal
    'capture_slide_images',
    'compare_presentation_versions',
    
    # Content Editing
    'edit_slide_text_content',
    'apply_shape_formatting',
    'manage_slide_shapes',
    
    # Utilities
    'get_system_capabilities'
]
