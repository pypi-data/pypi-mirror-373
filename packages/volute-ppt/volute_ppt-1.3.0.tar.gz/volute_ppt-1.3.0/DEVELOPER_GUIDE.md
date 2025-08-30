# VoluteMCP Developer Integration Guide

## 🎯 For Developers Building AI Desktop Applications

VoluteMCP enables your AI applications to interact with Microsoft PowerPoint presentations and local files on Windows machines through the Model Context Protocol (MCP).

## 🚀 Quick Integration

### 1. Install VoluteMCP

```bash
# Install from PyPI (after publishing)
pip install volutemcp

# Or install from source
pip install git+https://gitlab.com/coritan/volutemcp.git
```

### 2. MCP Configuration

Add to your MCP client configuration (e.g., Claude Desktop, custom MCP client):

```json
{
  "mcpServers": {
    "volutemcp-local": {
      "command": "python",
      "args": ["-m", "volute_ppt.server_local", "stdio"],
      "env": {
        "VOLUTEMCP_LOG_LEVEL": "INFO"
      },
      "working_directory": "/path/to/volutemcp"
    },
    "volutemcp-cloud": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-fetch", "https://volutemcp-server.onrender.com"],
      "env": {}
    }
  }
}
```

### 3. Your AI Agent Can Now:

```python
# Extract PowerPoint metadata
result = mcp_client.call_tool("extract_powerpoint_metadata", {
    "presentation_path": "C:/Users/Developer/presentation.pptx",
    "include_slide_content": True,
    "output_format": "json"
})

# Analyze specific slides
content = mcp_client.call_tool("analyze_powerpoint_content", {
    "presentation_path": "C:/Users/Developer/presentation.pptx",
    "slide_numbers": [1, 3, 5],
    "extract_text_only": False
})

# Get presentation summary
summary = mcp_client.call_tool("get_powerpoint_summary", {
    "presentation_path": "C:/Users/Developer/presentation.pptx"
})
```

## 🏗️ Architecture for Developers

### **Hybrid Architecture Benefits**:

- **Local Server**: PowerPoint COM integration, file access
- **Cloud Server**: General utilities, always available
- **Your App**: Uses both servers seamlessly

### **Integration Patterns**:

#### **Pattern 1: Direct MCP Client Integration**
```python
from mcp import Client

class MyAIApp:
    def __init__(self):
        self.local_client = Client("volutemcp-local")
        self.cloud_client = Client("volutemcp-cloud")
    
    async def analyze_presentation(self, file_path):
        # Use local server for PowerPoint operations
        metadata = await self.local_client.call_tool(
            "extract_powerpoint_metadata", 
            {"presentation_path": file_path}
        )
        
        # Use cloud server for calculations
        stats = await self.cloud_client.call_tool(
            "calculate", 
            {"expression": f"{len(metadata['slides'])} * 2"}
        )
        
        return {"metadata": metadata, "stats": stats}
```

#### **Pattern 2: HTTP API Integration**
```javascript
// For web-based or cross-platform desktop apps
class PowerPointAI {
    constructor() {
        this.cloudEndpoint = 'https://volutemcp-server.onrender.com';
        this.localEndpoint = 'http://localhost:8001'; // Local server
    }
    
    async analyzePresentationRemotely(data) {
        // Use cloud server for processing uploaded data
        const response = await fetch(`${this.cloudEndpoint}/mcp/tools/call`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: "2.0", id: 1,
                method: "tools/call",
                params: { 
                    name: "calculate", 
                    arguments: { expression: data.calculation }
                }
            })
        });
        return response.json();
    }
}
```

## 🔧 Available Tools for Your Apps

### **Local Server Tools** (Windows + PowerPoint required):
| Tool | Purpose | Use Case |
|------|---------|----------|
| `extract_powerpoint_metadata` | Full presentation analysis | Content extraction, slide analysis |
| `analyze_powerpoint_content` | Specific slide content | Targeted content analysis |
| `get_powerpoint_summary` | High-level overview | Quick presentation insights |
| `validate_powerpoint_file` | File integrity check | Error handling, validation |
| `list_local_files` | Directory listing | File discovery |
| `read_local_file` | File content access | Text file processing |

### **Cloud Server Tools** (Always available):
| Tool | Purpose | Use Case |
|------|---------|----------|
| `echo` | Connectivity test | Health checks |
| `calculate` | Mathematical operations | Data processing |
| `get_server_info` | System information | Debugging, diagnostics |
| `analyze_data` (prompt) | Analysis prompts | AI prompt generation |
| `code_review_prompt` (prompt) | Code review prompts | Development assistance |

## 💻 Development Examples

### **Desktop App Integration (Python + Tkinter/PyQt)**

