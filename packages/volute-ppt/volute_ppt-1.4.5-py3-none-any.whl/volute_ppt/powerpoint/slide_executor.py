"""
PowerPoint Slide Executor Module

This module handles execution of slide management operations like add, delete, move, and duplicate.
It uses Windows COM automation via win32com to manipulate PowerPoint presentations.
"""

import os
import logging
import pythoncom
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)

# Check for win32com availability
WIN32COM_AVAILABLE = False
try:
    import win32com.client
    WIN32COM_AVAILABLE = True
    logger.info("win32com available for PowerPoint slide operations")
except ImportError as e:
    logger.warning(f"win32com not available: {e}")

class PowerPointSlideExecutor:
    """
    Executes PowerPoint slide management operations using COM automation.
    """
    
    def __init__(self):
        self.app = None
        self.presentation = None
        self.presentation_path = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
    
    def open_presentation(self, file_path: str) -> bool:
        """
        Open a PowerPoint presentation for editing.
        
        Args:
            file_path: Path to the PowerPoint file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not WIN32COM_AVAILABLE:
                logger.error("win32com not available for PowerPoint operations")
                return False
            
            # Validate file exists
            if not os.path.exists(file_path):
                logger.error(f"PowerPoint file not found: {file_path}")
                return False
            
            # Check file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in ['.pptx', '.ppt']:
                logger.error(f"Unsupported file format: {file_ext}")
                return False
            
            # Initialize COM
            pythoncom.CoInitialize()
            
            # Create PowerPoint application
            self.app = win32com.client.Dispatch("PowerPoint.Application")
            self.app.Visible = True
            
            # Open presentation
            abs_path = os.path.abspath(file_path)
            self.presentation = self.app.Presentations.Open(abs_path)
            self.presentation_path = abs_path
            
            logger.info(f"Opened PowerPoint presentation: {file_path}")
            logger.info(f"Presentation has {self.presentation.Slides.Count} slides")
            
            return True
            
        except Exception as e:
            logger.error(f"Error opening PowerPoint presentation: {e}")
            self.cleanup()
            return False
    
    def get_slide_count(self) -> int:
        """
        Get the current number of slides in the presentation.
        
        Returns:
            Number of slides, or 0 if error
        """
        try:
            if self.presentation:
                return self.presentation.Slides.Count
            return 0
        except Exception as e:
            logger.error(f"Error getting slide count: {e}")
            return 0
    
    def add_slide(self, position: int, layout: Optional[str] = None) -> bool:
        """
        Add a new slide at the specified position.
        
        Args:
            position: Position to insert slide (1-based), or -1 for end
            layout: Optional layout name (e.g., "Title Slide", "Blank")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.presentation:
                logger.error("No presentation open")
                return False
            
            # Handle "end" position
            if position == -1:
                position = self.presentation.Slides.Count + 1
            
            # Validate position
            if position < 1 or position > self.presentation.Slides.Count + 1:
                logger.error(f"Invalid slide position: {position}")
                return False
            
            # Get slide layout
            slide_layout = self._get_slide_layout(layout)
            if slide_layout is None:
                logger.error(f"Could not get slide layout: {layout}")
                return False
            
            # Add the slide
            new_slide = self.presentation.Slides.AddSlide(position, slide_layout)
            
            logger.info(f"Added slide at position {position} with layout '{layout or 'default'}'")
            return True
            
        except Exception as e:
            logger.error(f"Error adding slide: {e}")
            return False
    
    def delete_slide(self, slide_number: int) -> bool:
        """
        Delete a slide by its number.
        
        Args:
            slide_number: Slide number to delete (1-based)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.presentation:
                logger.error("No presentation open")
                return False
            
            # Validate slide number
            if slide_number < 1 or slide_number > self.presentation.Slides.Count:
                logger.error(f"Invalid slide number: {slide_number}")
                return False
            
            # Delete the slide
            slide = self.presentation.Slides(slide_number)
            slide.Delete()
            
            logger.info(f"Deleted slide {slide_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting slide {slide_number}: {e}")
            return False
    
    def move_slide(self, from_position: int, to_position: int) -> bool:
        """
        Move a slide from one position to another.
        
        Args:
            from_position: Current slide position (1-based)
            to_position: Target slide position (1-based)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.presentation:
                logger.error("No presentation open")
                return False
            
            slide_count = self.presentation.Slides.Count
            
            # Validate positions
            if from_position < 1 or from_position > slide_count:
                logger.error(f"Invalid source position: {from_position}")
                return False
            
            if to_position < 1 or to_position > slide_count:
                logger.error(f"Invalid target position: {to_position}")
                return False
            
            if from_position == to_position:
                logger.info(f"Slide {from_position} is already at target position")
                return True
            
            # Move the slide using Cut and Paste
            slide = self.presentation.Slides(from_position)
            slide.Cut()
            
            # Adjust target position if moving backwards
            if to_position > from_position:
                to_position -= 1
            
            # Insert at target position
            if to_position <= 1:
                # Insert at beginning
                self.presentation.Slides.Paste(1)
            elif to_position >= slide_count:
                # Insert at end
                self.presentation.Slides.Paste(slide_count)
            else:
                # Insert at specific position
                self.presentation.Slides.Paste(to_position)
            
            logger.info(f"Moved slide from position {from_position} to {to_position}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving slide: {e}")
            return False
    
    def duplicate_slide(self, source_slide: int, position: int = -1) -> bool:
        """
        Duplicate a slide and place it at the specified position.
        
        Args:
            source_slide: Slide number to duplicate (1-based)
            position: Position to insert duplicate (1-based), or -1 for end
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.presentation:
                logger.error("No presentation open")
                return False
            
            slide_count = self.presentation.Slides.Count
            
            # Validate source slide
            if source_slide < 1 or source_slide > slide_count:
                logger.error(f"Invalid source slide number: {source_slide}")
                return False
            
            # Handle "end" position
            if position == -1:
                position = slide_count + 1
            
            # Validate target position
            if position < 1 or position > slide_count + 1:
                logger.error(f"Invalid target position: {position}")
                return False
            
            # Duplicate using PowerPoint's built-in Duplicate method
            source_slide_obj = self.presentation.Slides(source_slide)
            duplicated_slides = source_slide_obj.Duplicate()
            
            # The duplicated slide is initially placed after the source
            # If we need it elsewhere, move it
            duplicated_slide = duplicated_slides[0]  # Get the first (and only) duplicated slide
            current_position = duplicated_slide.SlideIndex
            
            if current_position != position:
                # Move to desired position
                self.move_slide(current_position, position)
            
            logger.info(f"Duplicated slide {source_slide} to position {position}")
            return True
            
        except Exception as e:
            logger.error(f"Error duplicating slide: {e}")
            return False
    
    def _get_slide_layout(self, layout_name: Optional[str]):
        """
        Get a slide layout by name.
        
        Args:
            layout_name: Name of the layout or None for default
            
        Returns:
            PowerPoint slide layout object or None if not found
        """
        try:
            if not self.presentation:
                return None
            
            # Get slide master
            slide_master = self.presentation.SlideMaster
            layouts = slide_master.CustomLayouts
            
            if not layout_name:
                # Return first layout (default)
                return layouts(1)
            
            # Try to find layout by name
            layout_name_lower = layout_name.lower()
            
            # Common layout name mappings
            layout_mappings = {
                'title slide': 'Title Slide',
                'title and content': 'Title and Content',
                'section header': 'Section Header',
                'two content': 'Two Content',
                'comparison': 'Comparison',
                'title only': 'Title Only',
                'blank': 'Blank',
                'content with caption': 'Content with Caption',
                'picture with caption': 'Picture with Caption'
            }
            
            # Check mapping first
            mapped_name = layout_mappings.get(layout_name_lower)
            if mapped_name:
                layout_name = mapped_name
            
            # Search for exact match
            for i in range(1, layouts.Count + 1):
                layout = layouts(i)
                if hasattr(layout, 'Name') and layout.Name.lower() == layout_name_lower:
                    logger.debug(f"Found layout '{layout.Name}' at index {i}")
                    return layout
            
            # If not found, try partial match
            for i in range(1, layouts.Count + 1):
                layout = layouts(i)
                if hasattr(layout, 'Name') and layout_name_lower in layout.Name.lower():
                    logger.debug(f"Found partial match layout '{layout.Name}' for '{layout_name}'")
                    return layout
            
            # Log available layouts for debugging
            available_layouts = []
            for i in range(1, layouts.Count + 1):
                layout = layouts(i)
                layout_name_str = getattr(layout, 'Name', f'Layout_{i}')
                available_layouts.append(f"{i}: {layout_name_str}")
            
            logger.warning(f"Layout '{layout_name}' not found. Available: {', '.join(available_layouts)}")
            
            # Return first layout as fallback
            return layouts(1)
            
        except Exception as e:
            logger.error(f"Error getting slide layout: {e}")
            return None
    
    def save_presentation(self) -> bool:
        """
        Save the current presentation.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.presentation:
                logger.error("No presentation open")
                return False
            
            self.presentation.Save()
            logger.info("Presentation saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving presentation: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up COM resources."""
        try:
            if self.presentation:
                try:
                    # Save before closing
                    self.presentation.Save()
                    logger.debug("Presentation saved during cleanup")
                except Exception as save_error:
                    logger.warning(f"Could not save presentation during cleanup: {save_error}")
                
                try:
                    # Don't close the presentation - let user decide
                    # self.presentation.Close()
                    logger.debug("Presentation kept open for user")
                except Exception as close_error:
                    logger.warning(f"Could not close presentation: {close_error}")
            
            if self.app:
                try:
                    # Don't quit PowerPoint application - let user decide
                    # self.app.Quit()
                    logger.debug("PowerPoint application kept running")
                except Exception as quit_error:
                    logger.warning(f"Could not quit PowerPoint: {quit_error}")
            
            # Reset instance variables
            self.presentation = None
            self.app = None
            self.presentation_path = None
            
            # Uninitialize COM
            try:
                pythoncom.CoUninitialize()
                logger.debug("COM uninitialized")
            except Exception as com_error:
                logger.warning(f"Could not uninitialize COM: {com_error}")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def execute_slide_operations(file_path: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Execute a list of slide operations on a PowerPoint presentation.
    
    Args:
        file_path: Path to the PowerPoint file
        operations: List of operation dictionaries from parser
        
    Returns:
        Dictionary with execution results
    """
    results = {
        "success": False,
        "operations_executed": 0,
        "operations_failed": 0,
        "details": [],
        "final_slide_count": 0,
        "error": None
    }
    
    try:
        with PowerPointSlideExecutor() as executor:
            # Open presentation
            if not executor.open_presentation(file_path):
                results["error"] = "Could not open PowerPoint presentation"
                return results
            
            initial_slide_count = executor.get_slide_count()
            logger.info(f"Initial slide count: {initial_slide_count}")
            
            # Execute operations in order
            for i, operation in enumerate(operations):
                op_type = operation.get("type")
                params = operation.get("parameters", {})
                
                try:
                    success = False
                    
                    if op_type == "add_slide":
                        success = executor.add_slide(
                            position=params.get("position", -1),
                            layout=params.get("layout")
                        )
                    
                    elif op_type == "delete_slide":
                        success = executor.delete_slide(
                            slide_number=params.get("slide_number")
                        )
                    
                    elif op_type == "move_slide":
                        success = executor.move_slide(
                            from_position=params.get("from"),
                            to_position=params.get("to")
                        )
                    
                    elif op_type == "duplicate_slide":
                        success = executor.duplicate_slide(
                            source_slide=params.get("source"),
                            position=params.get("position", -1)
                        )
                    
                    else:
                        logger.error(f"Unknown operation type: {op_type}")
                        success = False
                    
                    # Record result
                    operation_result = {
                        "operation_index": i,
                        "operation_type": op_type,
                        "parameters": params,
                        "success": success,
                        "slide_count_after": executor.get_slide_count()
                    }
                    
                    results["details"].append(operation_result)
                    
                    if success:
                        results["operations_executed"] += 1
                        logger.info(f"Operation {i+1} ({op_type}) completed successfully")
                    else:
                        results["operations_failed"] += 1
                        logger.error(f"Operation {i+1} ({op_type}) failed")
                
                except Exception as op_error:
                    results["operations_failed"] += 1
                    error_result = {
                        "operation_index": i,
                        "operation_type": op_type,
                        "parameters": params,
                        "success": False,
                        "error": str(op_error),
                        "slide_count_after": executor.get_slide_count()
                    }
                    results["details"].append(error_result)
                    logger.error(f"Operation {i+1} ({op_type}) failed with error: {op_error}")
            
            # Save presentation
            if executor.save_presentation():
                logger.info("Presentation saved successfully")
            else:
                logger.warning("Could not save presentation")
            
            results["final_slide_count"] = executor.get_slide_count()
            results["success"] = results["operations_executed"] > 0
            
            logger.info(f"Slide operations completed: {results['operations_executed']} successful, {results['operations_failed']} failed")
            logger.info(f"Final slide count: {results['final_slide_count']}")
            
    except Exception as e:
        logger.error(f"Error executing slide operations: {e}")
        results["error"] = str(e)
    
    return results
