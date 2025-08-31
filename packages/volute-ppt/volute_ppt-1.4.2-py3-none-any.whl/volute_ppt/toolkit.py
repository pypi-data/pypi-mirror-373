"""
PowerPoint toolkit providing direct access to PowerPoint automation tools.
This module exposes all PowerPoint tools as standalone functions that can be directly imported
and used without dealing with MCP server configuration.

Example Usage:
    from volute_ppt.toolkit import extract_powerpoint_metadata, capture_slide_images

    # Extract metadata from a presentation
    metadata = extract_powerpoint_metadata("presentation.pptx")
    
    # Capture slides as images
    images = capture_slide_images("presentation.pptx", slide_numbers=[1, 2, 3])
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .powerpoint_metadata import PowerPointMetadataExtractor
from .slide_capture_tools import capture_powerpoint_slides, get_slide_capture_capabilities
from .powerpoint_tools import extract_powerpoint_metadata as _extract_metadata
from .advanced_powerpoint_tools import (
    manage_presentation_slides as _manage_slides,
    bulk_slide_operations as _bulk_operations,
    compare_presentation_versions as _compare_versions
)
from .shape_editing_tools import (
    edit_slide_text_content as _edit_text,
    apply_shape_formatting as _apply_formatting,
    manage_slide_shapes as _manage_shapes
)

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# Core Analysis Tools
# =============================================================================

def extract_powerpoint_metadata(
    presentation_path: str,
    include_slide_content: bool = True,
    include_master_slides: bool = False,
    include_layouts: bool = False,
    output_format: str = "json"
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
    with PowerPointMetadataExtractor(presentation_path) as extractor:
        return extractor.analyze_slide_content(
            slide_numbers=slide_numbers,
            extract_text_only=extract_text_only
        )

def validate_powerpoint_file(presentation_path: str) -> Dict[str, Any]:
    """
    Validate a PowerPoint file and check for common issues.

    Args:
        presentation_path: Path to the PowerPoint file

    Returns:
        Dictionary containing validation results
    """
    with PowerPointMetadataExtractor(presentation_path) as extractor:
        return extractor.validate_file()

# =============================================================================
# Slide Management Tools
# =============================================================================

def manage_presentation_slides(
    presentation_path: str,
    dsl_operations: str
) -> Dict[str, Any]:
    """
    Manage PowerPoint slides using DSL commands.

    Args:
        presentation_path: Path to the PowerPoint file
        dsl_operations: Slide management operations in DSL format (e.g., "add_slide: position=1, layout=Title")

    Returns:
        Dictionary containing operation results
    """
    return _manage_slides(presentation_path, dsl_operations)

def bulk_slide_operations(
    presentation_path: str,
    operations: List[str],
    validate_before_execute: bool = True,
    stop_on_error: bool = True
) -> Dict[str, Any]:
    """
    Execute multiple slide operations with validation.

    Args:
        presentation_path: Path to the PowerPoint file
        operations: List of DSL operations to execute
        validate_before_execute: Validate operations before execution
        stop_on_error: Stop execution on first error

    Returns:
        Dictionary containing operation results
    """
    return _bulk_operations(
        presentation_path,
        operations,
        validate_before_execute,
        stop_on_error
    )

# =============================================================================
# Visual & Multimodal Tools
# =============================================================================

def capture_slide_images(
    presentation_path: str,
    slide_numbers: List[int],
    image_width: int = 1024,
    image_height: int = 768,
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Capture PowerPoint slides as base64-encoded PNG images.

    Args:
        presentation_path: Path to the PowerPoint file
        slide_numbers: Slide numbers to capture (1-based)
        image_width: Width of captured images in pixels
        image_height: Height of captured images in pixels
        include_metadata: Include capture metadata in response

    Returns:
        Dictionary containing captured slide images and metadata
    """
    return capture_powerpoint_slides(
        presentation_path,
        slide_numbers,
        image_width,
        image_height,
        include_metadata
    )

def compare_presentation_versions(
    original_path: str,
    modified_path: str,
    include_visual_comparison: bool = True,
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
    return _compare_versions(
        original_path,
        modified_path,
        include_visual_comparison,
        max_slides_to_compare
    )

# =============================================================================
# Content Editing Tools
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
    return _edit_text(
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
    return _apply_formatting(
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
        shape_operations: List of shape operations

    Returns:
        Dictionary containing operation results
    """
    return _manage_shapes(
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
    return get_slide_capture_capabilities()
