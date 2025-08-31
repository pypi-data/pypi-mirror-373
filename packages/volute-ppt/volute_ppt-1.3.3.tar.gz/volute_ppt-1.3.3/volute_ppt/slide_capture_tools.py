"""
PowerPoint slide image capture tools for multimodal analysis.
Uses win32com to capture slide images and return them for LLM multimodal processing.
"""

import os
import base64
import hashlib
import tempfile
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

# Check for win32com availability
WIN32COM_AVAILABLE = False
try:
    import win32com.client
    import pythoncom
    WIN32COM_AVAILABLE = True
    logger.info("win32com available for PowerPoint slide capture")
except ImportError as e:
    logger.warning(f"win32com not available: {e}")


class SlideImageCaptureResult(BaseModel):
    """Model for slide image capture results."""
    success: bool = Field(description="Whether the capture was successful")
    message: str = Field(description="Status message")
    slide_images: Dict[int, str] = Field(default_factory=dict, description="Map of slide numbers to base64 image data")
    captured_count: int = Field(default=0, description="Number of slides successfully captured")
    failed_slides: List[int] = Field(default_factory=list, description="List of slide numbers that failed to capture")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional capture metadata")


def register_slide_capture_tools(mcp: FastMCP) -> None:
    """
    Register slide image capture tools with the FastMCP server.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    
    @mcp.tool()
    def capture_powerpoint_slides(
        presentation_path: str = Field(description="Path to the PowerPoint file (.pptx, .ppt)"),
        slide_numbers: List[int] = Field(description="Array of slide numbers to capture (1-based indexing)"),
        image_width: int = Field(default=1024, description="Width of captured images in pixels"),
        image_height: int = Field(default=768, description="Height of captured images in pixels"),
        include_metadata: bool = Field(default=True, description="Include capture metadata in response")
    ) -> SlideImageCaptureResult:
        """
        Capture PowerPoint slide images for multimodal LLM analysis.
        
        This tool uses Windows COM automation to:
        - Open PowerPoint presentations
        - Export specific slides as PNG images
        - Return base64-encoded images for multimodal analysis
        - Handle PowerPoint application lifecycle safely
        - Provide comprehensive error handling and guardrails
        
        Perfect for agents that need visual analysis of slide content!
        """
        try:
            # Validate environment and requirements
            if not WIN32COM_AVAILABLE:
                return SlideImageCaptureResult(
                    success=False,
                    message="COM automation not available",
                    error="win32com library is required but not available. Install with: pip install pywin32"
                )
            
            # Validate file exists
            if not os.path.exists(presentation_path):
                return SlideImageCaptureResult(
                    success=False,
                    message="File not found",
                    error=f"PowerPoint file not found: {presentation_path}"
                )
            
            # Check file extension
            file_ext = os.path.splitext(presentation_path)[1].lower()
            if file_ext not in ['.pptx', '.ppt']:
                return SlideImageCaptureResult(
                    success=False,
                    message="Unsupported file format",
                    error=f"Unsupported file format: {file_ext}. Only .pptx and .ppt files are supported."
                )
            
            # Validate slide numbers
            if not slide_numbers:
                return SlideImageCaptureResult(
                    success=False,
                    message="No slides specified",
                    error="At least one slide number must be specified"
                )
            
            # Limit slide capture to prevent resource exhaustion
            if len(slide_numbers) > 20:
                return SlideImageCaptureResult(
                    success=False,
                    message="Too many slides requested",
                    error=f"Maximum 20 slides can be captured at once. Requested: {len(slide_numbers)}"
                )
            
            # Validate image dimensions
            if image_width < 100 or image_width > 2048 or image_height < 100 or image_height > 2048:
                return SlideImageCaptureResult(
                    success=False,
                    message="Invalid image dimensions",
                    error="Image dimensions must be between 100 and 2048 pixels"
                )
            
            # Perform slide image capture
            result = _capture_slide_images_safe(
                presentation_path, 
                slide_numbers, 
                image_width, 
                image_height
            )
            
            # Add metadata if requested
            metadata = None
            if include_metadata:
                metadata = {
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
            
            return SlideImageCaptureResult(
                success=result["success"],
                message=result["message"],
                slide_images=result["slide_images"],
                captured_count=len(result["slide_images"]),
                failed_slides=result["failed_slides"],
                error=result.get("error"),
                metadata=metadata
            )
            
        except Exception as e:
            logger.exception(f"Error in slide image capture: {str(e)}")
            return SlideImageCaptureResult(
                success=False,
                message="Capture failed with exception",
                error=f"Unexpected error during slide capture: {str(e)}"
            )
    
    @mcp.tool()
    def get_slide_capture_capabilities() -> Dict[str, Any]:
        """
        Get information about slide capture capabilities and requirements.
        
        Returns system capabilities for PowerPoint slide image capture.
        """
        try:
            capabilities = {
                "com_available": WIN32COM_AVAILABLE,
                "supported_formats": [".pptx", ".ppt"],
                "max_slides_per_request": 20,
                "supported_image_format": "PNG",
                "min_image_size": {"width": 100, "height": 100},
                "max_image_size": {"width": 2048, "height": 2048},
                "default_image_size": {"width": 1024, "height": 768},
                "multimodal_ready": True,
                "base64_encoded": True,
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
                        capabilities["status"] = "Ready for slide capture"
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
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "Error checking capabilities"
            }


def _capture_slide_images_safe(
    presentation_path: str, 
    slide_numbers: List[int],
    image_width: int = 1024,
    image_height: int = 768
) -> Dict[str, Any]:
    """
    Safely capture PowerPoint slide images with comprehensive error handling.
    
    Args:
        presentation_path: Path to PowerPoint file
        slide_numbers: List of slide numbers to capture
        image_width: Width in pixels for captured images
        image_height: Height in pixels for captured images
        
    Returns:
        Dictionary with capture results and any errors
    """
    slide_images = {}
    failed_slides = []
    ppt_app = None
    presentation = None
    app_was_running = False
    presentation_was_open = False
    
    try:
        # Initialize COM
        pythoncom.CoInitialize()
        logger.info("Initialized COM for PowerPoint automation")
        
        # Try to get existing PowerPoint application first
        try:
            ppt_app = win32com.client.GetActiveObject("PowerPoint.Application")
            app_was_running = True
            logger.info("Found existing PowerPoint application instance")
        except:
            # No existing PowerPoint application, create a new one
            ppt_app = win32com.client.Dispatch("PowerPoint.Application")
            app_was_running = False
            logger.info("Created new PowerPoint application instance")
        
        # PowerPoint must be visible for image export to work properly
        if not app_was_running:
            ppt_app.Visible = True
        
        # Check if presentation is already open
        presentation = None
        presentation_path_normalized = os.path.normpath(presentation_path).lower()
        
        try:
            for open_presentation in ppt_app.Presentations:
                open_path_normalized = os.path.normpath(open_presentation.FullName).lower()
                if open_path_normalized == presentation_path_normalized:
                    presentation = open_presentation
                    presentation_was_open = True
                    logger.info(f"Found already open presentation: {presentation_path}")
                    break
        except Exception as e:
            logger.warning(f"Could not check open presentations: {e}")
        
        # Open presentation if not already open
        if presentation is None:
            presentation = ppt_app.Presentations.Open(presentation_path, ReadOnly=True)
            presentation_was_open = False
            logger.info(f"Opened presentation: {presentation_path}")
        
        # Create temporary directory for images
        temp_dir = Path(tempfile.gettempdir()) / "volutemcp_slides"
        temp_dir.mkdir(exist_ok=True)
        
        logger.info(f"Capturing {len(slide_numbers)} slides at {image_width}x{image_height}")
        
        # Capture each requested slide
        total_slides = presentation.Slides.Count
        
        for slide_num in slide_numbers:
            try:
                # Validate slide number
                if slide_num < 1 or slide_num > total_slides:
                    logger.warning(f"Slide {slide_num} out of range (1-{total_slides})")
                    failed_slides.append(slide_num)
                    continue
                
                slide = presentation.Slides(slide_num)
                
                # Generate unique filename for the slide image
                file_hash = hashlib.md5(presentation_path.encode()).hexdigest()[:8]
                timestamp = datetime.now().strftime("%H%M%S")
                image_filename = f"slide_{slide_num}_{file_hash}_{timestamp}.png"
                image_path = temp_dir / image_filename
                
                # Export slide as PNG image
                slide.Export(str(image_path), "PNG", image_width, image_height)
                
                # Read and encode image as base64
                if image_path.exists():
                    with open(image_path, 'rb') as img_file:
                        img_data = img_file.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                        # Format as data URL for multimodal LLM compatibility
                        data_url = f"data:image/png;base64,{img_base64}"
                        slide_images[slide_num] = data_url
                    
                    # Clean up temporary file
                    try:
                        image_path.unlink()
                    except:
                        pass
                    
                    logger.info(f"Successfully captured slide {slide_num}")
                else:
                    logger.error(f"Failed to create image file for slide {slide_num}")
                    failed_slides.append(slide_num)
                    
            except Exception as e:
                logger.error(f"Error capturing slide {slide_num}: {str(e)}")
                failed_slides.append(slide_num)
        
        # Clean up resources (only if we opened them)
        if presentation and not presentation_was_open:
            presentation.Close()
            logger.info("Closed presentation")
        
        if ppt_app and not app_was_running:
            ppt_app.Quit()
            logger.info("Quit PowerPoint application")
        
        # Prepare result
        captured_count = len(slide_images)
        total_requested = len(slide_numbers)
        
        if captured_count == 0:
            return {
                "success": False,
                "message": f"Failed to capture any slides",
                "slide_images": {},
                "failed_slides": failed_slides,
                "error": "No slides were successfully captured"
            }
        elif failed_slides:
            return {
                "success": True,
                "message": f"Captured {captured_count}/{total_requested} slides with some failures",
                "slide_images": slide_images,
                "failed_slides": failed_slides
            }
        else:
            return {
                "success": True,
                "message": f"Successfully captured all {captured_count} requested slides",
                "slide_images": slide_images,
                "failed_slides": []
            }
            
    except Exception as e:
        logger.error(f"Critical error in slide image capture: {str(e)}")
        
        # Emergency cleanup
        try:
            if presentation and not presentation_was_open:
                presentation.Close()
            if ppt_app and not app_was_running:
                ppt_app.Quit()
        except:
            pass
        
        return {
            "success": False,
            "message": "Slide capture failed with critical error",
            "slide_images": slide_images,  # Return any slides that were captured before error
            "failed_slides": failed_slides,
            "error": str(e)
        }
    
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass


def capture_single_slide_after_operation(
    presentation_path: str,
    slide_number: int,
    image_width: int = 1024,
    image_height: int = 768
) -> Optional[str]:
    """
    Capture a single slide image after an operation for verification.
    
    This is a simplified version of the main capture function optimized
    for integration with editing tools to provide visual feedback.
    
    Args:
        presentation_path: Path to the PowerPoint file
        slide_number: Slide number to capture (1-based)
        image_width: Width of captured image in pixels
        image_height: Height of captured image in pixels
        
    Returns:
        Base64-encoded image data URL or None if capture failed
    """
    if not WIN32COM_AVAILABLE:
        logger.warning("Cannot capture slide: win32com not available")
        return None
    
    if not os.path.exists(presentation_path):
        logger.warning(f"Cannot capture slide: file not found - {presentation_path}")
        return None
    
    try:
        # Use the existing capture function for a single slide
        result = _capture_slide_images_safe(
            presentation_path, 
            [slide_number], 
            image_width, 
            image_height
        )
        
        if result["success"] and slide_number in result["slide_images"]:
            return result["slide_images"][slide_number]
        else:
            logger.warning(f"Failed to capture slide {slide_number}: {result.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        logger.error(f"Error capturing slide {slide_number}: {str(e)}")
        return None


def get_slide_capture_tools():
    """Get slide capture tools registration function."""
    return register_slide_capture_tools
