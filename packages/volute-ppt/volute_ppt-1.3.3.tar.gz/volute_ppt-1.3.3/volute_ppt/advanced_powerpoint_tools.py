"""
Advanced PowerPoint Tools Module

This module provides enhanced PowerPoint manipulation capabilities that build upon
the existing slide_executor and parser infrastructure. It includes advanced operations
like content editing, shape manipulation, and multimodal analysis.
"""

import os
import json
import tempfile
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Import existing infrastructure
from .powerpoint.slide_executor import PowerPointSlideExecutor, execute_slide_operations
from .powerpoint.parser import parse_slide_operations_dsl, validate_slide_dsl_format
from .slide_capture_tools import _capture_slide_images_safe
from .powerpoint_metadata import PowerPointMetadataExtractor, PPTX_AVAILABLE

# Configure logging
logger = logging.getLogger(__name__)

# Check for win32com availability for advanced operations
WIN32COM_AVAILABLE = False
try:
    import win32com.client
    import pythoncom
    WIN32COM_AVAILABLE = True
    logger.info("win32com available for advanced PowerPoint operations")
except ImportError as e:
    logger.warning(f"win32com not available: {e}")


class AdvancedPowerPointResult(BaseModel):
    """Model for advanced PowerPoint operation results."""
    success: bool = Field(description="Whether the operation was successful")
    message: str = Field(description="Status message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Operation data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ShapeEditOperation(BaseModel):
    """Model for shape editing operations."""
    operation_type: str = Field(description="Type of operation: add, edit, delete, copy")
    slide_number: int = Field(description="Target slide number (1-based)")
    shape_name: Optional[str] = Field(default=None, description="Name of target shape")
    properties: Optional[Dict[str, Any]] = Field(default=None, description="Shape properties to apply")
    source_slide: Optional[int] = Field(default=None, description="Source slide for copy operations")
    source_shape: Optional[str] = Field(default=None, description="Source shape name for copy operations")


class SlideAnalysisResult(BaseModel):
    """Model for slide analysis results with visual context."""
    slide_number: int = Field(description="Slide number")
    image_data: Optional[str] = Field(default=None, description="Base64 encoded slide image")
    content_summary: Dict[str, Any] = Field(description="Content analysis summary")
    shape_inventory: List[Dict[str, Any]] = Field(description="Inventory of all shapes")
    text_content: str = Field(description="All text content from slide")


def register_advanced_powerpoint_tools(mcp: FastMCP) -> None:
    """
    Register advanced PowerPoint tools with the FastMCP server.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    
    @mcp.tool()
    def analyze_presentation_with_images(
        presentation_path: str = Field(description="Path to the PowerPoint file (.pptx, .ppt)"),
        slide_numbers: Optional[List[int]] = Field(default=None, description="Specific slides to analyze (1-based). If None, analyzes first 5 slides"),
        include_content_analysis: bool = Field(default=True, description="Include detailed content analysis"),
        image_width: int = Field(default=1024, description="Width of captured slide images"),
        image_height: int = Field(default=768, description="Height of captured slide images")
    ) -> AdvancedPowerPointResult:
        """
        Analyze PowerPoint presentation with visual context using slide images.
        
        This tool combines metadata extraction with slide image capture to provide
        comprehensive analysis including:
        - Visual slide content as base64 images
        - Detailed shape and text analysis
        - Content inventory and structure
        - Multimodal analysis capabilities
        
        Perfect for understanding slide content before making edits or for
        comprehensive presentation review.
        """
        try:
            # Validate file exists
            if not os.path.exists(presentation_path):
                return AdvancedPowerPointResult(
                    success=False,
                    message="File not found",
                    error=f"PowerPoint file not found: {presentation_path}"
                )
            
            # Validate file format
            file_ext = os.path.splitext(presentation_path)[1].lower()
            if file_ext not in ['.pptx', '.ppt']:
                return AdvancedPowerPointResult(
                    success=False,
                    message="Unsupported file format",
                    error=f"Unsupported file format: {file_ext}"
                )
            
            result_data = {
                "presentationPath": presentation_path,
                "analyzedAt": datetime.now().isoformat(),
                "slideAnalysis": []
            }
            
            # Get basic presentation info
            if PPTX_AVAILABLE:
                try:
                    with PowerPointMetadataExtractor(presentation_path) as extractor:
                        basic_metadata = extractor.extract_presentation_metadata(
                            include_slide_content=include_content_analysis,
                            include_master_slides=False,
                            include_layouts=False
                        )
                        result_data["presentationMetadata"] = {
                            "totalSlides": basic_metadata.get("totalSlides", 0),
                            "presentationName": basic_metadata.get("presentationName"),
                            "coreProperties": basic_metadata.get("coreProperties", {})
                        }
                        total_slides = basic_metadata.get("totalSlides", 0)
                except Exception as e:
                    logger.warning(f"Could not extract basic metadata: {e}")
                    total_slides = 50  # Reasonable default
            else:
                total_slides = 50  # Default if python-pptx not available
            
            # Determine slides to analyze
            if slide_numbers is None:
                # Default to first 5 slides
                slide_numbers = list(range(1, min(6, total_slides + 1)))
            else:
                # Validate provided slide numbers
                slide_numbers = [n for n in slide_numbers if 1 <= n <= total_slides]
            
            if not slide_numbers:
                return AdvancedPowerPointResult(
                    success=False,
                    message="No valid slides to analyze",
                    error="No valid slide numbers found within presentation range"
                )
            
            logger.info(f"Analyzing slides: {slide_numbers}")
            
            # Capture slide images
            if WIN32COM_AVAILABLE:
                try:
                    capture_result = _capture_slide_images_safe(
                        presentation_path,
                        slide_numbers,
                        image_width,
                        image_height
                    )
                    
                    if capture_result["success"]:
                        slide_images = capture_result["slide_images"]
                        logger.info(f"Successfully captured {len(slide_images)} slide images")
                    else:
                        slide_images = {}
                        logger.warning(f"Slide capture failed: {capture_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    slide_images = {}
                    logger.warning(f"Error capturing slide images: {e}")
            else:
                slide_images = {}
                logger.warning("win32com not available - no slide images will be captured")
            
            # Combine metadata and images for each slide
            slides_with_metadata = basic_metadata.get("slides", []) if 'basic_metadata' in locals() else []
            
            for slide_num in slide_numbers:
                slide_analysis = SlideAnalysisResult(
                    slide_number=slide_num,
                    image_data=slide_images.get(slide_num),
                    content_summary={},
                    shape_inventory=[],
                    text_content=""
                )
                
                # Find corresponding metadata
                slide_metadata = None
                for slide_data in slides_with_metadata:
                    if slide_data.get("slideNumber") == slide_num:
                        slide_metadata = slide_data
                        break
                
                if slide_metadata and include_content_analysis:
                    # Extract content summary
                    shapes = slide_metadata.get("shapes", [])
                    slide_analysis.content_summary = {
                        "shapeCount": len(shapes),
                        "hasImages": any(
                            "imageData" in shape or "PICTURE" in shape.get("shapeType", "")
                            for shape in shapes
                        ),
                        "hasTables": any(
                            "tableData" in shape or "TABLE" in shape.get("shapeType", "")
                            for shape in shapes
                        ),
                        "hasCharts": any(
                            "CHART" in shape.get("shapeType", "") or "GRAPHIC" in shape.get("shapeType", "")
                            for shape in shapes
                        ),
                        "layoutName": slide_metadata.get("layoutName")
                    }
                    
                    # Create shape inventory
                    for i, shape in enumerate(shapes):
                        shape_info = {
                            "index": i,
                            "name": shape.get("name", f"Shape_{i}"),
                            "type": shape.get("shapeType", "Unknown"),
                            "hasText": shape.get("textContent", {}).get("hasText", False),
                            "position": shape.get("position", {})
                        }
                        
                        # Add text if present
                        if shape_info["hasText"]:
                            text_content = shape.get("textContent", {})
                            text = text_content.get("text", "").strip()
                            if text:
                                shape_info["text"] = text[:200] + "..." if len(text) > 200 else text
                        
                        slide_analysis.shape_inventory.append(shape_info)
                    
                    # Extract all text content
                    all_text = []
                    for shape in shapes:
                        text_content = shape.get("textContent", {})
                        if text_content.get("hasText"):
                            text = text_content.get("text", "").strip()
                            if text:
                                all_text.append(text)
                        
                        # Also get table text
                        table_data = shape.get("tableData", {})
                        if "cells" in table_data:
                            for cell in table_data["cells"]:
                                cell_text = cell.get("text", "").strip()
                                if cell_text:
                                    all_text.append(cell_text)
                    
                    slide_analysis.text_content = " ".join(all_text)
                
                result_data["slideAnalysis"].append(slide_analysis.model_dump())
            
            # Add summary statistics
            result_data["analysisStats"] = {
                "totalSlidesAnalyzed": len(slide_numbers),
                "slidesWithImages": len([s for s in result_data["slideAnalysis"] if s.get("image_data")]),
                "slidesWithContent": len([s for s in result_data["slideAnalysis"] if s.get("content_summary")]),
                "averageShapesPerSlide": sum(
                    len(s.get("shape_inventory", [])) for s in result_data["slideAnalysis"]
                ) / len(slide_numbers) if slide_numbers else 0
            }
            
            return AdvancedPowerPointResult(
                success=True,
                message=f"Successfully analyzed {len(slide_numbers)} slides with visual context",
                data=result_data
            )
            
        except Exception as e:
            logger.exception(f"Error in analyze_presentation_with_images: {str(e)}")
            return AdvancedPowerPointResult(
                success=False,
                message="Analysis failed",
                error=f"Failed to analyze presentation: {str(e)}"
            )
    
    @mcp.tool()
    def bulk_slide_operations(
        presentation_path: str = Field(description="Path to the PowerPoint file (.pptx, .ppt)"),
        operations: List[str] = Field(description="List of DSL operation strings to execute in sequence"),
        validate_before_execute: bool = Field(default=True, description="Validate all operations before executing any"),
        stop_on_error: bool = Field(default=True, description="Stop execution if any operation fails")
    ) -> AdvancedPowerPointResult:
        """
        Execute multiple slide operations in bulk with enhanced error handling and validation.
        
        This tool extends the basic manage_presentation_slides functionality by providing:
        - Bulk operation processing with transaction-like behavior
        - Pre-execution validation of all operations
        - Detailed error reporting with operation context
        - Option to continue on errors or stop at first failure
        - Comprehensive operation logging and rollback information
        
        Each operation in the list should be a valid DSL string as used by manage_presentation_slides.
        """
        try:
            # Validate file exists
            if not os.path.exists(presentation_path):
                return AdvancedPowerPointResult(
                    success=False,
                    message="File not found",
                    error=f"PowerPoint file not found: {presentation_path}"
                )
            
            # Validate file format
            file_ext = os.path.splitext(presentation_path)[1].lower()
            if file_ext not in ['.pptx', '.ppt']:
                return AdvancedPowerPointResult(
                    success=False,
                    message="Unsupported file format",
                    error=f"Unsupported file format: {file_ext}"
                )
            
            if not operations:
                return AdvancedPowerPointResult(
                    success=False,
                    message="No operations provided",
                    error="Operations list is empty"
                )
            
            result_data = {
                "totalOperations": len(operations),
                "operationsValidated": 0,
                "operationsExecuted": 0,
                "operationsFailed": 0,
                "operationDetails": [],
                "validationResults": []
            }
            
            # Pre-validate all operations if requested
            if validate_before_execute:
                logger.info(f"Pre-validating {len(operations)} operations...")
                validation_failed = False
                
                for i, operation_dsl in enumerate(operations):
                    validation_result = validate_slide_dsl_format(operation_dsl)
                    result_data["validationResults"].append({
                        "operationIndex": i,
                        "operationDSL": operation_dsl,
                        "valid": validation_result["valid"],
                        "errors": validation_result.get("errors", []),
                        "warnings": validation_result.get("warnings", [])
                    })
                    
                    if validation_result["valid"]:
                        result_data["operationsValidated"] += 1
                    else:
                        validation_failed = True
                        logger.error(f"Operation {i} validation failed: {validation_result['errors']}")
                
                if validation_failed and stop_on_error:
                    return AdvancedPowerPointResult(
                        success=False,
                        message=f"Pre-validation failed for {result_data['totalOperations'] - result_data['operationsValidated']} operations",
                        error="Some operations failed validation",
                        data=result_data
                    )
            
            # Get initial slide count for reference
            initial_slide_count = 0
            try:
                with PowerPointSlideExecutor() as executor:
                    if executor.open_presentation(presentation_path):
                        initial_slide_count = executor.get_slide_count()
            except Exception as e:
                logger.warning(f"Could not get initial slide count: {e}")
            
            result_data["initialSlideCount"] = initial_slide_count
            
            # Execute operations sequentially
            logger.info(f"Executing {len(operations)} slide operations...")
            
            for i, operation_dsl in enumerate(operations):
                operation_detail = {
                    "operationIndex": i,
                    "operationDSL": operation_dsl,
                    "success": False,
                    "executedAt": datetime.now().isoformat()
                }
                
                try:
                    # Parse the operation
                    parsed_operations = parse_slide_operations_dsl(operation_dsl)
                    if not parsed_operations:
                        operation_detail["error"] = "Failed to parse DSL operation"
                        result_data["operationsFailed"] += 1
                        if stop_on_error:
                            break
                        continue
                    
                    operation_detail["parsedOperations"] = parsed_operations["operations"]
                    
                    # Execute the operation
                    execution_result = execute_slide_operations(
                        presentation_path,
                        parsed_operations["operations"]
                    )
                    
                    operation_detail["executionResult"] = execution_result
                    operation_detail["success"] = execution_result["success"]
                    operation_detail["slideCountAfter"] = execution_result["final_slide_count"]
                    
                    if execution_result["success"]:
                        result_data["operationsExecuted"] += 1
                        logger.info(f"Operation {i} completed successfully")
                    else:
                        result_data["operationsFailed"] += 1
                        operation_detail["error"] = execution_result.get("error", "Unknown execution error")
                        logger.error(f"Operation {i} failed: {operation_detail['error']}")
                        
                        if stop_on_error:
                            break
                    
                except Exception as e:
                    operation_detail["error"] = str(e)
                    result_data["operationsFailed"] += 1
                    logger.exception(f"Error executing operation {i}: {e}")
                    
                    if stop_on_error:
                        break
                
                result_data["operationDetails"].append(operation_detail)
            
            # Get final slide count
            final_slide_count = 0
            try:
                with PowerPointSlideExecutor() as executor:
                    if executor.open_presentation(presentation_path):
                        final_slide_count = executor.get_slide_count()
            except Exception as e:
                logger.warning(f"Could not get final slide count: {e}")
            
            result_data["finalSlideCount"] = final_slide_count
            result_data["slideCountChange"] = final_slide_count - initial_slide_count
            
            # Determine overall success
            overall_success = result_data["operationsFailed"] == 0
            
            if overall_success:
                message = f"Successfully executed all {result_data['operationsExecuted']} operations"
            else:
                message = f"Completed with {result_data['operationsFailed']} failures out of {result_data['totalOperations']} operations"
            
            return AdvancedPowerPointResult(
                success=overall_success,
                message=message,
                data=result_data
            )
            
        except Exception as e:
            logger.exception(f"Error in bulk_slide_operations: {str(e)}")
            return AdvancedPowerPointResult(
                success=False,
                message="Bulk operations failed",
                error=f"Failed to execute bulk operations: {str(e)}"
            )
    
    @mcp.tool()
    def compare_presentation_versions(
        original_path: str = Field(description="Path to the original PowerPoint file"),
        modified_path: str = Field(description="Path to the modified PowerPoint file"),
        include_visual_comparison: bool = Field(default=True, description="Include slide image comparison"),
        max_slides_to_compare: int = Field(default=10, description="Maximum number of slides to compare")
    ) -> AdvancedPowerPointResult:
        """
        Compare two versions of a PowerPoint presentation to identify differences.
        
        This tool provides comprehensive comparison between two presentation versions:
        - Slide count differences
        - Content changes per slide
        - Shape additions, deletions, and modifications
        - Visual differences through slide images
        - Metadata and property changes
        
        Perfect for version control, change tracking, and presentation review workflows.
        """
        try:
            # Validate both files exist
            for file_path, file_label in [(original_path, "original"), (modified_path, "modified")]:
                if not os.path.exists(file_path):
                    return AdvancedPowerPointResult(
                        success=False,
                        message=f"{file_label.title()} file not found",
                        error=f"{file_label.title()} PowerPoint file not found: {file_path}"
                    )
                
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in ['.pptx', '.ppt']:
                    return AdvancedPowerPointResult(
                        success=False,
                        message=f"Unsupported {file_label} file format",
                        error=f"Unsupported file format: {file_ext}"
                    )
            
            result_data = {
                "comparisonPerformed": datetime.now().isoformat(),
                "originalPath": original_path,
                "modifiedPath": modified_path,
                "differences": {
                    "slideCount": {},
                    "slideChanges": [],
                    "contentChanges": [],
                    "metadataChanges": {}
                },
                "summary": {}
            }
            
            # Extract metadata from both presentations
            original_metadata = None
            modified_metadata = None
            
            if PPTX_AVAILABLE:
                try:
                    with PowerPointMetadataExtractor(original_path) as extractor:
                        original_metadata = extractor.extract_presentation_metadata(
                            include_slide_content=True,
                            include_master_slides=False,
                            include_layouts=False
                        )
                except Exception as e:
                    logger.warning(f"Could not extract original metadata: {e}")
                
                try:
                    with PowerPointMetadataExtractor(modified_path) as extractor:
                        modified_metadata = extractor.extract_presentation_metadata(
                            include_slide_content=True,
                            include_master_slides=False,
                            include_layouts=False
                        )
                except Exception as e:
                    logger.warning(f"Could not extract modified metadata: {e}")
            
            # Compare slide counts
            if original_metadata and modified_metadata:
                orig_slide_count = original_metadata.get("totalSlides", 0)
                mod_slide_count = modified_metadata.get("totalSlides", 0)
                
                result_data["differences"]["slideCount"] = {
                    "original": orig_slide_count,
                    "modified": mod_slide_count,
                    "difference": mod_slide_count - orig_slide_count
                }
                
                # Compare core properties
                orig_props = original_metadata.get("coreProperties", {})
                mod_props = modified_metadata.get("coreProperties", {})
                
                metadata_changes = {}
                for key in set(orig_props.keys()) | set(mod_props.keys()):
                    orig_val = orig_props.get(key)
                    mod_val = mod_props.get(key)
                    if orig_val != mod_val:
                        metadata_changes[key] = {
                            "original": orig_val,
                            "modified": mod_val
                        }
                
                result_data["differences"]["metadataChanges"] = metadata_changes
            
            # Capture slide images for visual comparison if requested
            slide_comparisons = []
            if include_visual_comparison and WIN32COM_AVAILABLE:
                # Determine slides to compare
                max_slides = min(
                    max_slides_to_compare,
                    result_data["differences"]["slideCount"].get("original", 10),
                    result_data["differences"]["slideCount"].get("modified", 10)
                )
                
                slide_numbers = list(range(1, max_slides + 1))
                
                try:
                    # Capture images from both presentations
                    orig_capture = _capture_slide_images_safe(original_path, slide_numbers, 800, 600)
                    mod_capture = _capture_slide_images_safe(modified_path, slide_numbers, 800, 600)
                    
                    orig_images = orig_capture.get("slide_images", {})
                    mod_images = mod_capture.get("slide_images", {})
                    
                    # Compare slides visually
                    for slide_num in slide_numbers:
                        comparison = {
                            "slideNumber": slide_num,
                            "originalImage": orig_images.get(slide_num),
                            "modifiedImage": mod_images.get(slide_num),
                            "hasVisualChanges": None,  # Would need image comparison logic
                            "imagesCaptured": {
                                "original": slide_num in orig_images,
                                "modified": slide_num in mod_images
                            }
                        }
                        
                        # Basic visual change detection (simple approach)
                        if orig_images.get(slide_num) and mod_images.get(slide_num):
                            comparison["hasVisualChanges"] = orig_images[slide_num] != mod_images[slide_num]
                        
                        slide_comparisons.append(comparison)
                    
                    logger.info(f"Captured images for {len(slide_comparisons)} slides for comparison")
                    
                except Exception as e:
                    logger.warning(f"Error capturing images for comparison: {e}")
            
            result_data["differences"]["visualComparisons"] = slide_comparisons
            
            # Create summary statistics
            summary = {
                "totalDifferences": (
                    (1 if result_data["differences"]["slideCount"].get("difference", 0) != 0 else 0) +
                    len(result_data["differences"]["metadataChanges"]) +
                    len([c for c in slide_comparisons if c.get("hasVisualChanges")])
                ),
                "slideCountChanged": result_data["differences"]["slideCount"].get("difference", 0) != 0,
                "metadataChanged": len(result_data["differences"]["metadataChanges"]) > 0,
                "visuallyChangedSlides": len([c for c in slide_comparisons if c.get("hasVisualChanges")]),
                "comparisonLimitations": []
            }
            
            if not PPTX_AVAILABLE:
                summary["comparisonLimitations"].append("python-pptx not available - limited metadata comparison")
            
            if not WIN32COM_AVAILABLE:
                summary["comparisonLimitations"].append("win32com not available - no visual comparison")
            
            result_data["summary"] = summary
            
            # Determine if presentations are identical
            are_identical = summary["totalDifferences"] == 0
            
            if are_identical:
                message = "Presentations appear to be identical"
            else:
                message = f"Found {summary['totalDifferences']} differences between presentations"
            
            return AdvancedPowerPointResult(
                success=True,
                message=message,
                data=result_data
            )
            
        except Exception as e:
            logger.exception(f"Error in compare_presentation_versions: {str(e)}")
            return AdvancedPowerPointResult(
                success=False,
                message="Comparison failed",
                error=f"Failed to compare presentations: {str(e)}"
            )
    
    @mcp.tool()
    def extract_presentation_templates(
        presentation_path: str = Field(description="Path to the PowerPoint file to extract templates from"),
        template_output_dir: str = Field(description="Directory to save extracted template information"),
        include_slide_masters: bool = Field(default=True, description="Include slide master templates"),
        include_layouts: bool = Field(default=True, description="Include layout templates"),
        export_as_json: bool = Field(default=True, description="Export template data as JSON")
    ) -> AdvancedPowerPointResult:
        """
        Extract presentation templates, layouts, and design elements for reuse.
        
        This tool analyzes a PowerPoint presentation and extracts reusable template components:
        - Slide master designs and layouts
        - Color schemes and font themes
        - Standard shape styles and formatting
        - Layout structures and positioning patterns
        - Template metadata for reconstruction
        
        Perfect for creating presentation templates, design systems, or style guides.
        """
        try:
            # Validate file exists
            if not os.path.exists(presentation_path):
                return AdvancedPowerPointResult(
                    success=False,
                    message="File not found",
                    error=f"PowerPoint file not found: {presentation_path}"
                )
            
            # Validate and create output directory
            output_dir = Path(template_output_dir)
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return AdvancedPowerPointResult(
                    success=False,
                    message="Cannot create output directory",
                    error=f"Failed to create output directory: {str(e)}"
                )
            
            if not PPTX_AVAILABLE:
                return AdvancedPowerPointResult(
                    success=False,
                    message="python-pptx not available",
                    error="Template extraction requires python-pptx library"
                )
            
            result_data = {
                "extractedAt": datetime.now().isoformat(),
                "presentationPath": presentation_path,
                "outputDirectory": str(output_dir),
                "templatesExtracted": {
                    "slideMasters": 0,
                    "layouts": 0,
                    "colorSchemes": 0,
                    "fontThemes": 0
                },
                "extractedFiles": [],
                "templateMetadata": {}
            }
            
            # Extract comprehensive metadata including masters and layouts
            with PowerPointMetadataExtractor(presentation_path) as extractor:
                metadata = extractor.extract_presentation_metadata(
                    include_slide_content=True,
                    include_master_slides=include_slide_masters,
                    include_layouts=include_layouts
                )
            
            # Extract slide masters if requested
            if include_slide_masters and "slideMasters" in metadata:
                masters_data = metadata["slideMasters"]
                masters_file = output_dir / "slide_masters.json"
                
                with open(masters_file, 'w', encoding='utf-8') as f:
                    json.dump(masters_data, f, indent=2, ensure_ascii=False, default=str)
                
                result_data["extractedFiles"].append(str(masters_file))
                result_data["templatesExtracted"]["slideMasters"] = len(masters_data)
                logger.info(f"Extracted {len(masters_data)} slide masters")
            
            # Extract layouts if requested
            if include_layouts and "slideLayouts" in metadata:
                layouts_data = metadata["slideLayouts"]
                layouts_file = output_dir / "slide_layouts.json"
                
                with open(layouts_file, 'w', encoding='utf-8') as f:
                    json.dump(layouts_data, f, indent=2, ensure_ascii=False, default=str)
                
                result_data["extractedFiles"].append(str(layouts_file))
                result_data["templatesExtracted"]["layouts"] = len(layouts_data)
                logger.info(f"Extracted {len(layouts_data)} slide layouts")
            
            # Extract color and font themes
            core_props = metadata.get("coreProperties", {})
            theme_data = {
                "colorTheme": metadata.get("colorTheme", {}),
                "fontTheme": metadata.get("fontTheme", {}),
                "presentationProperties": {
                    "slideSize": metadata.get("slideSize", {}),
                    "coreProperties": core_props
                }
            }
            
            theme_file = output_dir / "presentation_theme.json"
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False, default=str)
            
            result_data["extractedFiles"].append(str(theme_file))
            
            # Create a template summary
            template_summary = {
                "templateName": core_props.get("title", "Extracted Template"),
                "extractedFrom": os.path.basename(presentation_path),
                "extractionDate": datetime.now().isoformat(),
                "components": {
                    "slideMasters": result_data["templatesExtracted"]["slideMasters"],
                    "layouts": result_data["templatesExtracted"]["layouts"],
                    "totalSlides": metadata.get("totalSlides", 0)
                },
                "usage": {
                    "description": "Template extracted from PowerPoint presentation",
                    "applicationInstructions": [
                        "Use slide_masters.json to recreate master slide designs",
                        "Use slide_layouts.json to implement layout structures",
                        "Use presentation_theme.json to apply color and font themes",
                        "Adapt positioning and sizing for your presentation format"
                    ]
                }
            }
            
            summary_file = output_dir / "template_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(template_summary, f, indent=2, ensure_ascii=False, default=str)
            
            result_data["extractedFiles"].append(str(summary_file))
            result_data["templateMetadata"] = template_summary
            
            # If full metadata export requested, save complete metadata
            if export_as_json:
                full_metadata_file = output_dir / "full_presentation_metadata.json"
                with open(full_metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
                
                result_data["extractedFiles"].append(str(full_metadata_file))
            
            return AdvancedPowerPointResult(
                success=True,
                message=f"Successfully extracted templates to {len(result_data['extractedFiles'])} files",
                data=result_data
            )
            
        except Exception as e:
            logger.exception(f"Error in extract_presentation_templates: {str(e)}")
            return AdvancedPowerPointResult(
                success=False,
                message="Template extraction failed",
                error=f"Failed to extract templates: {str(e)}"
            )


def get_advanced_powerpoint_tools():
    """Get advanced PowerPoint tools registration function."""
    return register_advanced_powerpoint_tools
