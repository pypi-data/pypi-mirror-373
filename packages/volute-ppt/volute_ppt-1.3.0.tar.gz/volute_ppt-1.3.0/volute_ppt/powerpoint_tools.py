"""
Advanced PowerPoint tools for FastMCP server.
Provides comprehensive PowerPoint manipulation capabilities including metadata extraction,
presentation analysis, slide content analysis, and more.
"""

import os
import json
import tempfile
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Import our PowerPoint metadata extractor
from .powerpoint_metadata import PowerPointMetadataExtractor, PPTX_AVAILABLE

# Configure logging
logger = logging.getLogger(__name__)


class PowerPointAnalysisResult(BaseModel):
    """Model for PowerPoint analysis results."""
    success: bool = Field(description="Whether the analysis was successful")
    message: str = Field(description="Status message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Analysis data")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class SlideContentSummary(BaseModel):
    """Model for slide content summary."""
    slide_number: int = Field(description="Slide number")
    title: Optional[str] = Field(default=None, description="Slide title if found")
    text_content: str = Field(description="All text content from the slide")
    shape_count: int = Field(description="Total number of shapes on slide")
    has_images: bool = Field(description="Whether slide contains images")
    has_tables: bool = Field(description="Whether slide contains tables")
    has_charts: bool = Field(description="Whether slide contains charts")


class PresentationSummary(BaseModel):
    """Model for presentation summary."""
    filename: str = Field(description="Presentation filename")
    total_slides: int = Field(description="Total number of slides")
    title: Optional[str] = Field(default=None, description="Presentation title")
    author: Optional[str] = Field(default=None, description="Presentation author")
    created: Optional[str] = Field(default=None, description="Creation date")
    modified: Optional[str] = Field(default=None, description="Last modified date")
    slides: List[SlideContentSummary] = Field(description="Summary of each slide")


