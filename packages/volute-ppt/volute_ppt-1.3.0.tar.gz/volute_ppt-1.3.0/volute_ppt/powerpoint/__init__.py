"""
PowerPoint editing package for MCP server.

This package provides PowerPoint slide management functionality including:
- DSL parsing for slide operations
- Slide execution (add, delete, move, duplicate)
- COM automation integration

Modules:
    parser: DSL parsing and validation
    slide_executor: PowerPoint COM automation and slide operations
"""

from .parser import (
    parse_slide_operations_dsl,
    validate_slide_dsl_format,
    get_dsl_format_examples
)

from .slide_executor import (
    PowerPointSlideExecutor,
    execute_slide_operations
)

__all__ = [
    'parse_slide_operations_dsl',
    'validate_slide_dsl_format', 
    'get_dsl_format_examples',
    'PowerPointSlideExecutor',
    'execute_slide_operations'
]
