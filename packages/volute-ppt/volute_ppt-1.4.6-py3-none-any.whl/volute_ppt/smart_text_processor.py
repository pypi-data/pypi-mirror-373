"""
Smart Text Processing Module for PowerPoint

This module provides intelligent text processing capabilities including:
- Newline handling (existing functionality)
- Bullet detection and conversion to native PowerPoint bullets
- List formatting and indentation management
- Smart paragraph structure parsing
"""

import re
import logging
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BulletType(Enum):
    """Enumeration of PowerPoint bullet types."""
    FILLED_CIRCLE = 1      # • (default)
    OPEN_CIRCLE = 2        # ○
    SQUARE = 3             # ■
    DIAMOND = 4            # ◆
    ARROW = 5              # ►
    CHECKMARK = 6          # ✓
    DASH = 7               # -
    NUMBER = 8             # 1. 2. 3.
    LETTER = 9             # a. b. c.
    ROMAN = 10             # i. ii. iii.

@dataclass
class BulletInfo:
    """Information about a detected bullet point."""
    original_text: str
    clean_text: str
    bullet_type: BulletType
    indent_level: int
    line_number: int

@dataclass
class TextStructure:
    """Parsed text structure with bullets and formatting."""
    paragraphs: List[str]
    bullets: List[BulletInfo]
    has_bullets: bool
    original_text: str
    processed_text: str