def register_powerpoint_tools(mcp: FastMCP) -> None:
    """
    Register all PowerPoint tools with the FastMCP server.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    
    @mcp.tool()
    def extract_powerpoint_metadata(
        presentation_path: str = Field(description="Path to the PowerPoint file (.pptx, .ppt)"),
        include_slide_content: bool = Field(default=True, description="Include detailed slide content analysis"),
        include_master_slides: bool = Field(default=False, description="Include slide master information"),
        include_layouts: bool = Field(default=False, description="Include slide layout information"),
        output_format: str = Field(default="json", description="Output format: 'json' or 'summary'")
    ) -> PowerPointAnalysisResult:
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
        """
        try:
            if not PPTX_AVAILABLE:
                return PowerPointAnalysisResult(
                    success=False,
                    message="Error",
                    error="python-pptx library is not available. Please install it with: pip install python-pptx"
                )
            
            # Validate file exists
            if not os.path.exists(presentation_path):
                return PowerPointAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"File not found: {presentation_path}"
                )
            
            # Check file extension
            file_ext = os.path.splitext(presentation_path)[1].lower()
            if file_ext not in ['.pptx', '.ppt']:
                return PowerPointAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"Unsupported file format: {file_ext}. Only .pptx and .ppt files are supported."
                )
            
            # Extract metadata using our extractor
            with PowerPointMetadataExtractor(presentation_path) as extractor:
                metadata = extractor.extract_presentation_metadata(
                    include_slide_content=include_slide_content,
                    include_master_slides=include_master_slides,
                    include_layouts=include_layouts
                )
            
            if output_format.lower() == "summary":
                # Convert to summary format
                summary = _create_presentation_summary(metadata)
                return PowerPointAnalysisResult(
                    success=True,
                    message="PowerPoint metadata extracted successfully (summary format)",
                    data=summary.dict()
                )
            else:
                return PowerPointAnalysisResult(
                    success=True,
                    message="PowerPoint metadata extracted successfully",
                    data=metadata
                )
                
        except Exception as e:
            logger.exception(f"Error extracting PowerPoint metadata: {str(e)}")
            return PowerPointAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"Failed to extract metadata: {str(e)}"
            )

    @mcp.tool()
    def analyze_powerpoint_content(
        presentation_path: str = Field(description="Path to the PowerPoint file (.pptx, .ppt)"),
        slide_numbers: Optional[List[int]] = Field(default=None, description="Specific slide numbers to analyze (1-based). If None, analyzes all slides"),
        extract_text_only: bool = Field(default=False, description="Extract only text content, skip formatting details")
    ) -> PowerPointAnalysisResult:
        """
        Analyze content of specific slides in a PowerPoint presentation.
        
        This tool provides focused content analysis of PowerPoint slides, extracting:
        - Text content from all text boxes and shapes
        - Slide titles and bullet points
        - Table data and content
        - Image descriptions and alt text
        - Shape types and basic properties
        """
        try:
            if not PPTX_AVAILABLE:
                return PowerPointAnalysisResult(
                    success=False,
                    message="Error",
                    error="python-pptx library is not available. Please install it with: pip install python-pptx"
                )
            
            if not os.path.exists(presentation_path):
                return PowerPointAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"File not found: {presentation_path}"
                )
            
            with PowerPointMetadataExtractor() as extractor:
                extractor.open_presentation(presentation_path)
                if extract_text_only:
                    # Quick text-only extraction
                    content = _extract_text_content_only(extractor, slide_numbers)
                else:
                    # Full content analysis
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
            
            return PowerPointAnalysisResult(
                success=True,
                message=f"Content analysis completed for {len(content.get('slides', []))} slides",
                data=content
            )
                
        except Exception as e:
            logger.exception(f"Error analyzing PowerPoint content: {str(e)}")
            return PowerPointAnalysisResult(
                success=False,
                message="Analysis failed",
                error=f"Failed to analyze content: {str(e)}"
            )

    @mcp.tool()
    def get_powerpoint_summary(
        presentation_path: str = Field(description="Path to the PowerPoint file (.pptx, .ppt)")
    ) -> PowerPointAnalysisResult:
        """
        Get a high-level summary of a PowerPoint presentation.
        
        This tool provides a quick overview including:
        - Basic presentation properties (title, author, dates)
        - Slide count and structure
        - Content overview for each slide
        - Presence of multimedia elements
        """
        try:
            if not PPTX_AVAILABLE:
                return PowerPointAnalysisResult(
                    success=False,
                    message="Error",
                    error="python-pptx library is not available. Please install it with: pip install python-pptx"
                )
            
            if not os.path.exists(presentation_path):
                return PowerPointAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"File not found: {presentation_path}"
                )
            
            with PowerPointMetadataExtractor(presentation_path) as extractor:
                # Extract minimal metadata for summary
                metadata = extractor.extract_presentation_metadata(
                    include_slide_content=True,
                    include_master_slides=False,
                    include_layouts=False
                )
            
            # Create summary
            summary = _create_presentation_summary(metadata)
            
            return PowerPointAnalysisResult(
                success=True,
                message="Presentation summary generated successfully",
                data={
                    "summary": summary.model_dump(),
                    "quickStats": {
                        "totalSlides": summary.total_slides,
                        "slidesWithImages": sum(1 for slide in summary.slides if slide.has_images),
                        "slidesWithTables": sum(1 for slide in summary.slides if slide.has_tables),
                        "slidesWithCharts": sum(1 for slide in summary.slides if slide.has_charts),
                        "totalShapes": sum(slide.shape_count for slide in summary.slides),
                        "averageShapesPerSlide": sum(slide.shape_count for slide in summary.slides) / len(summary.slides) if summary.slides else 0
                    }
                }
            )
                
        except Exception as e:
            logger.exception(f"Error creating PowerPoint summary: {str(e)}")
            return PowerPointAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"Failed to create summary: {str(e)}"
            )

    @mcp.tool()
    def validate_powerpoint_file(
        presentation_path: str = Field(description="Path to the PowerPoint file to validate")
    ) -> PowerPointAnalysisResult:
        """
        Validate a PowerPoint file and check for common issues.
        
        This tool checks:
        - File format and compatibility
        - File corruption or accessibility issues
        - Basic structural integrity
        - Slide count and basic properties
        """
        try:
            validation_results = {
                "isValid": False,
                "fileExists": False,
                "isAccessible": False,
                "fileFormat": None,
                "fileSize": None,
                "canOpenPresentation": False,
                "slideCount": 0,
                "hasValidStructure": False,
                "issues": [],
                "warnings": []
            }
            
            # Check if file exists
            if not os.path.exists(presentation_path):
                validation_results["issues"].append("File does not exist")
                return PowerPointAnalysisResult(
                    success=True,
                    message="File validation completed with issues",
                    data=validation_results
                )
            
            validation_results["fileExists"] = True
            
            # Check file access and size
            try:
                stat_info = os.stat(presentation_path)
                validation_results["fileSize"] = stat_info.st_size
                validation_results["isAccessible"] = True
                
                if stat_info.st_size == 0:
                    validation_results["issues"].append("File is empty (0 bytes)")
                elif stat_info.st_size < 1024:
                    validation_results["warnings"].append("File is very small, may be corrupted")
                    
            except OSError as e:
                validation_results["issues"].append(f"Cannot access file: {str(e)}")
                return PowerPointAnalysisResult(
                    success=True,
                    message="File validation completed with issues",
                    data=validation_results
                )
            
            # Check file format
            file_ext = os.path.splitext(presentation_path)[1].lower()
            validation_results["fileFormat"] = file_ext
            
            if file_ext not in ['.pptx', '.ppt']:
                validation_results["issues"].append(f"Unsupported file format: {file_ext}")
            
            # Try to open with python-pptx if available
            if PPTX_AVAILABLE and file_ext in ['.pptx', '.ppt']:
                try:
                    with PowerPointMetadataExtractor() as extractor:
                        extractor.open_presentation(presentation_path)
                        validation_results["canOpenPresentation"] = True
                        validation_results["slideCount"] = len(extractor.presentation.slides)
                        validation_results["hasValidStructure"] = True
                        
                        if validation_results["slideCount"] == 0:
                            validation_results["warnings"].append("Presentation has no slides")
                        elif validation_results["slideCount"] > 1000:
                            validation_results["warnings"].append("Presentation has unusually many slides")
                            
                except Exception as e:
                    validation_results["issues"].append(f"Cannot open presentation: {str(e)}")
            elif not PPTX_AVAILABLE:
                validation_results["warnings"].append("python-pptx not available - limited validation")
            
            # Determine overall validity
            validation_results["isValid"] = (
                validation_results["fileExists"] and 
                validation_results["isAccessible"] and 
                len(validation_results["issues"]) == 0
            )
            
            status = "valid" if validation_results["isValid"] else "invalid"
            issue_count = len(validation_results["issues"])
            warning_count = len(validation_results["warnings"])
            
            message = f"File validation completed - {status}"
            if issue_count > 0:
                message += f" ({issue_count} issues"
                if warning_count > 0:
                    message += f", {warning_count} warnings"
                message += ")"
            elif warning_count > 0:
                message += f" ({warning_count} warnings)"
            
            return PowerPointAnalysisResult(
                success=True,
                message=message,
                data=validation_results
            )
                
        except Exception as e:
            logger.exception(f"Error validating PowerPoint file: {str(e)}")
            return PowerPointAnalysisResult(
                    success=False,
                    message="Error",
                    error=f"Failed to validate file: {str(e)}"
            )
    
    @mcp.tool()
    def manage_presentation_slides(
        presentation_path: str = Field(description="Path to the PowerPoint file (.pptx, .ppt)"),
        dsl_operations: str = Field(
            description="""Slide management operations in pipe-delimited DSL format.
            
            CRITICAL: Use this EXACT pipe-delimited format:
            operation_type: param=value, param=value | next_operation: param=value
            
            SUPPORTED OPERATIONS:
            
            1. ADD NEW SLIDE:
            add_slide: position=N, layout="Layout Name"
            - position: Where to insert (1-based, or "end" for last)
            - layout: "Title Slide", "Title and Content", "Blank", etc.
            
            2. DELETE SLIDE:
            delete_slide: slide_number=N
            - slide_number: Slide to delete (1-based)
            
            3. MOVE SLIDE:
            move_slide: from=N, to=M
            - from: Current position (1-based)
            - to: New position (1-based)
            
            4. DUPLICATE SLIDE:
            duplicate_slide: source=N, position=M
            - source: Slide to copy (1-based)
            - position: Where to insert copy (1-based, or "end")
            
            EXAMPLES:
            - Add title slide at beginning: "add_slide: position=1, layout=\"Title Slide\""
            - Delete slide 3: "delete_slide: slide_number=3"
            - Move slide 2 to position 5: "move_slide: from=2, to=5"
            - Duplicate slide 1 at end: "duplicate_slide: source=1, position=end"
            - Multiple operations: "add_slide: position=1, layout=\"Title Slide\" | delete_slide: slide_number=5 | move_slide: from=2, to=3"
            
            FORMAT REQUIREMENTS:
            - Use pipe (|) to separate multiple operations
            - Use exact parameter names (position, layout, slide_number, from, to, source)
            - Quote layout names with spaces
            - Operations execute in left-to-right order
            """
        )
    ) -> PowerPointAnalysisResult:
        """
        Manage PowerPoint presentation slides using DSL format.
        
        This tool allows you to add, delete, move, and duplicate slides in PowerPoint presentations
        using a simple Domain Specific Language (DSL) format. Operations are executed using
        Windows COM automation for reliable PowerPoint integration.
        
        The tool supports:
        - Adding new slides with specific layouts at any position
        - Deleting slides by slide number
        - Moving slides from one position to another
        - Duplicating slides to any position
        - Multiple operations in a single command
        
        All operations use 1-based slide numbering and are executed in the order specified.
        The presentation is automatically saved after successful operations.
        """
        try:
            # Import PowerPoint slide management modules
            from .powerpoint import (
                parse_slide_operations_dsl,
                validate_slide_dsl_format,
                execute_slide_operations
            )
            
            # Validate file exists
            if not os.path.exists(presentation_path):
                return PowerPointAnalysisResult(
                    success=False,
                    message="File not found",
                    error=f"PowerPoint file not found: {presentation_path}"
                )
            
            # Check file extension
            file_ext = os.path.splitext(presentation_path)[1].lower()
            if file_ext not in ['.pptx', '.ppt']:
                return PowerPointAnalysisResult(
                    success=False,
                    message="Unsupported file format",
                    error=f"Unsupported file format: {file_ext}. Only .pptx and .ppt files are supported."
                )
            
            # Validate DSL format first
            validation_result = validate_slide_dsl_format(dsl_operations)
            if not validation_result["valid"]:
                return PowerPointAnalysisResult(
                    success=False,
                    message="Invalid DSL format",
                    error="DSL validation failed",
                    data={
                        "validation_errors": validation_result["errors"],
                        "suggestions": validation_result["suggestions"],
                        "your_input": dsl_operations
                    }
                )
            
            # Parse DSL operations
            parsed_operations = parse_slide_operations_dsl(dsl_operations)
            if not parsed_operations:
                return PowerPointAnalysisResult(
                    success=False,
                    message="DSL parsing failed",
                    error="Could not parse slide operations from DSL input",
                    data={"dsl_input": dsl_operations}
                )
            
            logger.info(f"Parsed {parsed_operations['total_operations']} slide operations")
            
            # Execute slide operations
            execution_result = execute_slide_operations(
                presentation_path,
                parsed_operations["operations"]
            )
            
            # Prepare response data
            response_data = {
                "operations_parsed": parsed_operations["total_operations"],
                "operations_executed": execution_result["operations_executed"],
                "operations_failed": execution_result["operations_failed"],
                "final_slide_count": execution_result["final_slide_count"],
                "operation_details": execution_result["details"],
                "parsed_operations": parsed_operations["operations"]
            }
            
            if execution_result["success"]:
                return PowerPointAnalysisResult(
                    success=True,
                    message=f"Successfully executed {execution_result['operations_executed']} slide operations. Final slide count: {execution_result['final_slide_count']}",
                    data=response_data
                )
            else:
                return PowerPointAnalysisResult(
                    success=False,
                    message=f"Slide operations completed with errors: {execution_result['operations_failed']} failed",
                    error=execution_result.get("error", "Some operations failed"),
                    data=response_data
                )
                
        except ImportError as e:
            return PowerPointAnalysisResult(
                success=False,
                message="PowerPoint modules not available",
                error=f"Could not import PowerPoint slide management modules: {e}"
            )
        except Exception as e:
            logger.exception(f"Error in manage_presentation_slides: {str(e)}")
            return PowerPointAnalysisResult(
                success=False,
                message="Error",
                error=f"Failed to manage presentation slides: {str(e)}"
            )


