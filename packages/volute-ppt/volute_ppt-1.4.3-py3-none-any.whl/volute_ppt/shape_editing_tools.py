"""
PowerPoint Shape Editing Tools Module

This module provides sophisticated shape editing capabilities that build upon
the existing slide_executor infrastructure. It includes advanced operations
for manipulating text, shapes, tables, charts, and other slide content.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Import existing infrastructure
from .powerpoint.slide_executor import PowerPointSlideExecutor
from .slide_capture_tools import capture_single_slide_after_operation
from .smart_text_processor import smart_processor, apply_smart_text_to_shape

# Configure logging
logger = logging.getLogger(__name__)

# Check for win32com availability
WIN32COM_AVAILABLE = False
try:
    import win32com.client
    import pythoncom
    WIN32COM_AVAILABLE = True
    logger.info("win32com available for shape editing operations")
except ImportError as e:
    logger.warning(f"win32com not available: {e}")


class ShapeEditResult(BaseModel):
    """Model for shape editing operation results."""
    success: bool = Field(description="Whether the operation was successful")
    message: str = Field(description="Status message")
    shapes_modified: int = Field(default=0, description="Number of shapes modified")
    operations_performed: List[str] = Field(default_factory=list, description="List of operations performed")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Operation data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    slide_image: Optional[str] = Field(default=None, description="Base64-encoded slide image for visual verification")
    visual_verification: Optional[Dict[str, Any]] = Field(default=None, description="Visual verification metadata")


class ShapeProperties(BaseModel):
    """Model for comprehensive shape properties."""
    text: Optional[str] = Field(default=None, description="Text content")
    font_name: Optional[str] = Field(default=None, description="Font family name")
    font_size: Optional[float] = Field(default=None, description="Font size in points")
    font_color: Optional[str] = Field(default=None, description="Font color as hex (#RRGGBB)")
    bold: Optional[bool] = Field(default=None, description="Bold formatting")
    italic: Optional[bool] = Field(default=None, description="Italic formatting")
    underline: Optional[bool] = Field(default=None, description="Underline formatting")
    
    # Position and size
    left: Optional[float] = Field(default=None, description="Left position in points")
    top: Optional[float] = Field(default=None, description="Top position in points")
    width: Optional[float] = Field(default=None, description="Width in points")
    height: Optional[float] = Field(default=None, description="Height in points")
    
    # Shape appearance
    fill_color: Optional[str] = Field(default=None, description="Fill color as hex (#RRGGBB)")
    line_color: Optional[str] = Field(default=None, description="Outline color as hex (#RRGGBB)")
    line_width: Optional[float] = Field(default=None, description="Outline width in points")
    
    # Alignment
    text_align: Optional[str] = Field(default=None, description="Text alignment: left, center, right, justify")
    vertical_align: Optional[str] = Field(default=None, description="Vertical alignment: top, middle, bottom")


def register_shape_editing_tools(mcp: FastMCP) -> None:
    """
    Register shape editing tools with the FastMCP server.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    
    @mcp.tool()
    def edit_slide_text_content(
        presentation_path: str = Field(description="Path to the PowerPoint file (.pptx, .ppt)"),
        slide_number: int = Field(description="Slide number to edit (1-based)"),
        text_updates: Dict[str, str] = Field(description="Dictionary of shape names to new text content"),
        convert_bullets: bool = Field(default=True, description="Convert text bullets (•, -, etc.) to native PowerPoint bullets"),
        preserve_formatting: bool = Field(default=True, description="Preserve existing text formatting"),
        auto_resize: bool = Field(default=True, description="Auto-resize shapes to fit new text"),
        capture_result: bool = Field(default=True, description="Capture slide image after text updates for visual verification")
    ) -> ShapeEditResult:
        """
        Edit text content in specific shapes on a PowerPoint slide with intelligent processing.
        
        This tool provides advanced text editing capabilities:
        - Update text in multiple shapes simultaneously
        - Intelligent bullet detection and conversion to native PowerPoint bullets
        - Enhanced newline handling (\n → line breaks, \\n → literal \n)
        - Multi-level bullet indentation support
        - Preserve existing formatting and styles
        - Auto-resize shapes to accommodate new content
        
        Perfect for LLM-generated content with bullets, ensuring clean PowerPoint
        formatting without duplicate bullets or formatting issues.
        """
        try:
            # Validate inputs
            if not os.path.exists(presentation_path):
                return ShapeEditResult(
                    success=False,
                    message="File not found",
                    error=f"PowerPoint file not found: {presentation_path}"
                )
            
            if not WIN32COM_AVAILABLE:
                return ShapeEditResult(
                    success=False,
                    message="COM automation not available",
                    error="win32com library is required for smart text editing"
                )
            
            if not text_updates:
                return ShapeEditResult(
                    success=False,
                    message="No text updates provided",
                    error="text_updates dictionary is empty"
                )
            
            operations_performed = []
            shapes_modified = 0
            smart_operations = []
            
            # Use slide executor to perform text edits
            with PowerPointSlideExecutor() as executor:
                if not executor.open_presentation(presentation_path):
                    return ShapeEditResult(
                        success=False,
                        message="Cannot open presentation",
                        error="Failed to open PowerPoint presentation"
                    )
                
                # Validate slide number
                total_slides = executor.get_slide_count()
                if slide_number < 1 or slide_number > total_slides:
                    return ShapeEditResult(
                        success=False,
                        message="Invalid slide number",
                        error=f"Slide {slide_number} not found. Presentation has {total_slides} slides"
                    )
                
                # Get the slide
                slide = executor.presentation.Slides(slide_number)
                
                # Update text in each specified shape with smart processing
                for shape_name, new_text in text_updates.items():
                    try:
                        # Find the shape by name
                        target_shape = None
                        for shape in slide.Shapes:
                            if shape.Name == shape_name:
                                target_shape = shape
                                break
                        
                        if not target_shape:
                            logger.warning(f"Shape '{shape_name}' not found on slide {slide_number}")
                            operations_performed.append(f"Shape '{shape_name}' not found")
                            continue
                        
                        # Check if shape has text frame
                        if hasattr(target_shape, 'TextFrame') and target_shape.TextFrame:
                            
                            if convert_bullets:
                                # Use smart text processing with bullet conversion
                                smart_result = apply_smart_text_to_shape(
                                    target_shape, 
                                    new_text, 
                                    preserve_formatting=preserve_formatting
                                )
                                
                                if smart_result['success']:
                                    shapes_modified += 1
                                    
                                    # Build operation description
                                    operations_list = smart_result.get('operations', [])
                                    bullets_detected = smart_result.get('bullets_detected', 0)
                                    bullet_types = smart_result.get('bullet_types', [])
                                    
                                    operation_desc = f"Smart updated '{shape_name}' ({len(new_text)} chars)"
                                    if bullets_detected > 0:
                                        operation_desc += f", converted {bullets_detected} bullets ({', '.join(bullet_types)})"
                                    
                                    operations_performed.append(operation_desc)
                                    smart_operations.extend(operations_list)
                                    
                                    logger.info(f"Smart updated shape '{shape_name}' with {bullets_detected} bullets converted")
                                else:
                                    # Fall back to regular text processing
                                    processed_text = _process_text_with_newlines(new_text)
                                    target_shape.TextFrame.TextRange.Text = processed_text
                                    shapes_modified += 1
                                    operations_performed.append(f"Updated '{shape_name}' (smart processing failed: {smart_result.get('error', 'unknown')})")
                            else:
                                # Regular text processing without bullet conversion
                                processed_text = _process_text_with_newlines(new_text)
                                target_shape.TextFrame.TextRange.Text = processed_text
                                shapes_modified += 1
                                operations_performed.append(f"Updated '{shape_name}' with standard processing")
                            
                            # Auto-resize if requested
                            if auto_resize:
                                try:
                                    text_frame = target_shape.TextFrame
                                    text_frame.AutoSize = 1  # ppAutoSizeShapeToFitText
                                except:
                                    pass  # Auto-resize not supported for this shape
                        
                        else:
                            logger.warning(f"Shape '{shape_name}' does not support text on slide {slide_number}")
                            operations_performed.append(f"Shape '{shape_name}' does not support text")
                    
                    except Exception as e:
                        logger.error(f"Error updating shape '{shape_name}': {e}")
                        operations_performed.append(f"Failed to update '{shape_name}': {str(e)}")
                
                # Save the presentation
                if not executor.save_presentation():
                    logger.warning("Failed to save presentation after text updates")
            
            success = shapes_modified > 0
            message = f"Successfully updated {shapes_modified} shapes" if success else "No shapes were updated"
            
            # Add smart operations summary to regular operations
            if smart_operations:
                operations_performed.append(f"Smart operations: {', '.join(set(smart_operations))}")
            
            # Capture slide image for visual verification if requested and operations were successful
            slide_image = None
            visual_verification = None
            
            if capture_result and success:
                try:
                    slide_image = capture_single_slide_after_operation(
                        presentation_path, 
                        slide_number
                    )
                    
                    if slide_image:
                        visual_verification = {
                            "captured": True,
                            "slide_number": slide_number,
                            "text_updates_count": shapes_modified,
                            "smart_processing_used": convert_bullets,
                            "capture_time": datetime.now().isoformat(),
                            "image_format": "PNG",
                            "encoding": "base64",
                            "purpose": "multimodal_verification",
                            "operation_type": "smart_text_content_edit"
                        }
                        logger.info(f"Captured slide {slide_number} after text updates")
                    else:
                        visual_verification = {
                            "captured": False,
                            "reason": "Slide capture failed or not available"
                        }
                        logger.warning(f"Failed to capture slide {slide_number} after text updates")
                        
                except Exception as e:
                    logger.error(f"Error during slide capture after text updates: {e}")
                    visual_verification = {
                        "captured": False,
                        "reason": f"Capture error: {str(e)}"
                    }
            
            return ShapeEditResult(
                success=success,
                message=message,
                shapes_modified=shapes_modified,
                operations_performed=operations_performed,
                data={"smart_operations": smart_operations} if smart_operations else None,
                slide_image=slide_image,
                visual_verification=visual_verification
            )
            
        except Exception as e:
            logger.exception(f"Error in edit_slide_text_content: {str(e)}")
            return ShapeEditResult(
                success=False,
                message="Text editing failed",
                error=f"Failed to edit slide text: {str(e)}"
            )
    
    
    @mcp.tool()
    def apply_shape_formatting(
        presentation_path: str = Field(description="Path to the PowerPoint file (.pptx, .ppt)"),
        slide_number: int = Field(description="Slide number to edit (1-based)"),
        shape_formatting: Dict[str, ShapeProperties] = Field(description="Dictionary mapping shape names to their formatting properties"),
        create_backup: bool = Field(default=True, description="Create backup of original file before editing"),
        capture_result: bool = Field(default=True, description="Capture slide image after formatting for visual verification")
    ) -> ShapeEditResult:
        """
        Apply comprehensive formatting to shapes on a PowerPoint slide.
        
        This tool provides advanced shape formatting capabilities:
        - Text formatting (font, size, color, alignment)
        - Position and size adjustments
        - Fill and outline styling
        - Bulk formatting operations
        - Safe editing with backup protection
        
        Perfect for applying consistent styling, branding guidelines,
        or making precise layout adjustments.
        """
        try:
            # Validate inputs
            if not os.path.exists(presentation_path):
                return ShapeEditResult(
                    success=False,
                    message="File not found",
                    error=f"PowerPoint file not found: {presentation_path}"
                )
            
            if not WIN32COM_AVAILABLE:
                return ShapeEditResult(
                    success=False,
                    message="COM automation not available",
                    error="win32com library is required for shape formatting"
                )
            
            if not shape_formatting:
                return ShapeEditResult(
                    success=False,
                    message="No formatting specified",
                    error="shape_formatting dictionary is empty"
                )
            
            # Create backup if requested
            if create_backup:
                try:
                    from shutil import copy2
                    backup_path = presentation_path + ".backup"
                    copy2(presentation_path, backup_path)
                    logger.info(f"Created backup at: {backup_path}")
                except Exception as e:
                    logger.warning(f"Could not create backup: {e}")
            
            operations_performed = []
            shapes_modified = 0
            
            # Use slide executor to perform formatting
            with PowerPointSlideExecutor() as executor:
                if not executor.open_presentation(presentation_path):
                    return ShapeEditResult(
                        success=False,
                        message="Cannot open presentation",
                        error="Failed to open PowerPoint presentation"
                    )
                
                # Validate slide number
                total_slides = executor.get_slide_count()
                if slide_number < 1 or slide_number > total_slides:
                    return ShapeEditResult(
                        success=False,
                        message="Invalid slide number",
                        error=f"Slide {slide_number} not found. Presentation has {total_slides} slides"
                    )
                
                # Get the slide
                slide = executor.presentation.Slides(slide_number)
                
                # Apply formatting to each specified shape
                for shape_name, properties in shape_formatting.items():
                    try:
                        # Find the shape by name
                        target_shape = None
                        for shape in slide.Shapes:
                            if shape.Name == shape_name:
                                target_shape = shape
                                break
                        
                        if not target_shape:
                            operations_performed.append(f"Shape '{shape_name}' not found on slide")
                            logger.warning(f"Shape '{shape_name}' not found on slide {slide_number}")
                            continue
                        
                        current_operations = []
                        
                        # Apply position and size properties
                        if properties.left is not None:
                            target_shape.Left = properties.left
                            current_operations.append("position-left")
                        
                        if properties.top is not None:
                            target_shape.Top = properties.top
                            current_operations.append("position-top")
                        
                        if properties.width is not None:
                            target_shape.Width = properties.width
                            current_operations.append("size-width")
                        
                        if properties.height is not None:
                            target_shape.Height = properties.height
                            current_operations.append("size-height")
                        
                        # Apply fill color
                        if properties.fill_color is not None:
                            try:
                                if properties.fill_color.lower() == "none":
                                    target_shape.Fill.Visible = False
                                else:
                                    # Convert hex color to RGB
                                    color_hex = properties.fill_color.replace("#", "")
                                    r = int(color_hex[0:2], 16)
                                    g = int(color_hex[2:4], 16)
                                    b = int(color_hex[4:6], 16)
                                    rgb_value = r + (g * 256) + (b * 256 * 256)
                                    
                                    target_shape.Fill.Visible = True
                                    target_shape.Fill.ForeColor.RGB = rgb_value
                                current_operations.append("fill-color")
                            except Exception as e:
                                logger.warning(f"Could not apply fill color to '{shape_name}': {e}")
                        
                        # Apply line/outline properties
                        if properties.line_color is not None:
                            try:
                                if properties.line_color.lower() == "none":
                                    target_shape.Line.Visible = False
                                else:
                                    # Convert hex color to RGB
                                    color_hex = properties.line_color.replace("#", "")
                                    r = int(color_hex[0:2], 16)
                                    g = int(color_hex[2:4], 16)
                                    b = int(color_hex[4:6], 16)
                                    rgb_value = r + (g * 256) + (b * 256 * 256)
                                    
                                    target_shape.Line.Visible = True
                                    target_shape.Line.ForeColor.RGB = rgb_value
                                current_operations.append("line-color")
                            except Exception as e:
                                logger.warning(f"Could not apply line color to '{shape_name}': {e}")
                        
                        if properties.line_width is not None:
                            try:
                                target_shape.Line.Weight = properties.line_width
                                current_operations.append("line-width")
                            except Exception as e:
                                logger.warning(f"Could not apply line width to '{shape_name}': {e}")
                        
                        # Apply text formatting if shape has text
                        if hasattr(target_shape, 'TextFrame') and target_shape.TextFrame:
                            text_range = target_shape.TextFrame.TextRange
                            
                            # Update text content with proper newline handling
                            if properties.text is not None:
                                processed_text = _process_text_with_newlines(properties.text)
                                text_range.Text = processed_text
                                current_operations.append("text-content")
                            
                            # Apply font formatting
                            if properties.font_name is not None:
                                text_range.Font.Name = properties.font_name
                                current_operations.append("font-name")
                            
                            if properties.font_size is not None:
                                text_range.Font.Size = properties.font_size
                                current_operations.append("font-size")
                            
                            if properties.font_color is not None:
                                try:
                                    # Convert hex color to RGB
                                    color_hex = properties.font_color.replace("#", "")
                                    r = int(color_hex[0:2], 16)
                                    g = int(color_hex[2:4], 16)
                                    b = int(color_hex[4:6], 16)
                                    rgb_value = r + (g * 256) + (b * 256 * 256)
                                    
                                    text_range.Font.Color.RGB = rgb_value
                                    current_operations.append("font-color")
                                except Exception as e:
                                    logger.warning(f"Could not apply font color to '{shape_name}': {e}")
                            
                            if properties.bold is not None:
                                text_range.Font.Bold = properties.bold
                                current_operations.append("bold")
                            
                            if properties.italic is not None:
                                text_range.Font.Italic = properties.italic
                                current_operations.append("italic")
                            
                            if properties.underline is not None:
                                text_range.Font.Underline = properties.underline
                                current_operations.append("underline")
                            
                            # Apply text alignment
                            if properties.text_align is not None:
                                alignment_map = {
                                    "left": 1,      # ppAlignLeft
                                    "center": 2,    # ppAlignCenter
                                    "right": 3,     # ppAlignRight
                                    "justify": 4    # ppAlignJustify
                                }
                                if properties.text_align in alignment_map:
                                    text_range.ParagraphFormat.Alignment = alignment_map[properties.text_align]
                                    current_operations.append("text-align")
                            
                            # Apply vertical alignment
                            if properties.vertical_align is not None:
                                valign_map = {
                                    "top": 1,       # msoAnchorTop
                                    "middle": 2,    # msoAnchorMiddle
                                    "bottom": 3     # msoAnchorBottom
                                }
                                if properties.vertical_align in valign_map:
                                    target_shape.TextFrame.VerticalAnchor = valign_map[properties.vertical_align]
                                    current_operations.append("vertical-align")
                        
                        if current_operations:
                            shapes_modified += 1
                            operations_performed.append(f"Applied to '{shape_name}': {', '.join(current_operations)}")
                            logger.info(f"Applied {len(current_operations)} formatting operations to shape '{shape_name}'")
                        
                    except Exception as e:
                        logger.error(f"Error formatting shape '{shape_name}': {e}")
                        operations_performed.append(f"Failed to format '{shape_name}': {str(e)}")
                
                # Save the presentation
                if not executor.save_presentation():
                    logger.warning("Failed to save presentation after formatting")
            
            success = shapes_modified > 0
            message = f"Successfully formatted {shapes_modified} shapes" if success else "No shapes were formatted"
            
            # Capture slide image for visual verification if requested and operations were successful
            slide_image = None
            visual_verification = None
            
            if capture_result and success:
                try:
                    slide_image = capture_single_slide_after_operation(
                        presentation_path, 
                        slide_number
                    )
                    
                    if slide_image:
                        visual_verification = {
                            "captured": True,
                            "slide_number": slide_number,
                            "formatting_updates_count": shapes_modified,
                            "capture_time": datetime.now().isoformat(),
                            "image_format": "PNG",
                            "encoding": "base64",
                            "purpose": "multimodal_verification",
                            "operation_type": "shape_formatting"
                        }
                        logger.info(f"Captured slide {slide_number} after shape formatting")
                    else:
                        visual_verification = {
                            "captured": False,
                            "reason": "Slide capture failed or not available"
                        }
                        logger.warning(f"Failed to capture slide {slide_number} after formatting")
                        
                except Exception as e:
                    logger.error(f"Error during slide capture after formatting: {e}")
                    visual_verification = {
                        "captured": False,
                        "reason": f"Capture error: {str(e)}"
                    }
            
            return ShapeEditResult(
                success=success,
                message=message,
                shapes_modified=shapes_modified,
                operations_performed=operations_performed,
                slide_image=slide_image,
                visual_verification=visual_verification
            )
            
        except Exception as e:
            logger.exception(f"Error in apply_shape_formatting: {str(e)}")
            return ShapeEditResult(
                success=False,
                message="Shape formatting failed",
                error=f"Failed to apply shape formatting: {str(e)}"
            )
    
    @mcp.tool()
    def manage_slide_shapes(
        presentation_path: str = Field(description="Path to the PowerPoint file (.pptx, .ppt)"),
        slide_number: int = Field(description="Slide number to edit (1-based)"),
        shape_operations: List[Dict[str, Any]] = Field(description="List of shape operations to perform"),
        validate_operations: bool = Field(default=True, description="Validate operations before executing"),
        capture_result: bool = Field(default=True, description="Capture slide image after operations for visual verification")
    ) -> ShapeEditResult:
        """
        Perform comprehensive shape management operations on a PowerPoint slide.
        
        This tool provides advanced shape manipulation capabilities:
        - Add new shapes with specific properties
        - Delete existing shapes by name or criteria
        - Copy shapes within or between slides
        - Reorder shapes (z-order management)
        - Group and ungroup shapes
        - Apply transformations (rotate, flip, scale)
        
        Operations are specified as a list of operation dictionaries with the following format:
        {
            "operation": "add|delete|copy|move|group|ungroup|transform",
            "shape_name": "target shape name",
            "properties": {...},  // operation-specific properties
            "source_slide": 1,    // for copy operations
            "target_position": {...}  // for positioning
        }
        """
        try:
            # Validate inputs
            if not os.path.exists(presentation_path):
                return ShapeEditResult(
                    success=False,
                    message="File not found",
                    error=f"PowerPoint file not found: {presentation_path}"
                )
            
            if not WIN32COM_AVAILABLE:
                return ShapeEditResult(
                    success=False,
                    message="COM automation not available",
                    error="win32com library is required for shape management"
                )
            
            if not shape_operations:
                return ShapeEditResult(
                    success=False,
                    message="No operations specified",
                    error="shape_operations list is empty"
                )
            
            operations_performed = []
            shapes_modified = 0
            
            # Validate operations if requested
            if validate_operations:
                valid_operations = ["add", "delete", "copy", "move", "group", "ungroup", "transform"]
                for i, op in enumerate(shape_operations):
                    if not isinstance(op, dict):
                        return ShapeEditResult(
                            success=False,
                            message="Invalid operation format",
                            error=f"Operation {i} is not a dictionary"
                        )
                    
                    if "operation" not in op:
                        return ShapeEditResult(
                            success=False,
                            message="Missing operation type",
                            error=f"Operation {i} missing 'operation' key"
                        )
                    
                    if op["operation"] not in valid_operations:
                        return ShapeEditResult(
                            success=False,
                            message="Invalid operation type",
                            error=f"Operation {i}: '{op['operation']}' not in {valid_operations}"
                        )
            
            # Use slide executor to perform shape operations
            with PowerPointSlideExecutor() as executor:
                if not executor.open_presentation(presentation_path):
                    return ShapeEditResult(
                        success=False,
                        message="Cannot open presentation",
                        error="Failed to open PowerPoint presentation"
                    )
                
                # Validate slide number
                total_slides = executor.get_slide_count()
                if slide_number < 1 or slide_number > total_slides:
                    return ShapeEditResult(
                        success=False,
                        message="Invalid slide number",
                        error=f"Slide {slide_number} not found. Presentation has {total_slides} slides"
                    )
                
                # Get the slide
                slide = executor.presentation.Slides(slide_number)
                
                # Execute each operation
                for i, operation in enumerate(shape_operations):
                    try:
                        op_type = operation["operation"]
                        shape_name = operation.get("shape_name")
                        properties = operation.get("properties", {})
                        
                        if op_type == "delete":
                            # Delete shape by name
                            if not shape_name:
                                operations_performed.append(f"Operation {i}: Missing shape_name for delete")
                                continue
                            
                            target_shape = None
                            for shape in slide.Shapes:
                                if shape.Name == shape_name:
                                    target_shape = shape
                                    break
                            
                            if target_shape:
                                target_shape.Delete()
                                shapes_modified += 1
                                operations_performed.append(f"Deleted shape '{shape_name}'")
                                logger.info(f"Deleted shape '{shape_name}' from slide {slide_number}")
                            else:
                                operations_performed.append(f"Shape '{shape_name}' not found for deletion")
                        
                        elif op_type == "add":
                            # Add new shape with improved error handling
                            shape_type = properties.get("type", "rectangle")
                            left = float(properties.get("left", 100))
                            top = float(properties.get("top", 100))
                            width = float(properties.get("width", 100))
                            height = float(properties.get("height", 50))
                            
                            # Validate dimensions
                            if width <= 0 or height <= 0:
                                operations_performed.append(f"Operation {i}: Invalid dimensions (width={width}, height={height})")
                                continue
                            
                            # Validate position (must be positive)
                            if left < 0 or top < 0:
                                operations_performed.append(f"Operation {i}: Invalid position (left={left}, top={top})")
                                continue
                            
                            try:
                                # Shape type mapping with more options
                                shape_type_map = {
                                    "rectangle": 1,      # msoShapeRectangle
                                    "oval": 9,          # msoShapeOval
                                    "circle": 9,        # msoShapeOval (alias)
                                    "line": 20,         # msoShapeLine
                                    "textbox": "textbox", # Special handling
                                    "rounded_rectangle": 5, # msoShapeRoundedRectangle
                                    "triangle": 7,      # msoShapeIsoscelesTriangle
                                    "arrow": 15,        # msoShapeRightArrow
                                    "diamond": 4,       # msoShapeDiamond
                                    "star": 12          # msoShape5pointStar
                                }
                                
                                if shape_type == "textbox":
                                    # TextBox requires orientation parameter (1 = horizontal)
                                    new_shape = slide.Shapes.AddTextbox(1, left, top, width, height)
                                elif shape_type == "line":
                                    # Line requires start and end points
                                    end_x = left + width
                                    end_y = top + height
                                    new_shape = slide.Shapes.AddLine(left, top, end_x, end_y)
                                else:
                                    shape_type_id = shape_type_map.get(shape_type, 1)
                                    if shape_type_id == "textbox":
                                        operations_performed.append(f"Operation {i}: Unsupported shape type '{shape_type}'")
                                        continue
                                    new_shape = slide.Shapes.AddShape(shape_type_id, left, top, width, height)
                                
                                # Set shape name if provided
                                if shape_name:
                                    new_shape.Name = shape_name
                                else:
                                    # Generate a unique name
                                    new_shape.Name = f"{shape_type}_{len([s for s in slide.Shapes])}"
                                
                                # Apply text if provided and shape supports text
                                text_content = properties.get("text")
                                if text_content:
                                    try:
                                        if hasattr(new_shape, 'TextFrame') and new_shape.TextFrame:
                                            new_shape.TextFrame.TextRange.Text = text_content
                                        else:
                                            # Try to add text frame for shapes that might support it
                                            if shape_type not in ["line"]:
                                                logger.warning(f"Shape '{shape_type}' may not support text")
                                    except Exception as e:
                                        logger.warning(f"Could not add text to {shape_type} shape: {e}")
                                
                                # Apply basic formatting if provided
                                if "fill_color" in properties:
                                    try:
                                        color_hex = properties["fill_color"].replace("#", "")
                                        r = int(color_hex[0:2], 16)
                                        g = int(color_hex[2:4], 16)
                                        b = int(color_hex[4:6], 16)
                                        rgb_value = r + (g * 256) + (b * 256 * 256)
                                        new_shape.Fill.ForeColor.RGB = rgb_value
                                    except Exception as e:
                                        logger.warning(f"Could not apply fill color: {e}")
                                
                                if "line_color" in properties:
                                    try:
                                        color_hex = properties["line_color"].replace("#", "")
                                        r = int(color_hex[0:2], 16)
                                        g = int(color_hex[2:4], 16)
                                        b = int(color_hex[4:6], 16)
                                        rgb_value = r + (g * 256) + (b * 256 * 256)
                                        new_shape.Line.ForeColor.RGB = rgb_value
                                    except Exception as e:
                                        logger.warning(f"Could not apply line color: {e}")
                                
                                shapes_modified += 1
                                actual_name = shape_name or new_shape.Name
                                operations_performed.append(f"Added {shape_type} shape '{actual_name}' at ({left}, {top}) size {width}x{height}")
                                logger.info(f"Added {shape_type} shape '{actual_name}' to slide {slide_number}")
                                
                            except Exception as e:
                                operations_performed.append(f"Failed to add {shape_type} shape: {str(e)}")
                                logger.error(f"Error adding shape: {e}")
                        
                        elif op_type == "copy":
                            # Copy shape from another slide or within same slide
                            source_slide_num = operation.get("source_slide", slide_number)
                            source_shape_name = operation.get("source_shape_name", shape_name)
                            
                            if not source_shape_name:
                                operations_performed.append(f"Operation {i}: Missing source shape name for copy")
                                continue
                            
                            try:
                                # Get source slide
                                if source_slide_num == slide_number:
                                    source_slide = slide
                                else:
                                    if source_slide_num < 1 or source_slide_num > total_slides:
                                        operations_performed.append(f"Operation {i}: Invalid source slide {source_slide_num}")
                                        continue
                                    source_slide = executor.presentation.Slides(source_slide_num)
                                
                                # Find source shape
                                source_shape = None
                                for shape in source_slide.Shapes:
                                    if shape.Name == source_shape_name:
                                        source_shape = shape
                                        break
                                
                                if source_shape:
                                    # Copy and paste with better error handling
                                    source_shape.Copy()
                                    
                                    # Paste and handle the result properly
                                    try:
                                        slide.Shapes.Paste()
                                        # Get the last added shape (the pasted one)
                                        pasted_shape = slide.Shapes(slide.Shapes.Count)
                                        
                                        # Rename if new name provided
                                        if shape_name and shape_name != source_shape_name:
                                            pasted_shape.Name = shape_name
                                        elif shape_name is None:
                                            # Generate unique name
                                            pasted_shape.Name = f"{source_shape_name}_copy"
                                        
                                        # Apply new position if provided
                                        target_pos = operation.get("target_position", {})
                                        position_changed = False
                                        if target_pos:
                                            if "left" in target_pos:
                                                pasted_shape.Left = float(target_pos["left"])
                                                position_changed = True
                                            if "top" in target_pos:
                                                pasted_shape.Top = float(target_pos["top"])
                                                position_changed = True
                                        else:
                                            # Offset the copy slightly so it's visible
                                            pasted_shape.Left = pasted_shape.Left + 20
                                            pasted_shape.Top = pasted_shape.Top + 20
                                            position_changed = True
                                        
                                        shapes_modified += 1
                                        final_name = shape_name or pasted_shape.Name
                                        position_info = f" at ({pasted_shape.Left}, {pasted_shape.Top})" if position_changed else ""
                                        operations_performed.append(f"Copied shape '{source_shape_name}' to '{final_name}'{position_info}")
                                        logger.info(f"Copied shape from slide {source_slide_num} to slide {slide_number}")
                                        
                                    except Exception as paste_error:
                                        operations_performed.append(f"Failed to paste copied shape: {str(paste_error)}")
                                        logger.error(f"Paste operation failed: {paste_error}")
                                else:
                                    operations_performed.append(f"Source shape '{source_shape_name}' not found on slide {source_slide_num}")
                                    
                            except Exception as e:
                                operations_performed.append(f"Copy operation failed: {str(e)}")
                                logger.error(f"Error during copy operation: {e}")
                        
                        elif op_type == "move":
                            # Move shape to new position or z-order
                            if not shape_name:
                                operations_performed.append(f"Operation {i}: Missing shape_name for move")
                                continue
                            
                            target_shape = None
                            for shape in slide.Shapes:
                                if shape.Name == shape_name:
                                    target_shape = shape
                                    break
                            
                            if target_shape:
                                move_operations = []
                                
                                # Move to new position
                                if "left" in properties:
                                    target_shape.Left = properties["left"]
                                    move_operations.append(f"left={properties['left']}")
                                
                                if "top" in properties:
                                    target_shape.Top = properties["top"]
                                    move_operations.append(f"top={properties['top']}")
                                
                                # Z-order operations
                                if "z_order" in properties:
                                    z_action = properties["z_order"]
                                    if z_action == "bring_to_front":
                                        target_shape.ZOrder(0)  # msoBringToFront
                                        move_operations.append("brought to front")
                                    elif z_action == "send_to_back":
                                        target_shape.ZOrder(1)  # msoSendToBack
                                        move_operations.append("sent to back")
                                    elif z_action == "bring_forward":
                                        target_shape.ZOrder(2)  # msoBringForward
                                        move_operations.append("brought forward")
                                    elif z_action == "send_backward":
                                        target_shape.ZOrder(3)  # msoSendBackward
                                        move_operations.append("sent backward")
                                
                                if move_operations:
                                    shapes_modified += 1
                                    operations_performed.append(f"Moved shape '{shape_name}': {', '.join(move_operations)}")
                                    logger.info(f"Moved shape '{shape_name}' on slide {slide_number}")
                                else:
                                    operations_performed.append(f"No move parameters specified for '{shape_name}'")
                            else:
                                operations_performed.append(f"Shape '{shape_name}' not found for move")
                        
                        elif op_type == "group":
                            # Group multiple shapes together
                            shape_names = operation.get("shape_names", [])
                            group_name = operation.get("group_name", "GroupedShapes")
                            
                            if len(shape_names) < 2:
                                operations_performed.append(f"Operation {i}: Need at least 2 shapes to group")
                                continue
                            
                            # Find all shapes to group
                            shapes_to_group = []
                            for name in shape_names:
                                for shape in slide.Shapes:
                                    if shape.Name == name:
                                        shapes_to_group.append(shape)
                                        break
                            
                            if len(shapes_to_group) >= 2:
                                try:
                                    # Create a range of shapes
                                    shape_range = slide.Shapes.Range([s.Name for s in shapes_to_group])
                                    # Group them
                                    grouped_shape = shape_range.Group()
                                    grouped_shape.Name = group_name
                                    
                                    shapes_modified += len(shapes_to_group)
                                    operations_performed.append(f"Grouped {len(shapes_to_group)} shapes into '{group_name}'")
                                    logger.info(f"Grouped {len(shapes_to_group)} shapes on slide {slide_number}")
                                except Exception as e:
                                    operations_performed.append(f"Failed to group shapes: {str(e)}")
                                    logger.error(f"Grouping failed: {e}")
                            else:
                                operations_performed.append(f"Could only find {len(shapes_to_group)} of {len(shape_names)} shapes for grouping")
                        
                        elif op_type == "ungroup":
                            # Ungroup a grouped shape
                            if not shape_name:
                                operations_performed.append(f"Operation {i}: Missing shape_name for ungroup")
                                continue
                            
                            target_shape = None
                            for shape in slide.Shapes:
                                if shape.Name == shape_name:
                                    target_shape = shape
                                    break
                            
                            if target_shape:
                                try:
                                    # Check if it's a grouped shape
                                    if hasattr(target_shape, 'Ungroup'):
                                        ungrouped_shapes = target_shape.Ungroup()
                                        
                                        shapes_modified += ungrouped_shapes.Count
                                        operations_performed.append(f"Ungrouped '{shape_name}' into {ungrouped_shapes.Count} shapes")
                                        logger.info(f"Ungrouped shape '{shape_name}' on slide {slide_number}")
                                    else:
                                        operations_performed.append(f"Shape '{shape_name}' is not a group")
                                except Exception as e:
                                    operations_performed.append(f"Failed to ungroup '{shape_name}': {str(e)}")
                                    logger.error(f"Ungrouping failed: {e}")
                            else:
                                operations_performed.append(f"Shape '{shape_name}' not found for ungroup")
                        
                        elif op_type == "transform":
                            # Transform existing shape (rotate, scale, etc.)
                            if not shape_name:
                                operations_performed.append(f"Operation {i}: Missing shape_name for transform")
                                continue
                            
                            target_shape = None
                            for shape in slide.Shapes:
                                if shape.Name == shape_name:
                                    target_shape = shape
                                    break
                            
                            if target_shape:
                                # Apply transformations
                                if "rotation" in properties:
                                    target_shape.Rotation = properties["rotation"]
                                
                                if "flip_horizontal" in properties and properties["flip_horizontal"]:
                                    target_shape.Flip(0)  # msoFlipHorizontal
                                
                                if "flip_vertical" in properties and properties["flip_vertical"]:
                                    target_shape.Flip(1)  # msoFlipVertical
                                
                                # Scale (multiply current dimensions)
                                if "scale_width" in properties:
                                    target_shape.Width = target_shape.Width * properties["scale_width"]
                                
                                if "scale_height" in properties:
                                    target_shape.Height = target_shape.Height * properties["scale_height"]
                                
                                transforms = [k for k in properties.keys() if k in ["rotation", "flip_horizontal", "flip_vertical", "scale_width", "scale_height"]]
                                shapes_modified += 1
                                operations_performed.append(f"Transformed shape '{shape_name}': {', '.join(transforms)}")
                                logger.info(f"Applied {len(transforms)} transformations to shape '{shape_name}'")
                            else:
                                operations_performed.append(f"Shape '{shape_name}' not found for transform")
                        
                        else:
                            operations_performed.append(f"Operation {i}: Unsupported operation type '{op_type}'")
                    
                    except Exception as e:
                        logger.error(f"Error executing operation {i} ({op_type}): {e}")
                        operations_performed.append(f"Operation {i} failed: {str(e)}")
                
                # Save the presentation
                if not executor.save_presentation():
                    logger.warning("Failed to save presentation after shape operations")
            
            success = shapes_modified > 0
            message = f"Successfully executed operations on {shapes_modified} shapes" if success else "No shapes were modified"
            
            # Capture slide image for visual verification if requested and operations were successful
            slide_image = None
            visual_verification = None
            
            if capture_result and success:
                try:
                    slide_image = capture_single_slide_after_operation(
                        presentation_path, 
                        slide_number
                    )
                    
                    if slide_image:
                        visual_verification = {
                            "captured": True,
                            "slide_number": slide_number,
                            "operations_count": shapes_modified,
                            "capture_time": datetime.now().isoformat(),
                            "image_format": "PNG",
                            "encoding": "base64",
                            "purpose": "multimodal_verification"
                        }
                        logger.info(f"Captured slide {slide_number} for visual verification")
                    else:
                        visual_verification = {
                            "captured": False,
                            "reason": "Slide capture failed or not available"
                        }
                        logger.warning(f"Failed to capture slide {slide_number} for visual verification")
                        
                except Exception as e:
                    logger.error(f"Error during slide capture: {e}")
                    visual_verification = {
                        "captured": False,
                        "reason": f"Capture error: {str(e)}"
                    }
            
            return ShapeEditResult(
                success=success,
                message=message,
                shapes_modified=shapes_modified,
                operations_performed=operations_performed,
                slide_image=slide_image,
                visual_verification=visual_verification
            )
            
        except Exception as e:
            logger.exception(f"Error in manage_slide_shapes: {str(e)}")
            return ShapeEditResult(
                success=False,
                message="Shape management failed",
                error=f"Failed to manage slide shapes: {str(e)}"
            )


