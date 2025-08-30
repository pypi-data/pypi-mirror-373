# VoluteMCP Hybrid Architecture

## 🏗️ Architecture Overview

VoluteMCP uses a **hybrid architecture** with two complementary MCP servers to solve the PowerPoint/COM integration challenge:

### 🌐 Cloud Server (Public)
**URL**: https://volutemcp-server.onrender.com
- **Environment**: Linux (Render cloud)
- **Purpose**: General-purpose tools accessible from anywhere
- **Access**: Global, any AI agent can connect

### 🖥️ Local Server (Private)  
**Location**: User's Windows machine
- **Environment**: Windows with PowerPoint installed
- **Purpose**: PowerPoint COM integration and local file access
- **Access**: Local only, full system integration

## 🤔 Why This Architecture?

### **The Problem You Identified**:
```
❌ Cloud Server Limitations:
- No PowerPoint installed
- No Windows COM objects  
- No access to user's local files
- Linux environment (your tools need Windows)
```

### **The Solution**:
```
✅ Hybrid Architecture:
- Cloud server handles general tools
- Local server handles PowerPoint + file access
- AI agents can use both simultaneously
- Best of both worlds!
```

## 🔧 Server Responsibilities

### **Cloud Server Tools**:
- ✅ `echo` - Test connectivity
- ✅ `calculate` - Math operations  
- ✅ `get_server_info` - System info
- ✅ Text processing, JSON handling
- ✅ Data analysis prompts
- ✅ Code review prompts

### **Local Server Tools**:
- ✅ `extract_powerpoint_metadata` - COM integration
- ✅ `analyze_powerpoint_content` - File access
- ✅ `get_powerpoint_summary` - Local processing
- ✅ `validate_powerpoint_file` - File validation
- ✅ `list_local_files` - Directory access
- ✅ `read_local_file` - File content access

## 🚀 Setup Instructions

### 1. Cloud Server (Already Done!)
Your cloud server is live at: https://volutemcp-server.onrender.com

### 2. Local Server Setup

#### Install Local Dependencies:
```bash
# Make sure you have pywin32 for COM access
pip install pywin32

# Test COM access
python -c "import win32com.client; print('COM available!')"
```

#### Run Local Server:
```bash
# HTTP mode (accessible via localhost)
python server_local.py

# STDIO mode (for Claude Desktop)
python server_local.py stdio
```

### 3. Configure Claude Desktop

Use the hybrid configuration file I created:

**File**: `claude_mcp_hybrid_config.json`
```json
{
  "mcpServers": {
    "volutemcp-cloud": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-fetch", "https://volutemcp-server.onrender.com"]
    },
    "volutemcp-local": {
      "command": "python",
      "args": ["C:\\Users\\shrey\\projects\\volutemcp\\server_local.py", "stdio"]
    }
  }
}
```

Copy this to your Claude Desktop MCP settings.

## 💡 Usage Examples

### **Using Cloud Tools** (General Purpose):
```javascript
// Calculate something
fetch('https://volutemcp-server.onrender.com/mcp/tools/call', {
  method: 'POST',
  body: JSON.stringify({
    jsonrpc: "2.0", id: 1,
    method: "tools/call",
    params: { name: "calculate", arguments: { expression: "2 + 3 * 4" }}
  })
})
```

### **Using Local Tools** (PowerPoint):
```python
# In Claude Desktop with local server configured
"Please use the extract_powerpoint_metadata tool to analyze my presentation.pptx file"
```

## 🎯 Best Practices

### **When to Use Cloud Server**:
- ✅ Mathematical calculations
- ✅ Text processing 
- ✅ Data analysis prompts
- ✅ General utilities
- ✅ When user location doesn't matter

### **When to Use Local Server**:
- ✅ PowerPoint file manipulation
- ✅ Local file access
- ✅ COM object integration
- ✅ Windows-specific operations
- ✅ When you need user's actual files

## 🔄 Workflow Example

Here's how an AI agent would work with both servers:

1. **General Task**: "Calculate the average of these numbers"
   - → **Cloud server** handles calculation
   
2. **PowerPoint Task**: "Analyze my presentation.pptx"
   - → **Local server** accesses local file and uses COM

3. **Combined Task**: "Calculate metrics from my presentation data"
   - → **Local server** extracts PowerPoint data
   - → **Cloud server** performs calculations
   - → AI agent combines results

## 🛡️ Security Benefits

### **Cloud Server**:
- ✅ No access to your local files
- ✅ Isolated environment
- ✅ Public tools only

### **Local Server**:
- ✅ Runs on your machine
- ✅ You control access
- ✅ Local files stay local
- ✅ COM integration under your control

## 🚀 Deployment Status

### ✅ **Cloud Server**: DEPLOYED
- **URL**: https://volutemcp-server.onrender.com
- **Status**: ✅ Live and accessible
- **Auto-deploy**: ✅ Connected to GitLab

### 🖥️ **Local Server**: READY TO RUN
- **Status**: ✅ Code ready
- **Requirements**: Windows + PowerPoint installed
- **Command**: `python server_local.py`

## 🎉 Summary

You now have a **complete hybrid MCP architecture** that solves the PowerPoint integration challenge:

- **Global accessibility** via cloud server
- **Local PowerPoint integration** via local server  
- **Best of both worlds** - secure, functional, and accessible
- **Future-proof** - can add more specialized local tools as needed

Your users get:
- ✅ Universal access to general tools
- ✅ Full PowerPoint integration on their local machine
- ✅ Secure local file access
- ✅ Seamless experience across both servers

This is exactly the right architecture for your use case! 🚀