def _create_presentation_summary(metadata: Dict[str, Any]) -> PresentationSummary:
    """Create a presentation summary from extracted metadata."""
    core_props = metadata.get("coreProperties", {})
    slides_data = metadata.get("slides", [])
    
    slide_summaries = []
    for slide_data in slides_data:
        # Extract slide title (usually first text box or shape with large font)
        title = _extract_slide_title(slide_data)
        
        # Extract all text content
        text_content = _extract_all_text_from_slide(slide_data)
        
        # Count shape types
        shapes = slide_data.get("shapes", [])
        has_images = any(
            shape.get("shapeType", "").find("PICTURE") >= 0 or 
            "imageData" in shape 
            for shape in shapes
        )
        has_tables = any(
            shape.get("shapeType", "").find("TABLE") >= 0 or 
            "tableData" in shape 
            for shape in shapes
        )
        has_charts = any(
            shape.get("shapeType", "").find("CHART") >= 0 or
            shape.get("shapeType", "").find("GRAPHIC") >= 0
            for shape in shapes
        )
        
        slide_summary = SlideContentSummary(
            slide_number=slide_data.get("slideNumber", 0),
            title=title,
            text_content=text_content,
            shape_count=len(shapes),
            has_images=has_images,
            has_tables=has_tables,
            has_charts=has_charts
        )
        slide_summaries.append(slide_summary)
    
    return PresentationSummary(
        filename=metadata.get("presentationName", "Unknown"),
        total_slides=metadata.get("totalSlides", 0),
        title=core_props.get("title"),
        author=core_props.get("author"),
        created=core_props.get("created"),
        modified=core_props.get("modified"),
        slides=slide_summaries
    )


