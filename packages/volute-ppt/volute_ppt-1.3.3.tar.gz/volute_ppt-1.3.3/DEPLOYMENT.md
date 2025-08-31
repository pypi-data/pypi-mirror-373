# VoluteMCP Render Deployment Guide

## Quick Deploy to Render

### Method 1: Using Render Blueprint (Recommended)

1. **Push your code to GitHub** (if not already there):
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Deploy via Render Dashboard**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file and deploy

### Method 2: Manual Web Service Creation

1. **Go to Render Dashboard**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `volutemcp` repository

2. **Configure the service**:
   - **Name**: `volutemcp-server`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`

3. **Set Environment Variables**:
   ```
   SERVER_NAME=VoluteMCP
   SERVER_HOST=0.0.0.0
   FASTMCP_LOG_LEVEL=INFO
   FASTMCP_MASK_ERROR_DETAILS=false
   FASTMCP_RESOURCE_PREFIX_FORMAT=path
   FASTMCP_INCLUDE_FASTMCP_META=true
   ```

4. **Deploy**: Click "Create Web Service"

## After Deployment

### 1. Get Your Server URL
After deployment, Render will provide a URL like:
```
https://volutemcp-server-xxxx.onrender.com
```

### 2. Test Your Deployment
```bash
# Test health endpoint
curl https://your-app-name.onrender.com/health

# Test server info
curl https://your-app-name.onrender.com/info

# Test MCP endpoint (tools list)
curl -X POST https://your-app-name.onrender.com/mcp/tools/list \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

### 3. Configure AI Agents to Use Your Server

Your deployed MCP server can now be used by any AI agent that supports MCP over HTTP:

#### For Claude (Desktop App)
Add to your MCP configuration:
```json
{
  "servers": {
    "volutemcp": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-fetch", "https://your-app-name.onrender.com"]
    }
  }
}
```

#### GitLab Repository
Your code is hosted at: https://gitlab.com/coritan/volutemcp

#### For Custom Applications
Use the HTTP endpoint directly:
```javascript
// Example: Call a tool
fetch('https://your-app-name.onrender.com/mcp/tools/call', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: "echo",
      arguments: { message: "Hello from remote!" }
    }
  })
})
```

## Pricing Considerations

### Render Plans:
- **Free Tier**: 750 hours/month, spins down after 15 minutes of inactivity
- **Starter ($7/month)**: Always on, no sleep, 100GB bandwidth
- **Standard ($25/month)**: More CPU/memory, 1TB bandwidth

For production use with AI agents, the **Starter plan** is recommended to avoid cold starts.

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 10000 | Port (Render sets this automatically) |
| `SERVER_NAME` | VoluteMCP | Your server name |
| `SERVER_HOST` | 0.0.0.0 | Host binding (must be 0.0.0.0 for Render) |
| `FASTMCP_LOG_LEVEL` | INFO | Logging level |
| `FASTMCP_MASK_ERROR_DETAILS` | false | Hide error details from clients |

## Monitoring and Logs

### View Logs:
1. Go to your Render service dashboard
2. Click on "Logs" tab
3. Monitor real-time logs and health checks

### Health Monitoring:
- Health check endpoint: `/health`
- Server info endpoint: `/info`
- Render automatically monitors these endpoints

## Troubleshooting

### Common Issues:

1. **Build fails**: Check that all dependencies in `requirements.txt` are correct
2. **Server won't start**: Ensure `SERVER_HOST=0.0.0.0` (not 127.0.0.1)
3. **Port issues**: Let Render handle the PORT env var automatically
4. **PowerPoint tools fail**: May need to install system dependencies (see Dockerfile for reference)

### Debug Commands:
```bash
# Check if server is responding
curl https://your-app-name.onrender.com/health

# Test MCP protocol
curl -X POST https://your-app-name.onrender.com/mcp/initialize \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}}'
```

## Security Considerations

### For Public Deployment:
1. **Add authentication** if needed:
   ```python
   # In server.py, add middleware for API key validation
   @mcp.middleware("http")
   async def auth_middleware(request, call_next):
       api_key = request.headers.get("X-API-Key")
       if not api_key or api_key != os.getenv("API_KEY"):
           return PlainTextResponse("Unauthorized", status_code=401)
       return await call_next(request)
   ```

2. **Rate limiting**: Consider adding rate limiting for production use
3. **CORS**: Configure CORS if needed for browser-based clients

### Environment Variables for Production:
```bash
# Add to Render environment variables
API_KEY=your-secure-api-key-here
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## Next Steps

1. **Custom Domain**: Add your own domain in Render settings
2. **SSL Certificate**: Render provides free SSL automatically  
3. **Monitoring**: Set up uptime monitoring with services like UptimeRobot
4. **CI/CD**: Enable auto-deploy on git push (already configured in render.yaml)

Your VoluteMCP server is now accessible globally at your Render URL! 🚀
