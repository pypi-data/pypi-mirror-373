"""
PowerPoint tools wrapped as LangChain tools with decorators.

This module provides all PowerPoint tools as LangChain-compatible tools that can be used
with LangChain agents and chains. Each tool is decorated with @tool and includes
detailed descriptions and type hints.

Example Usage:
    from volute_ppt.langchain_tools import (
        get_powerpoint_metadata,
        capture_powerpoint_images,
        edit_slide_text
    )
    
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_openai import ChatOpenAI
    
    tools = [
        get_powerpoint_metadata,
        capture_powerpoint_images,
        edit_slide_text
    ]
    
    llm = ChatOpenAI()
    agent = create_openai_tools_agent(llm, tools)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
"""

from typing import Dict, List, Any, Optional, Union
from langchain.tools import tool

# =============================================================================
# Core Analysis Tools
# =============================================================================

@tool
def get_powerpoint_metadata(
    presentation_path: str,
    include_slide_content: bool = True,
    include_master_slides: bool = False,
    include_layouts: bool = False,
    output_format: str = "json"
) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from a PowerPoint presentation.
    
    This tool analyzes PowerPoint files and extracts detailed information including:
    - Core properties (title, author, creation date, etc.)
    - Slide dimensions and layout information
    - All shapes on each slide with position, size, and formatting
    - Text content and formatting (fonts, colors, alignment)
    - Images with crop information
    - Tables with cell data
    - Fill, line, and shadow formatting
    - Shape-specific properties (autoshapes, groups, etc.)
    - Slide notes and comments
    
    Unless the user specifically asks for formatting details, limit responses to content and objects.
    
    Args:
        presentation_path: Path to the PowerPoint file
        include_slide_content: Include detailed slide content analysis
        include_master_slides: Include slide master information
        include_layouts: Include slide layout information
        output_format: Output format ('json' or 'summary')
    
    Returns:
        Dictionary containing complete presentation metadata
    """
    from .toolkit import extract_powerpoint_metadata
    return extract_powerpoint_metadata(
        presentation_path,
        include_slide_content,
        include_master_slides,
        include_layouts,
        output_format
    )

@tool
def get_slide_content(
    presentation_path: str,
    slide_numbers: Optional[List[int]] = None,
    extract_text_only: bool = False
) -> Dict[str, Any]:
    """
    Analyze content of specific slides in a PowerPoint presentation.
    
    This tool provides focused content analysis of PowerPoint slides, extracting:
    - Text content from all text boxes and shapes
    - Slide titles and bullet points
    - Table data and content
    - Image descriptions and alt text
    - Shape types and basic properties
    
    Keep responses natural and focused on content unless formatting is specifically requested.
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_numbers: Specific slide numbers to analyze (1-based). If None, analyzes all slides
        extract_text_only: Extract only text content, skip formatting details
    
    Returns:
        Dictionary containing slide content analysis
    """
    from .toolkit import analyze_powerpoint_content
    return analyze_powerpoint_content(
        presentation_path,
        slide_numbers,
        extract_text_only
    )

@tool
def validate_powerpoint(presentation_path: str) -> Dict[str, Any]:
    """
    Validate a PowerPoint file and check for common issues.
    
    This tool performs comprehensive validation including:
    - File format and compatibility checks
    - File corruption detection
    - Structural integrity verification 
    - Slide count validation
    - Basic content checks
    
    Args:
        presentation_path: Path to the PowerPoint file to validate
    
    Returns:
        Dictionary containing validation results with issues and warnings
    """
    from .toolkit import validate_powerpoint_file
    return validate_powerpoint_file(presentation_path)

# =============================================================================
# Slide Management Tools
# =============================================================================

@tool
def manage_slides(
    presentation_path: str,
    dsl_operations: str
) -> Dict[str, Any]:
    """
    Manage PowerPoint slides using a domain-specific language (DSL).
    
    This tool executes slide management operations using a simple DSL:
    - add_slide: position=1, layout="Title Slide"
    - delete_slide: slide_number=3
    - move_slide: from=1, to=5 
    - duplicate_slide: source=2, position=end
    
    Operations can be combined with pipes:
    "add_slide: position=1 | move_slide: from=3, to=5"
    
    Args:
        presentation_path: Path to the PowerPoint file
        dsl_operations: Slide operations in DSL format
    
    Returns:
        Dictionary containing operation results
    """
    from .toolkit import manage_presentation_slides
    return manage_presentation_slides(
        presentation_path,
        dsl_operations
    )

@tool
def execute_bulk_operations(
    presentation_path: str,
    operations: List[str],
    validate_before_execute: bool = True,
    stop_on_error: bool = True
) -> Dict[str, Any]:
    """
    Execute multiple slide operations with validation and error handling.
    
    This tool provides transaction-like behavior for slide operations:
    - Pre-validates all operations
    - Executes operations in sequence
    - Optionally stops on first error
    - Provides detailed operation tracking
    
    Args:
        presentation_path: Path to the PowerPoint file
        operations: List of DSL operations to execute
        validate_before_execute: Validate operations before execution
        stop_on_error: Stop execution on first error
    
    Returns:
        Dictionary containing operation results
    """
    from .toolkit import bulk_slide_operations
    return bulk_slide_operations(
        presentation_path,
        operations,
        validate_before_execute,
        stop_on_error
    )

# =============================================================================
# Visual & Multimodal Tools
# =============================================================================

@tool
def capture_powerpoint_images(
    presentation_path: str,
    slide_numbers: List[int],
    image_width: int = 1024,
    image_height: int = 768,
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Capture PowerPoint slides as base64-encoded PNG images for multimodal AI analysis.
    
    This tool enables vision-based analysis of slides by:
    - Capturing high-quality slide images
    - Converting to base64 PNG format
    - Supporting configurable resolutions
    - Including capture metadata
    
    Perfect for vision-capable AI models that need to analyze slide visuals!
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_numbers: Slide numbers to capture (1-based)
        image_width: Width of captured images in pixels
        image_height: Height of captured images in pixels
        include_metadata: Include capture metadata
    
    Returns:
        Dictionary containing slide images and metadata
    """
    from .toolkit import capture_slide_images
    return capture_slide_images(
        presentation_path,
        slide_numbers,
        image_width,
        image_height,
        include_metadata
    )