def _extract_slide_title(slide_data: Dict[str, Any]) -> Optional[str]:
    """Extract likely slide title from slide data."""
    shapes = slide_data.get("shapes", [])
    
    # Look for shapes with text that might be titles
    title_candidates = []
    
    for shape in shapes:
        text_content = shape.get("textContent", {})
        if not text_content.get("hasText"):
            continue
            
        text = text_content.get("text", "").strip()
        if not text:
            continue
            
        # Check if this could be a title based on position and formatting
        position = shape.get("position", {})
        top_inches = position.get("topInches", 999)
        
        # Titles are usually near the top
        if top_inches < 2.0:  # Top 2 inches of slide
            # Check font size in paragraphs/runs
            max_font_size = 0
            paragraphs = text_content.get("paragraphs", [])
            for para in paragraphs:
                for run in para.get("runs", []):
                    font = run.get("font", {})
                    size = font.get("size", 0) or 0
                    if size > max_font_size:
                        max_font_size = size
            
            title_candidates.append({
                "text": text,
                "top": top_inches,
                "font_size": max_font_size,
                "length": len(text)
            })
    
    if not title_candidates:
        return None
    
    # Sort by position (top first) and font size (larger first)
    title_candidates.sort(key=lambda x: (x["top"], -x["font_size"]))
    
    # Return the best candidate (topmost, largest font)
    best_candidate = title_candidates[0]
    
    # Only return if it looks like a reasonable title
    if best_candidate["length"] < 200 and best_candidate["font_size"] > 14:
        return best_candidate["text"]
    
    return None


