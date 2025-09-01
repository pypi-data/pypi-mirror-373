# Volute-PPT Server

A FastMCP 2.0-based Model Context Protocol (MCP) server providing various tools, resources, and prompts for AI model interaction with **multimodal AI capabilities** including PowerPoint slide image capture.

## Features

- **PowerPoint Analysis**: Comprehensive metadata extraction, content analysis, file validation
- **PowerPoint Editing**: Smart text editing with bullet conversion, shape formatting, content management
- **Slide Management**: Add, delete, move, duplicate slides with DSL commands and bulk operations
- **Multimodal AI**: Slide image capture with base64-encoded PNG data URLs for vision-based AI analysis

## Quick Start

### 1. Local Development Setup

For local development and PowerPoint COM integration:

```bash
# Clone the project
git clone https://gitlab.com/coritan/volute-ppt.git
cd volute-ppt

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# SERVER_NAME=Volute-PPT
# SERVER_HOST=127.0.0.1
# SERVER_PORT=8001
```

### 3. Run the Server

#### HTTP Transport (Web Service)
```bash
python server.py
```
Server will be available at: http://127.0.0.1:8001

#### STDIO Transport (Local Tool)
```bash
python server.py stdio
```

## Server Components

### PowerPoint Tools

Advanced PowerPoint analysis, editing, and processing capabilities with **multimodal AI support**:

#### Core Analysis Tools
| Tool | Description | Key Features |
|------|-------------|-------------|
| `extract_powerpoint_metadata` | Extract comprehensive metadata from presentations | Complete technical metadata, shapes, formatting, layouts |
| `analyze_powerpoint_content` | Analyze content of specific slides | Text extraction, content focus, selective slide analysis |
| `get_powerpoint_summary` | Get high-level presentation overview | Quick stats, multimedia detection, slide summaries |
| `validate_powerpoint_file` | Validate file integrity and compatibility | Format validation, corruption detection, structure checks |

#### Slide Management Tools
| Tool | Description | Key Features |
|------|-------------|-------------|
| `manage_presentation_slides` | Add, delete, move, duplicate slides using DSL | DSL commands, COM automation, batch operations |
| `bulk_slide_operations` | Execute multiple slide operations with validation | Transaction-like behavior, pre-validation, error handling |

#### Visual & Multimodal Tools
| Tool | Description | Key Features |
|------|-------------|-------------|
| `capture_slide_images` | Capture slides as base64 PNG images | Multimodal AI integration, configurable resolution, batch capture |
| `compare_presentation_versions` | Compare two presentation versions | Visual diffs, metadata changes, version control support |

#### Content Editing Tools
| Tool | Description | Key Features |
|------|-------------|-------------|
| `edit_slide_text_content` | Edit text with intelligent bullet conversion | Smart bullet detection, multi-level indentation, format preservation |
| `apply_shape_formatting` | Apply comprehensive shape formatting | Font styling, positioning, colors, bulk operations |
| `manage_slide_shapes` | Add, delete, copy, transform shapes | Shape lifecycle, z-order, grouping, transformations |

#### Advanced Tools
| Tool | Description | Key Features |
|------|-------------|-------------|
| `extract_presentation_templates` | Extract reusable design templates | Master slides, color schemes, layout patterns, design systems |
| `get_slide_capture_capabilities` | Report system capabilities | COM availability, system requirements, capability checks |

#### PowerPoint Features

**Analysis & Extraction:**
- **Comprehensive Metadata Extraction**: Core properties, slide dimensions, layout information
- **Shape Analysis**: Position, size, formatting, and content of all shapes
- **Text Content**: Fonts, colors, alignment, paragraph and run-level formatting
- **Multimedia Elements**: Images with crop information, tables with cell data
- **Formatting Details**: Fill, line, shadow formatting for all objects
- **Slide Structure**: Master slides, layouts, notes, and comments
- **Content Summarization**: Automatic extraction of slide titles and content
- **File Validation**: Format checking, corruption detection, structural integrity

**Editing & Content Management:**
- **🆕 Smart Text Processing**: Intelligent bullet detection and conversion to native PowerPoint bullets
- **🆕 Multi-level Bullet Support**: Proper indentation and nesting for complex bullet structures
- **🆕 Enhanced Newline Handling**: Converts `\n` to line breaks, `\\n` to literal text
- **🆕 Shape Editing**: Add, delete, copy, transform shapes with comprehensive property control
- **🆕 Text Formatting**: Font styling, colors, alignment, positioning with format preservation
- **🆕 Auto-resize**: Automatic shape resizing to accommodate new content

**Slide Management:**
- **🆕 Bulk Operations**: Execute multiple slide operations with transaction-like validation
- **🆕 Error Handling**: Pre-validation, rollback support, detailed operation tracking

**Multimodal & Visual:**
- **🆕 Multimodal AI Integration**: Slide image capture as base64 PNG data URLs for vision-capable LLMs
- **🆕 Visual Content Analysis**: Export slides as images for AI-powered visual understanding
- **🆕 Version Comparison**: Visual and metadata diffs between presentation versions

**Advanced Features:**
- **🆕 Template Extraction**: Extract reusable design systems, masters, and layouts
- **🆕 Theme Management**: Color schemes, font themes, and design pattern extraction

### Resources
- `config://server` - PowerPoint server configuration
- `local://system` - Local PowerPoint system status
- `local://files/{directory}` - Get PowerPoint files in directory



## Integration Approaches

### **Local MCP Integration (Desktop Apps)**

**Best for**: Claude Desktop, local AI applications, PowerPoint integration, multimodal AI workflows

```json
{
  "volute-ppt": {
    "command": "python",
    "args": [
      "-m",
      "volute_ppt.server_local",
      "stdio"
    ],
    "env": {},
    "working_directory": null
  }
}
```

## SDK Toolkit

The package provides a high-level toolkit that lets you directly use PowerPoint tools without dealing with MCP server setup:

```python
from volute_ppt import (
    # Core Analysis
    extract_powerpoint_metadata, analyze_powerpoint_content,
    # Multimodal & Visual
    capture_slide_images, compare_presentation_versions,
    # Content Editing
    edit_slide_text_content, manage_slide_shapes
)

# Extract metadata from a presentation
metadata = extract_powerpoint_metadata(
    presentation_path="./presentation.pptx",
    include_slide_content=True
)

# Capture slides as images for AI analysis
images = capture_slide_images(
    presentation_path="./presentation.pptx",
    slide_numbers=[1, 2, 3],  # Specific slides or omit for all
    image_width=1024,         # Optional: control image size
    image_height=768
)

# Edit slide text with intelligent bullet conversion
edit_result = edit_slide_text_content(
    presentation_path="./presentation.pptx",
    slide_number=2,
    text_updates={
        "Title 1": "New Title",
        "Content 1": "• First bullet\n• Second bullet\n  - Sub-bullet"
    },
    convert_bullets=True,  # Converts text bullets to native PowerPoint bullets
    preserve_formatting=True
)
```


## Contributing

1. Fork the git repository
2. Create a feature branch
3. Add your changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.