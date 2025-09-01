"""
PowerPoint Application Singleton Manager

This module provides a singleton PowerPoint application manager that coordinates
access across all MCP tools to prevent file opening conflicts and ensure
proper resource management.
"""

import threading
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Check for win32com availability
WIN32COM_AVAILABLE = False
try:
    import win32com.client
    import pythoncom
    WIN32COM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"win32com not available: {e}")

class PowerPointManager:
    """
    Singleton PowerPoint application manager for coordinating access across MCP tools.
    
    This manager ensures:
    - Single PowerPoint application instance
    - Proper file access coordination
    - Thread-safe operations
    - Resource cleanup
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PowerPointManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.app = None
        self.open_presentations = {}  # filepath -> presentation object
        self.presentation_locks = {}  # filepath -> threading.Lock
        self.app_lock = threading.Lock()
        self._initialized = True
        
        logger.info("PowerPoint Manager initialized")
    
    def _ensure_app(self):
        """Ensure PowerPoint application is available."""
        if not WIN32COM_AVAILABLE:
            raise RuntimeError("win32com not available - cannot manage PowerPoint")
            
        with self.app_lock:
            if self.app is None:
                try:
                    pythoncom.CoInitialize()
                    
                    # Try to get existing PowerPoint application first
                    try:
                        self.app = win32com.client.GetActiveObject("PowerPoint.Application")
                        logger.info("Connected to existing PowerPoint application")
                    except:
                        # Create new PowerPoint application
                        self.app = win32com.client.Dispatch("PowerPoint.Application")
                        logger.info("Created new PowerPoint application")
                    
                    # Make sure PowerPoint is visible
                    self.app.Visible = True
                    
                except Exception as e:
                    logger.error(f"Failed to initialize PowerPoint application: {e}")
                    raise
    
    def get_presentation(self, filepath: str, readonly: bool = False):
        """
        Get or open a PowerPoint presentation with proper coordination.
        
        Args:
            filepath: Path to the PowerPoint file
            readonly: Whether to open in read-only mode
            
        Returns:
            PowerPoint presentation object
        """
        self._ensure_app()
        
        filepath = Path(filepath).resolve().as_posix()
        
        # Get or create lock for this file
        if filepath not in self.presentation_locks:
            self.presentation_locks[filepath] = threading.Lock()
        
        with self.presentation_locks[filepath]:
            # Check if presentation is already open
            if filepath in self.open_presentations:
                presentation = self.open_presentations[filepath]
                
                # Verify the presentation is still valid
                try:
                    _ = presentation.FullName
                    logger.info(f"Reusing existing presentation: {filepath}")
                    return presentation
                except:
                    # Presentation object is stale, remove it
                    del self.open_presentations[filepath]
                    logger.warning(f"Removed stale presentation reference: {filepath}")
            
            # Check if already open in PowerPoint but not tracked
            try:
                for open_pres in self.app.Presentations:
                    open_path = Path(open_pres.FullName).resolve().as_posix()
                    if open_path == filepath:
                        self.open_presentations[filepath] = open_pres
                        logger.info(f"Found untracked open presentation: {filepath}")
                        return open_pres
            except Exception as e:
                logger.warning(f"Could not check open presentations: {e}")
            
            # Open the presentation
            try:
                if not Path(filepath).exists():
                    raise FileNotFoundError(f"PowerPoint file not found: {filepath}")
                
                presentation = self.app.Presentations.Open(filepath, ReadOnly=readonly)
                self.open_presentations[filepath] = presentation
                
                mode = "read-only" if readonly else "read-write"
                logger.info(f"Opened presentation in {mode} mode: {filepath}")
                
                return presentation
                
            except Exception as e:
                logger.error(f"Failed to open presentation {filepath}: {e}")
                raise
    
    def save_presentation(self, filepath: str) -> bool:
        """
        Save a presentation if it's currently open.
        
        Args:
            filepath: Path to the presentation to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        filepath = Path(filepath).resolve().as_posix()
        
        if filepath not in self.open_presentations:
            logger.warning(f"Cannot save - presentation not managed: {filepath}")
            return False
        
        with self.presentation_locks[filepath]:
            try:
                presentation = self.open_presentations[filepath]
                presentation.Save()
                logger.info(f"Saved presentation: {filepath}")
                return True
            except Exception as e:
                logger.error(f"Failed to save presentation {filepath}: {e}")
                return False
    
    def close_presentation(self, filepath: str, save_first: bool = True) -> bool:
        """
        Close a presentation with optional saving.
        
        Args:
            filepath: Path to the presentation to close
            save_first: Whether to save before closing
            
        Returns:
            True if closed successfully, False otherwise
        """
        filepath = Path(filepath).resolve().as_posix()
        
        if filepath not in self.open_presentations:
            logger.info(f"Presentation not managed, nothing to close: {filepath}")
            return True
        
        with self.presentation_locks[filepath]:
            try:
                presentation = self.open_presentations[filepath]
                
                if save_first:
                    try:
                        presentation.Save()
                        logger.info(f"Saved before closing: {filepath}")
                    except Exception as save_error:
                        logger.warning(f"Could not save before closing: {save_error}")
                
                presentation.Close()
                del self.open_presentations[filepath]
                logger.info(f"Closed presentation: {filepath}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to close presentation {filepath}: {e}")
                # Remove from tracking even if close failed
                if filepath in self.open_presentations:
                    del self.open_presentations[filepath]
                return False
    
    def get_slide_count(self, filepath: str) -> int:
        """Get the number of slides in a presentation."""
        try:
            presentation = self.get_presentation(filepath, readonly=True)
            return presentation.Slides.Count
        except Exception as e:
            logger.error(f"Failed to get slide count for {filepath}: {e}")
            return 0
    
    def cleanup(self, quit_app: bool = False):
        """
        Clean up resources.
        
        Args:
            quit_app: Whether to quit the PowerPoint application
        """
        logger.info("Cleaning up PowerPoint Manager resources")
        
        # Close all tracked presentations
        for filepath in list(self.open_presentations.keys()):
            self.close_presentation(filepath, save_first=True)
        
        # Optionally quit PowerPoint
        if quit_app and self.app:
            try:
                self.app.Quit()
                logger.info("Quit PowerPoint application")
            except Exception as e:
                logger.warning(f"Could not quit PowerPoint application: {e}")
        
        # Reset state
        self.app = None
        self.open_presentations.clear()
        self.presentation_locks.clear()
        
        try:
            pythoncom.CoUninitialize()
        except:
            pass

# Global singleton instance
_powerpoint_manager = None

def get_powerpoint_manager() -> PowerPointManager:
    """Get the global PowerPoint manager singleton instance."""
    global _powerpoint_manager
    if _powerpoint_manager is None:
        _powerpoint_manager = PowerPointManager()
    return _powerpoint_manager

def ensure_presentation_available(filepath: str, readonly: bool = False):
    """
    Ensure a PowerPoint presentation is available for operations.
    
    Args:
        filepath: Path to the PowerPoint file
        readonly: Whether to open in read-only mode
        
    Returns:
        PowerPoint presentation object
    """
    manager = get_powerpoint_manager()
    return manager.get_presentation(filepath, readonly=readonly)

def save_if_open(filepath: str) -> bool:
    """Save a presentation if it's currently open and managed."""
    manager = get_powerpoint_manager()
    return manager.save_presentation(filepath)

def get_managed_slide_count(filepath: str) -> int:
    """Get slide count through the manager."""
    manager = get_powerpoint_manager()
    return manager.get_slide_count(filepath)