def _extract_all_text_from_slide(slide_data: Dict[str, Any]) -> str:
    """Extract all text content from a slide."""
    shapes = slide_data.get("shapes", [])
    all_text = []
    
    for shape in shapes:
        # Text from text content
        text_content = shape.get("textContent", {})
        if text_content.get("hasText"):
            text = text_content.get("text", "").strip()
            if text:
                all_text.append(text)
        
        # Text from table data
        table_data = shape.get("tableData", {})
        if "cells" in table_data:
            for cell in table_data["cells"]:
                cell_text = cell.get("text", "").strip()
                if cell_text:
                    all_text.append(cell_text)
    
    return " ".join(all_text)


def _extract_text_content_only(extractor: PowerPointMetadataExtractor, slide_numbers: Optional[List[int]] = None) -> Dict[str, Any]:
    """Extract only text content from slides for quick analysis."""
    if not extractor.presentation:
        raise ValueError("No presentation loaded")
    
    slides_to_analyze = slide_numbers or list(range(1, len(extractor.presentation.slides) + 1))
    
    result = {
        "extractedAt": datetime.now().isoformat(),
        "presentationPath": extractor.presentation_path,
        "textOnlyExtraction": True,
        "analyzedSlides": slides_to_analyze,
        "slides": []
    }
    
    for i, slide in enumerate(extractor.presentation.slides):
        slide_num = i + 1
        if slide_num not in slides_to_analyze:
            continue
            
        slide_text = {
            "slideNumber": slide_num,
            "textContent": []
        }
        
        # Extract text from all shapes
        for j, shape in enumerate(slide.shapes):
            if hasattr(shape, 'text_frame') and shape.has_text_frame:
                text = shape.text_frame.text.strip()
                if text:
                    slide_text["textContent"].append({
                        "shapeIndex": j,
                        "text": text
                    })
        
        # Extract text from tables
        for j, shape in enumerate(slide.shapes):
            try:
                if hasattr(shape, 'table'):
                    table = shape.table
                    table_texts = []
                    for row in table.rows:
                        for cell in row.cells:
                            cell_text = cell.text.strip()
                            if cell_text:
                                table_texts.append(cell_text)
                    
                    if table_texts:
                        slide_text["textContent"].append({
                            "shapeIndex": j,
                            "type": "table",
                            "text": " | ".join(table_texts)
                        })
            except:
                pass  # Skip if not a table or has issues
        
        result["slides"].append(slide_text)
    
    return result



# Register tools when module is imported
def get_powerpoint_tools():
    """Get PowerPoint tools registration function."""
    return register_powerpoint_tools
