# Volute-PPT Server

A FastMCP 2.0-based Model Context Protocol (MCP) server providing various tools, resources, and prompts for AI model interaction with **multimodal AI capabilities** including PowerPoint slide image capture.

## Features

- **Core Tools**: Mathematical calculations, text processing, JSON manipulation, hashing, encoding/decoding
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

### Tools

| Tool | Description | Tags |
|------|-------------|------|
| `echo` | Echo back messages for testing | utility, public |
| `calculate` | Safely evaluate math expressions | math, utility |
| `get_server_info` | Get server environment info | system, info |
| `format_text` | Format text (upper, lower, title, reverse) | utility, text |
| `process_json` | Process JSON (pretty, minify, keys, validate) | data, json |
| `get_timestamp` | Get timestamps in various formats | system, time |
| `list_operations` | Perform operations on string lists | data, list |
| `hash_text` | Generate text hashes (SHA256, SHA1, MD5) | security, hash |
| `encode_decode` | Encode/decode text (base64, URL, hex) | development, base64 |

### PowerPoint Tools

Advanced PowerPoint analysis, editing, and processing capabilities with **multimodal AI support**:

#### 📊 Core Analysis Tools
| Tool | Description | Key Features |
|------|-------------|-------------|
| `extract_powerpoint_metadata` | Extract comprehensive metadata from presentations | Complete technical metadata, shapes, formatting, layouts |
| `analyze_powerpoint_content` | Analyze content of specific slides | Text extraction, content focus, selective slide analysis |
| `get_powerpoint_summary` | Get high-level presentation overview | Quick stats, multimedia detection, slide summaries |
| `validate_powerpoint_file` | Validate file integrity and compatibility | Format validation, corruption detection, structure checks |

#### 🎯 Slide Management Tools
| Tool | Description | Key Features |
|------|-------------|-------------|
| `manage_presentation_slides` | Add, delete, move, duplicate slides using DSL | DSL commands, COM automation, batch operations |
| `bulk_slide_operations` | Execute multiple slide operations with validation | Transaction-like behavior, pre-validation, error handling |

#### 🖼️ Visual & Multimodal Tools
| Tool | Description | Key Features |
|------|-------------|-------------|
| `capture_slide_images` | Capture slides as base64 PNG images | Multimodal AI integration, configurable resolution, batch capture |
| `compare_presentation_versions` | Compare two presentation versions | Visual diffs, metadata changes, version control support |

#### ✏️ Content Editing Tools
| Tool | Description | Key Features |
|------|-------------|-------------|
| `edit_slide_text_content` | Edit text with intelligent bullet conversion | Smart bullet detection, multi-level indentation, format preservation |
| `apply_shape_formatting` | Apply comprehensive shape formatting | Font styling, positioning, colors, bulk operations |
| `manage_slide_shapes` | Add, delete, copy, transform shapes | Shape lifecycle, z-order, grouping, transformations |

#### 🎨 Advanced Tools
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

#### Static Resources
- `config://server` - Server configuration
- `data://environment` - Environment information  
- `system://status` - System status
- `data://sample-users` - Sample user data
- `config://features` - Available features

#### Resource Templates
- `users://{user_id}` - Get user by ID
- `config://{section}` - Get config section
- `data://{data_type}/summary` - Get data summaries
- `logs://{log_level}` - Get simulated logs
- `file://{file_path}` - Read file contents (with safety checks)



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

### Configuration

The server uses Pydantic for configuration management. Settings can be provided via:

1. Environment variables (prefixed with `VOLUTE_`)
2. `.env` file
3. Default values in `config.py`

#### Available Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `VOLUTE_NAME` | VoluteMCP | Server name |
| `VOLUTE_HOST` | 127.0.0.1 | Server host |
| `VOLUTE_PORT` | 8000 | Server port |
| `VOLUTE_LOG_LEVEL` | INFO | Logging level |

### Tag-Based Filtering

Filter components by tags when creating the server:

```python
# Only expose utility tools
mcp = FastMCP(include_tags={"utility"})

# Hide internal tools
mcp = FastMCP(exclude_tags={"internal"})

# Combine filters
mcp = FastMCP(include_tags={"public"}, exclude_tags={"deprecated"})
```

## Advanced Usage

### Server Composition

```python
from fastmcp import FastMCP
from tools import register_tools

# Create modular servers
tools_server = FastMCP("ToolsOnly")
register_tools(tools_server)

# Mount into main server
main_server = FastMCP("Main")
main_server.mount(tools_server, prefix="tools")
```

### Custom Serialization

```python
import yaml

def yaml_serializer(data):
    return yaml.dump(data, sort_keys=False)

mcp = FastMCP(tool_serializer=yaml_serializer)
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "server.py"]
```

### systemd Service

```ini
[Unit]
Description=VoluteMCP Server
After=network.target

[Service]
Type=simple
User=volute
WorkingDirectory=/opt/volutemcp
ExecStart=/opt/volutemcp/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.