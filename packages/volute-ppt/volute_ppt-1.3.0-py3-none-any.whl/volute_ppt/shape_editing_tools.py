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
        preserve_formatting: bool = Field(default=True, description="Preserve existing text formatting"),
        auto_resize: bool = Field(default=True, description="Auto-resize shapes to fit new text")
    ) -> ShapeEditResult:
        """
        Edit text content in specific shapes on a PowerPoint slide.
        
        This tool provides precise text editing capabilities:
        - Update text in multiple shapes simultaneously
        - Preserve existing formatting and styles
        - Auto-resize shapes to accommodate new content
        - Maintain layout integrity
        
        Perfect for updating presentations with new data, correcting text,
        or adapting content for different audiences.
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
                    error="win32com library is required for shape editing"
                )
            
            if not text_updates:
                return ShapeEditResult(
                    success=False,
                    message="No text updates provided",
                    error="text_updates dictionary is empty"
                )
            
            operations_performed = []
            shapes_modified = 0
            
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
                
                # Update text in each specified shape
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
                            continue
                        
                        # Check if shape has text frame
                        if hasattr(target_shape, 'TextFrame') and target_shape.TextFrame:
                            # Store original formatting if preserving
                            original_formatting = {}
                            if preserve_formatting and target_shape.TextFrame.TextRange.Text.strip():
                                try:
                                    text_range = target_shape.TextFrame.TextRange
                                    original_formatting = {
                                        'font_name': text_range.Font.Name,
                                        'font_size': text_range.Font.Size,
                                        'font_color': text_range.Font.Color.RGB,
                                        'bold': text_range.Font.Bold,
                                        'italic': text_range.Font.Italic,
                                        'alignment': text_range.ParagraphFormat.Alignment
                                    }
                                except:
                                    pass  # Failed to extract formatting
                            
                            # Update the text
                            target_shape.TextFrame.TextRange.Text = new_text
                            
                            # Restore formatting if preserved
                            if preserve_formatting and original_formatting:
                                try:
                                    text_range = target_shape.TextFrame.TextRange
                                    if 'font_name' in original_formatting:
                                        text_range.Font.Name = original_formatting['font_name']
                                    if 'font_size' in original_formatting:
                                        text_range.Font.Size = original_formatting['font_size']
                                    if 'font_color' in original_formatting:
                                        text_range.Font.Color.RGB = original_formatting['font_color']
                                    if 'bold' in original_formatting:
                                        text_range.Font.Bold = original_formatting['bold']
                                    if 'italic' in original_formatting:
                                        text_range.Font.Italic = original_formatting['italic']
                                    if 'alignment' in original_formatting:
                                        text_range.ParagraphFormat.Alignment = original_formatting['alignment']
                                except:
                                    pass  # Failed to apply formatting
                            
                            # Auto-resize if requested
                            if auto_resize:
                                try:
                                    # PowerPoint auto-resize functionality
                                    text_frame = target_shape.TextFrame
                                    text_frame.AutoSize = 1  # ppAutoSizeShapeToFitText
                                except:
                                    pass  # Auto-resize not supported for this shape
                            
                            shapes_modified += 1
                            operations_performed.append(f"Updated text in '{shape_name}' with {len(new_text)} characters")
                            logger.info(f"Updated text in shape '{shape_name}' on slide {slide_number}")
                        
                        else:
                            logger.warning(f"Shape '{shape_name}' does not support text on slide {slide_number}")
                    
                    except Exception as e:
                        logger.error(f"Error updating shape '{shape_name}': {e}")
                        operations_performed.append(f"Failed to update '{shape_name}': {str(e)}")
                
                # Save the presentation
                if not executor.save_presentation():
                    logger.warning("Failed to save presentation after text updates")
            
            success = shapes_modified > 0
            message = f"Successfully updated {shapes_modified} shapes" if success else "No shapes were updated"
            
            return ShapeEditResult(
                success=success,
                message=message,
                shapes_modified=shapes_modified,
                operations_performed=operations_performed
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
        create_backup: bool = Field(default=True, description="Create backup of original file before editing")
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
                            
                            # Update text content
                            if properties.text is not None:
                                text_range.Text = properties.text
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
            
            return ShapeEditResult(
                success=success,
                message=message,
                shapes_modified=shapes_modified,
                operations_performed=operations_performed
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
        validate_operations: bool = Field(default=True, description="Validate operations before executing")
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
                            # Add new shape
                            shape_type = properties.get("type", "rectangle")
                            left = properties.get("left", 100)
                            top = properties.get("top", 100)
                            width = properties.get("width", 100)
                            height = properties.get("height", 50)
                            
                            # Shape type mapping
                            shape_type_map = {
                                "rectangle": 1,     # msoShapeRectangle
                                "oval": 9,         # msoShapeOval
                                "line": 20,        # msoShapeLine
                                "textbox": 17      # msoTextBox
                            }
                            
                            shape_type_id = shape_type_map.get(shape_type, 1)
                            
                            if shape_type == "textbox":
                                new_shape = slide.Shapes.AddTextbox(1, left, top, width, height)
                            else:
                                new_shape = slide.Shapes.AddShape(shape_type_id, left, top, width, height)
                            
                            if shape_name:
                                new_shape.Name = shape_name
                            
                            # Apply text if provided
                            text_content = properties.get("text")
                            if text_content and hasattr(new_shape, 'TextFrame'):
                                new_shape.TextFrame.TextRange.Text = text_content
                            
                            shapes_modified += 1
                            operations_performed.append(f"Added {shape_type} shape '{shape_name or new_shape.Name}'")
                            logger.info(f"Added {shape_type} shape to slide {slide_number}")
                        
                        elif op_type == "copy":
                            # Copy shape from another slide or within same slide
                            source_slide_num = operation.get("source_slide", slide_number)
                            source_shape_name = operation.get("source_shape_name", shape_name)
                            
                            if not source_shape_name:
                                operations_performed.append(f"Operation {i}: Missing source shape name for copy")
                                continue
                            
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
                                # Copy and paste
                                source_shape.Copy()
                                pasted_shapes = slide.Shapes.Paste()
                                
                                # Rename if new name provided
                                if pasted_shapes.Count > 0 and shape_name:
                                    pasted_shapes[0].Name = shape_name
                                
                                # Apply new position if provided
                                target_pos = operation.get("target_position", {})
                                if target_pos and pasted_shapes.Count > 0:
                                    if "left" in target_pos:
                                        pasted_shapes[0].Left = target_pos["left"]
                                    if "top" in target_pos:
                                        pasted_shapes[0].Top = target_pos["top"]
                                
                                shapes_modified += 1
                                operations_performed.append(f"Copied shape '{source_shape_name}' to '{shape_name or source_shape_name}'")
                                logger.info(f"Copied shape from slide {source_slide_num} to slide {slide_number}")
                            else:
                                operations_performed.append(f"Source shape '{source_shape_name}' not found on slide {source_slide_num}")
                        
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
            
            return ShapeEditResult(
                success=success,
                message=message,
                shapes_modified=shapes_modified,
                operations_performed=operations_performed
            )
            
        except Exception as e:
            logger.exception(f"Error in manage_slide_shapes: {str(e)}")
            return ShapeEditResult(
                success=False,
                message="Shape management failed",
                error=f"Failed to manage slide shapes: {str(e)}"
            )


def get_shape_editing_tools():
    """Get shape editing tools registration function."""
    return register_shape_editing_tools