def _process_text_with_newlines(text: str) -> str:
    """
    Process text to properly handle newline characters for PowerPoint COM.
    
    Args:
        text: Input text that may contain \n characters
        
    Returns:
        Processed text with proper line breaks for PowerPoint
    """
    if not text:
        return text
    
    # Use a temporary placeholder to handle escaped newlines correctly
    # This ensures that \\n becomes literal \n, not PowerPoint line breaks
    temp_placeholder = "__ESCAPED_NEWLINE_PLACEHOLDER__"
    
    # Step 1: Replace escaped newlines with placeholder
    processed_text = text.replace('\\n', temp_placeholder)
    
    # Step 2: Convert actual newlines to PowerPoint line breaks (\r)
    # PowerPoint COM uses \r (carriage return) for line breaks in text ranges
    processed_text = processed_text.replace('\n', '\r')
    
    # Step 3: Restore escaped newlines as literal newlines
    processed_text = processed_text.replace(temp_placeholder, '\n')
    
    # Also handle common text formatting patterns
    processed_text = processed_text.replace('\\t', '\t')  # Handle tabs
    
    return processed_text


def _set_text_with_line_breaks(text_range, text: str, preserve_formatting: bool = True) -> bool:
    """
    Set text in a PowerPoint TextRange with proper line break handling.
    
    Args:
        text_range: PowerPoint TextRange COM object
        text: Text to set (may contain newlines)
        preserve_formatting: Whether to preserve existing formatting
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Process the text for proper newline handling
        processed_text = _process_text_with_newlines(text)
        
        if preserve_formatting and text_range.Text.strip():
            # Store original formatting before clearing
            original_font = {}
            try:
                original_font = {
                    'name': text_range.Font.Name,
                    'size': text_range.Font.Size,
                    'color': text_range.Font.Color.RGB,
                    'bold': text_range.Font.Bold,
                    'italic': text_range.Font.Italic
                }
            except:
                pass
            
            # Set the new text
            text_range.Text = processed_text
            
            # Restore formatting to the entire text range
            try:
                if 'name' in original_font:
                    text_range.Font.Name = original_font['name']
                if 'size' in original_font:
                    text_range.Font.Size = original_font['size']
                if 'color' in original_font:
                    text_range.Font.Color.RGB = original_font['color']
                if 'bold' in original_font:
                    text_range.Font.Bold = original_font['bold']
                if 'italic' in original_font:
                    text_range.Font.Italic = original_font['italic']
            except:
                pass
        else:
            # Simple text replacement without formatting preservation
            text_range.Text = processed_text
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting text with line breaks: {e}")
        return False


def get_shape_editing_tools():
    """Get shape editing tools registration function."""
    return register_shape_editing_tools