class SmartTextProcessor:
    """Smart text processor with bullet detection and PowerPoint integration."""
    
    # Bullet pattern definitions
    BULLET_PATTERNS = {
        BulletType.FILLED_CIRCLE: [r'^(\s*)•\s+(.+)$', r'^(\s*)●\s+(.+)$'],
        BulletType.OPEN_CIRCLE: [r'^(\s*)○\s+(.+)$', r'^(\s*)◯\s+(.+)$'],
        BulletType.SQUARE: [r'^(\s*)■\s+(.+)$', r'^(\s*)□\s+(.+)$', r'^(\s*)▪\s+(.+)$'],
        BulletType.DIAMOND: [r'^(\s*)◆\s+(.+)$', r'^(\s*)◇\s+(.+)$', r'^(\s*)♦\s+(.+)$'],
        BulletType.ARROW: [r'^(\s*)►\s+(.+)$', r'^(\s*)→\s+(.+)$', r'^(\s*)➤\s+(.+)$'],
        BulletType.CHECKMARK: [r'^(\s*)✓\s+(.+)$', r'^(\s*)✔\s+(.+)$', r'^(\s*)☑\s+(.+)$'],
        BulletType.DASH: [r'^(\s*)-\s+(.+)$', r'^(\s*)–\s+(.+)$', r'^(\s*)—\s+(.+)$'],
        BulletType.NUMBER: [r'^(\s*)(\d+)\.\s+(.+)$'],
        BulletType.LETTER: [r'^(\s*)([a-zA-Z])\.\s+(.+)$'],
        BulletType.ROMAN: [r'^(\s*)(i{1,3}|iv|v|vi{0,3}|ix|x)\.\s+(.+)$', 
                          r'^(\s*)(I{1,3}|IV|V|VI{0,3}|IX|X)\.\s+(.+)$']
    }
    
    def __init__(self):
        """Initialize the smart text processor."""
        self.compiled_patterns = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance."""
        for bullet_type, patterns in self.BULLET_PATTERNS.items():
            self.compiled_patterns[bullet_type] = [
                re.compile(pattern, re.MULTILINE) for pattern in patterns
            ]
    
    def process_text_with_newlines(self, text: str) -> str:
        """
        Process text to properly handle newline characters for PowerPoint COM.
        This is the enhanced version of the original _process_text_with_newlines function.
        
        Args:
            text: Input text that may contain \\n characters
            
        Returns:
            Processed text with proper line breaks for PowerPoint
        """
        if not text:
            return text
        
        # Use a temporary placeholder to handle escaped newlines correctly
        temp_placeholder = "__ESCAPED_NEWLINE_PLACEHOLDER__"
        
        # Step 1: Replace escaped newlines with placeholder
        processed_text = text.replace('\\\\n', temp_placeholder)
        
        # Step 2: Convert actual newlines to PowerPoint line breaks (\\r)
        processed_text = processed_text.replace('\\n', '\\r')
        
        # Step 3: Restore escaped newlines as literal newlines
        processed_text = processed_text.replace(temp_placeholder, '\\n')
        
        # Also handle common text formatting patterns
        processed_text = processed_text.replace('\\\\t', '\\t')  # Handle tabs
        
        return processed_text
    
    def detect_bullets(self, text: str) -> List[BulletInfo]:
        """
        Detect bullet points in text and return structured information.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of BulletInfo objects for detected bullets
        """
        bullets = []
        # Handle both actual newlines and escaped newlines
        if '\n' in text:
            lines = text.split('\n')
        else:
            lines = text.split('\\n')
        
        for line_no, line in enumerate(lines):
            bullet_info = self._analyze_line_for_bullets(line, line_no)
            if bullet_info:
                bullets.append(bullet_info)
        
        return bullets
    
    def _analyze_line_for_bullets(self, line: str, line_number: int) -> Optional[BulletInfo]:
        """
        Analyze a single line for bullet patterns.
        
        Args:
            line: Line of text to analyze
            line_number: Line number in the original text
            
        Returns:
            BulletInfo if bullet detected, None otherwise
        """
        for bullet_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                match = pattern.match(line)
                if match:
                    groups = match.groups()
                    
                    # Calculate indent level based on leading whitespace
                    indent = groups[0] if groups else ""
                    indent_level = len(indent) // 2  # Assume 2 spaces per indent level
                    
                    # Extract clean text (varies by bullet type)
                    if bullet_type in [BulletType.NUMBER, BulletType.LETTER, BulletType.ROMAN]:
                        clean_text = groups[2] if len(groups) > 2 else groups[-1]
                    else:
                        clean_text = groups[1] if len(groups) > 1 else groups[-1]
                    
                    return BulletInfo(
                        original_text=line,
                        clean_text=clean_text.strip(),
                        bullet_type=bullet_type,
                        indent_level=indent_level,
                        line_number=line_number
                    )
        
        return None
    
    def parse_text_structure(self, text: str) -> TextStructure:
        """
        Parse text into a structured format with bullet detection.
        
        Args:
            text: Input text to parse
            
        Returns:
            TextStructure with parsed information
        """
        # First handle newlines
        processed_text = self.process_text_with_newlines(text)
        
        # Detect bullets
        bullets = self.detect_bullets(text)  # Use original text for detection
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in processed_text.split('\\r') if p.strip()]
        
        return TextStructure(
            paragraphs=paragraphs,
            bullets=bullets,
            has_bullets=len(bullets) > 0,
            original_text=text,
            processed_text=processed_text
        )
    
    def create_clean_text_for_bullets(self, text_structure: TextStructure) -> str:
        """
        Create clean text with bullet characters removed for PowerPoint bullet formatting.
        
        Args:
            text_structure: Parsed text structure
            
        Returns:
            Clean text without bullet characters
        """
        if not text_structure.has_bullets:
            return text_structure.processed_text
        
        lines = text_structure.processed_text.split('\\r')
        clean_lines = []
        bullet_map = {bullet.line_number: bullet for bullet in text_structure.bullets}
        
        for i, line in enumerate(lines):
            if i in bullet_map:
                bullet_info = bullet_map[i]
                # Replace with clean text, preserving indentation
                indent = " " * (bullet_info.indent_level * 2)
                clean_lines.append(f"{indent}{bullet_info.clean_text}")
            else:
                clean_lines.append(line)
        
        return '\\r'.join(clean_lines)
    
    def apply_smart_formatting_to_shape(self, shape, text: str, preserve_formatting: bool = True) -> Dict[str, Any]:
        """
        Apply smart formatting to a PowerPoint shape, including bullet conversion.
        
        Args:
            shape: PowerPoint shape COM object
            text: Text content to apply
            preserve_formatting: Whether to preserve existing formatting
            
        Returns:
            Dictionary with operation results
        """
        try:
            # Parse text structure
            text_structure = self.parse_text_structure(text)
            
            result = {
                'success': False,
                'bullets_detected': len(text_structure.bullets),
                'bullet_types': [],
                'operations': [],
                'error': None
            }
            
            if not hasattr(shape, 'TextFrame') or not shape.TextFrame:
                result['error'] = 'Shape does not support text'
                return result
            
            text_frame = shape.TextFrame
            text_range = text_frame.TextRange
            
            # Store original formatting if needed
            original_formatting = {}
            if preserve_formatting and text_range.Text.strip():
                try:
                    original_formatting = {
                        'font_name': text_range.Font.Name,
                        'font_size': text_range.Font.Size,
                        'font_color': text_range.Font.Color.RGB,
                        'bold': text_range.Font.Bold,
                        'italic': text_range.Font.Italic
                    }
                except:
                    pass
            
            if text_structure.has_bullets:
                # Apply bullet formatting
                success = self._apply_bullet_formatting(text_frame, text_structure)
                if success:
                    result['operations'].append('applied_bullet_formatting')
                    result['bullet_types'] = [bullet.bullet_type.name for bullet in text_structure.bullets]
            else:
                # Regular text without bullets
                text_range.Text = text_structure.processed_text
                result['operations'].append('applied_regular_text')
            
            # Restore formatting if needed
            if preserve_formatting and original_formatting:
                try:
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
                    
                    result['operations'].append('restored_formatting')
                except:
                    pass
            
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Error applying smart formatting: {e}")
            return {
                'success': False,
                'error': str(e),
                'bullets_detected': 0,
                'bullet_types': [],
                'operations': []
            }
    
    def _apply_bullet_formatting(self, text_frame, text_structure: TextStructure) -> bool:
        """
        Apply bullet formatting to PowerPoint text frame.
        
        Args:
            text_frame: PowerPoint TextFrame COM object
            text_structure: Parsed text structure with bullets
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create clean text without bullet characters
            clean_text = self.create_clean_text_for_bullets(text_structure)
            
            # Set the clean text
            text_frame.TextRange.Text = clean_text
            
            # Apply bullet formatting to the paragraphs
            paragraphs = text_frame.TextRange.Paragraphs()
            bullet_index = 0
            
            for i in range(1, paragraphs.Count + 1):
                paragraph = paragraphs(i)
                
                # Check if this paragraph corresponds to a bullet
                if bullet_index < len(text_structure.bullets):
                    bullet = text_structure.bullets[bullet_index]
                    
                    # Enable bullets for this paragraph
                    paragraph.ParagraphFormat.Bullet.Visible = True
                    
                    # Set bullet type based on detected pattern
                    self._set_bullet_type(paragraph.ParagraphFormat.Bullet, bullet.bullet_type)
                    
                    # Set indentation
                    if bullet.indent_level > 0:
                        paragraph.IndentLevel = bullet.indent_level
                    
                    bullet_index += 1
                else:
                    # Disable bullets for non-bullet paragraphs
                    paragraph.ParagraphFormat.Bullet.Visible = False
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying bullet formatting: {e}")
            return False
    
    def _set_bullet_type(self, bullet_format, bullet_type: BulletType):
        """
        Set the PowerPoint bullet type based on detected bullet.
        
        Args:
            bullet_format: PowerPoint Bullet COM object
            bullet_type: Detected bullet type
        """
        try:
            # PowerPoint bullet type constants (approximate values)
            bullet_type_mapping = {
                BulletType.FILLED_CIRCLE: 1,   # Filled circle
                BulletType.OPEN_CIRCLE: 2,     # Open circle  
                BulletType.SQUARE: 3,          # Square
                BulletType.DIAMOND: 4,         # Diamond
                BulletType.ARROW: 5,           # Arrow
                BulletType.CHECKMARK: 6,       # Check mark
                BulletType.DASH: 7,            # Dash
                BulletType.NUMBER: 2,          # Numbered (ppBulletNumbered)
                BulletType.LETTER: 3,          # Lettered (ppBulletAlphaLowercase)
                BulletType.ROMAN: 4            # Roman (ppBulletRomanLowercase)
            }
            
            if bullet_type in [BulletType.NUMBER, BulletType.LETTER, BulletType.ROMAN]:
                # Set numbered/lettered bullets
                if bullet_type == BulletType.NUMBER:
                    bullet_format.Type = 2  # ppBulletNumbered
                elif bullet_type == BulletType.LETTER:
                    bullet_format.Type = 3  # ppBulletAlphaLowercase
                elif bullet_type == BulletType.ROMAN:
                    bullet_format.Type = 4  # ppBulletRomanLowercase
            else:
                # Set character bullets
                bullet_format.Type = 1  # ppBulletUnnumbered
                
                # Set specific bullet character
                bullet_chars = {
                    BulletType.FILLED_CIRCLE: '•',
                    BulletType.OPEN_CIRCLE: '○',
                    BulletType.SQUARE: '■',
                    BulletType.DIAMOND: '◆',
                    BulletType.ARROW: '►',
                    BulletType.CHECKMARK: '✓',
                    BulletType.DASH: '–'
                }
                
                if bullet_type in bullet_chars:
                    bullet_format.Character = ord(bullet_chars[bullet_type])
                    
        except Exception as e:
            logger.warning(f"Could not set bullet type {bullet_type}: {e}")


# Global instance for easy access
smart_processor = SmartTextProcessor()

# Convenience functions for backward compatibility
def process_text_with_newlines(text: str) -> str:
    """Enhanced version of the original function with bullet awareness."""
    return smart_processor.process_text_with_newlines(text)

def apply_smart_text_to_shape(shape, text: str, preserve_formatting: bool = True) -> Dict[str, Any]:
    """Apply smart text processing including bullet conversion to a shape."""
    return smart_processor.apply_smart_formatting_to_shape(shape, text, preserve_formatting)