```python
import asyncio
from tkinter import filedialog, messagebox
import tkinter as tk
from mcp import Client

class PowerPointAIApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PowerPoint AI Assistant")
        self.mcp_client = None
        self.setup_ui()
        
    async def init_mcp(self):
        self.mcp_client = Client("volutemcp-local")
        await self.mcp_client.connect()
        
    def setup_ui(self):
        # File selection
        tk.Button(
            self.root, 
            text="Analyze PowerPoint", 
            command=self.analyze_presentation
        ).pack(pady=10)
        
        self.result_text = tk.Text(self.root, height=20, width=80)
        self.result_text.pack(pady=10)
        
    def analyze_presentation(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PowerPoint files", "*.pptx *.ppt")]
        )
        if file_path:
            asyncio.run(self._analyze_async(file_path))
            
    async def _analyze_async(self, file_path):
        if not self.mcp_client:
            await self.init_mcp()
            
        try:
            result = await self.mcp_client.call_tool(
                "extract_powerpoint_metadata",
                {
                    "presentation_path": file_path,
                    "include_slide_content": True,
                    "output_format": "json"
                }
            )
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, str(result))
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {e}")

if __name__ == "__main__":
    app = PowerPointAIApp()
    app.root.mainloop()
```

### **Web App Integration (FastAPI + JavaScript)**

```python
# Backend (FastAPI)
from fastapi import FastAPI, UploadFile
import httpx

app = FastAPI()

@app.post("/analyze-presentation")
async def analyze_presentation(file: UploadFile):
    # Save uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    # Call local MCP server (assuming it's running)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/mcp/tools/call",
            json={
                "jsonrpc": "2.0", "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "extract_powerpoint_metadata",
                    "arguments": {
                        "presentation_path": temp_path,
                        "include_slide_content": True
                    }
                }
            }
        )
    
    return response.json()
```

```javascript
// Frontend (React/Vue/vanilla JS)
class PowerPointAnalyzer {
    async analyzeFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/analyze-presentation', {
            method: 'POST',
            body: formData
        });
        
        return response.json();
    }
}

// Usage
const analyzer = new PowerPointAnalyzer();
const fileInput = document.getElementById('ppt-file');

fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const result = await analyzer.analyzeFile(file);
        console.log('PowerPoint Analysis:', result);
    }
});
```

## 🚦 Development Workflow

### **1. Local Development**
```bash
# Clone and setup
git clone https://gitlab.com/coritan/volutemcp.git
cd volutemcp
pip install -e .

# Run local server for testing
volutemcp-local --port 8001

# Test your integration
curl http://localhost:8001/health  # Should return "LOCAL-OK"
```

### **2. Production Deployment**
```bash
# Your app's requirements.txt
volutemcp>=1.0.0

# User installation
pip install volutemcp

# MCP configuration in your app's setup
{
  "volutemcp-local": {
    "command": "volutemcp-local",
    "args": ["--transport", "stdio"]
  }
}
```

### **3. Distribution**
Include this in your app's documentation:

> **Prerequisites**: 
> - Windows OS
> - Microsoft PowerPoint installed
> - Python 3.8+ 
> 
> **Installation**: `pip install volutemcp`

## 🔒 Security Considerations

### **For Desktop Apps**:
- ✅ Local server runs with user permissions
- ✅ File access limited to user's accessible files
- ✅ COM integration sandboxed to PowerPoint
- ✅ No network access to user files

### **For Web Apps**:
- ⚠️ Be careful with file uploads
- ✅ Use cloud server for processing uploaded content
- ✅ Don't expose local server to network
- ✅ Validate file types and sizes

## 📚 API Reference

### **PowerPoint Metadata Structure**
```typescript
interface PowerPointMetadata {
  core_properties: {
    title: string;
    author: string;
    created: string;
    modified: string;
  };
  presentation_info: {
    slide_count: number;
    slide_width: number;
    slide_height: number;
  };
  slides: Array<{
    slide_number: number;
    title: string;
    content: string;
    shapes: Array<ShapeInfo>;
  }>;
}
```

### **Error Handling**
```python
try:
    result = await mcp_client.call_tool("extract_powerpoint_metadata", {
        "presentation_path": file_path
    })
except FileNotFoundError:
    # Handle missing file
    print("PowerPoint file not found")
except PermissionError:
    # Handle access denied
    print("Permission denied - check file access")
except Exception as e:
    # Handle PowerPoint/COM errors
    print(f"PowerPoint processing error: {e}")
```

## 🤝 Support & Contributing

- **Issues**: https://gitlab.com/coritan/volutemcp/-/issues
- **Documentation**: https://gitlab.com/coritan/volutemcp
- **Examples**: See `examples/` directory in repository

## 📈 Roadmap for Developers

- 🔄 **Python SDK**: Direct API without MCP overhead
- 📦 **NPM Package**: Node.js integration  
- 🔌 **Visual Studio Extension**: IDE integration
- 📱 **Cross-platform**: macOS/Linux support (via Office Online APIs)

Your AI desktop applications now have powerful PowerPoint integration capabilities! 🚀