@tool
def compare_presentations(
    original_path: str,
    modified_path: str,
    include_visual_comparison: bool = True,
    max_slides_to_compare: int = 10
) -> Dict[str, Any]:
    """
    Compare two versions of a PowerPoint presentation and identify changes.
    
    This tool analyzes differences including:
    - Slide count changes
    - Content modifications
    - Formatting changes
    - Visual differences (optional)
    - Metadata changes
    
    Perfect for version control and change tracking!
    
    Args:
        original_path: Path to original presentation
        modified_path: Path to modified presentation
        include_visual_comparison: Include visual slide comparisons
        max_slides_to_compare: Maximum slides to compare
    
    Returns:
        Dictionary containing comparison results
    """
    from .toolkit import compare_presentation_versions
    return compare_presentation_versions(
        original_path,
        modified_path,
        include_visual_comparison,
        max_slides_to_compare
    )

# =============================================================================
# Content Editing Tools
# =============================================================================

@tool
def edit_slide_text(
    presentation_path: str,
    slide_number: int,
    text_updates: Dict[str, str],
    convert_bullets: bool = True,
    preserve_formatting: bool = True,
    auto_resize: bool = True
) -> Dict[str, Any]:
    """
    Edit text content with intelligent bullet conversion and formatting preservation.
    
    This tool provides smart text editing features:
    - Converts text bullets to native PowerPoint bullets
    - Preserves existing text formatting
    - Supports multi-level bullet hierarchies
    - Automatically resizes shapes to fit content
    - Handles newlines correctly
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_number: Slide number to edit (1-based)
        text_updates: Map of shape names to new text content
        convert_bullets: Convert text bullets to native PowerPoint bullets
        preserve_formatting: Preserve existing text formatting
        auto_resize: Automatically resize shapes to fit content
    
    Returns:
        Dictionary containing edit results
    """
    from .toolkit import edit_slide_text_content
    return edit_slide_text_content(
        presentation_path,
        slide_number,
        text_updates,
        convert_bullets,
        preserve_formatting,
        auto_resize
    )

@tool
def format_shapes(
    presentation_path: str,
    slide_number: int,
    shape_formatting: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Apply comprehensive formatting to PowerPoint shapes.
    
    This tool supports extensive shape formatting:
    - Font properties (name, size, color, etc.)
    - Text alignment and spacing
    - Shape fills and lines
    - Position and size
    - Visual effects
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_number: Slide number to edit (1-based)
        shape_formatting: Map of shape names to formatting properties
    
    Returns:
        Dictionary containing formatting results
    """
    from .toolkit import apply_shape_formatting
    return apply_shape_formatting(
        presentation_path,
        slide_number,
        shape_formatting
    )

@tool
def manage_shapes(
    presentation_path: str,
    slide_number: int,
    shape_operations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Add, delete, copy, transform shapes on PowerPoint slides.
    
    This tool provides complete shape management:
    - Add new shapes with properties
    - Delete existing shapes
    - Copy shapes between positions
    - Transform shape properties
    - Group/ungroup shapes
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_number: Slide number to edit (1-based)
        shape_operations: List of shape operations to perform
    
    Returns:
        Dictionary containing operation results
    """
    from .toolkit import manage_slide_shapes
    return manage_slide_shapes(
        presentation_path,
        slide_number,
        shape_operations
    )

# =============================================================================
# Utility Tools
# =============================================================================

@tool
def get_capabilities() -> Dict[str, Any]:
    """
    Get information about PowerPoint capabilities and requirements.
    
    This tool reports system capabilities including:
    - COM automation availability
    - PowerPoint installation status
    - Supported file formats
    - Image capture capabilities
    - System requirements
    
    Returns:
        Dictionary containing system capabilities
    """
    from .toolkit import get_system_capabilities
    return get_system_capabilities()

# Export all tools
__all__ = [
    # Core Analysis
    'get_powerpoint_metadata',
    'get_slide_content',
    'validate_powerpoint',
    
    # Slide Management
    'manage_slides',
    'execute_bulk_operations',
    
    # Visual & Multimodal
    'capture_powerpoint_images',
    'compare_presentations',
    
    # Content Editing
    'edit_slide_text',
    'format_shapes',
    'manage_shapes',
    
    # Utilities
    'get_capabilities'
]
