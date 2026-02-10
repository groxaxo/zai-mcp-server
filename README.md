# ZAI MCP Server

A Model Context Protocol (MCP) server that provides web search, content fetching, and AI-powered summarization capabilities using ZAI's GLM-4.7-Flash model.

## Features

- **Web Search**: Search the web using DuckDuckGo
- **Content Fetching**: Clean and extract text from any website
- **AI Summarization**: Summarize web content using GLM-4.7-Flash
- **Combined Workflows**: Search, fetch, and summarize in one operation
- **Fast & Efficient**: Uses flash model for quick responses

## Tools

### `search_web`
Search the web for information.

**Parameters:**
- `query` (string, required): Search query
- `num_results` (number, optional): Number of results (1-10, default: 5)

**Returns:**
```json
{
  "query": "search term",
  "count": 5,
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com",
      "snippet": "Brief snippet of the content..."
    }
  ]
}
```

### `fetch_and_summarize`
Fetch a website URL and summarize its content.

**Parameters:**
- `url` (string, required): Website URL to fetch
- `max_content_length` (number, optional): Max content length to process (default: 10000)

**Returns:**
```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "summary": "AI-generated summary of the content...",
  "content_length": 5000
}
```

### `search_and_summarize`
Search the web, fetch the top result, and summarize it.

**Parameters:**
- `query` (string, required): Search query
- `result_index` (number, optional): Which search result to fetch (1-10, default: 1)

**Returns:**
```json
{
  "query": "search term",
  "result_index": 1,
  "url": "https://example.com/article",
  "title": "Article Title",
  "summary": "AI-generated summary...",
  "total_results": 10
}
```

## Installation

### Prerequisites

- Python 3.8 or higher
- ZAI API key (get one at https://z.ai/model-api)
- pip package manager

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/zai-mcp-server.git
cd zai-mcp-server

# Install dependencies
pip install -r requirements.txt

# Make server executable
chmod +x src/server.py
```

### Quick Start

```bash
# Set your API key
export ZAI_API_KEY="your-zai-api-key"

# Run the server
python src/server.py
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|-----------|-------------|-----------|---------|
| `ZAI_API_KEY` | Your ZAI API key | Yes | - |

### API Configuration

The server uses the following ZAI API configuration:
- **Base URL**: `https://api.z.ai/api/paas/v4`
- **Model**: `glm-4.7-flash`
- **Max Tokens**: 1000
- **Temperature**: 0.7

## Usage

### Standalone Testing

```bash
# Test initialization
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python src/server.py

# List available tools
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | python src/server.py

# Search the web
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search_web", "arguments": {"query": "AI news", "num_results": 3}}}' | python src/server.py
```

### Integration with Claude Desktop

Add to Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "zai": {
      "command": "python3",
      "args": ["/absolute/path/to/zai-mcp-server/src/server.py"],
      "env": {
        "ZAI_API_KEY": "your-zai-api-key"
      }
    }
  }
}
```

### Integration with Cursor

Add to Cursor settings file (`~/.cursor/mcp_config.json`):

```json
{
  "mcpServers": {
    "zai": {
      "command": "python3",
      "args": ["/absolute/path/to/zai-mcp-server/src/server.py"],
      "env": {
        "ZAI_API_KEY": "your-zai-api-key"
      }
    }
  }
}
```

### Integration with Cline (VS Code)

Add to your MCP settings in VS Code:

```json
{
  "mcpServers": [
    {
      "name": "zai",
      "command": "python3",
      "args": ["/absolute/path/to/zai-mcp-server/src/server.py"],
      "env": {
        "ZAI_API_KEY": "${env:ZAI_API_KEY}"
      }
    }
  ]
}
```

### Integration with Continue

Add to `~/.continue/config.json`:

```json
{
  "mcpServers": {
    "zai": {
      "command": "python3",
      "args": ["/absolute/path/to/zai-mcp-server/src/server.py"],
      "env": {
        "ZAI_API_KEY": "your-zai-api-key"
      }
    }
  }
}
```

### Integration with Roo Code

Add to Roo Code's MCP configuration:

```json
{
  "mcpServers": {
    "zai": {
      "command": "python3",
      "args": ["/absolute/path/to/zai-mcp-server/src/server.py"],
      "env": {
        "ZAI_API_KEY": "your-zai-api-key"
      }
    }
  }
}
```

## OpenCode Native Integration

### Setup

OpenCode supports MCP servers natively. To configure:

1. **Create/Update the MCP configuration file**:
   ```bash
   # Default location: ~/.config/opencode/mcp_servers.json
   mkdir -p ~/.config/opencode
   nano ~/.config/opencode/mcp_servers.json
   ```

2. **Add ZAI MCP Server configuration**:
   ```json
   {
     "mcpServers": {
       "zai": {
         "name": "ZAI Web Search & Summarization",
         "description": "Search web and summarize content using GLM-4.7-Flash",
         "command": "python3",
         "args": ["/home/op/zai-mcp-server/src/server.py"],
         "env": {
           "ZAI_API_KEY": "your-zai-api-key"
         },
         "enabled": true
       }
     }
   }
   ```

3. **Restart OpenCode** to load the new MCP server

### Usage in OpenCode

Once configured, you can use the MCP server in OpenCode conversations:

```
User: Search for recent developments in AI and summarize the top result

Assistant: I'll use the ZAI MCP server to search and summarize for you.

[Calls search_and_summarize tool]

The ZAI MCP server found an article about recent AI developments. Here's a summary:
- Main point 1
- Main point 2
- Main point 3

Full article available at: https://example.com/ai-developments
```

## Examples

### Example 1: Web Search

```python
# Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_web",
    "arguments": {
      "query": "machine learning trends 2024",
      "num_results": 5
    }
  }
}

# Response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": JSON.stringify({
          "query": "machine learning trends 2024",
          "count": 5,
          "results": [...]
        })
      }
    ]
  }
}
```

### Example 2: Fetch and Summarize

```python
# Request
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "fetch_and_summarize",
    "arguments": {
      "url": "https://www.example.com/article"
    }
  }
}

# Response
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": JSON.stringify({
          "url": "https://www.example.com/article",
          "title": "Article Title",
          "summary": "Key points:\n• Point 1\n• Point 2\n• Point 3",
          "content_length": 5000
        })
      }
    ]
  }
}
```

### Example 3: Search and Summarize (Combined)

```python
# Request
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "search_and_summarize",
    "arguments": {
      "query": "quantum computing breakthrough",
      "result_index": 1
    }
  }
}

# Response
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": JSON.stringify({
          "query": "quantum computing breakthrough",
          "result_index": 1,
          "url": "https://example.com/quantum-news",
          "title": "Major Quantum Computing Breakthrough",
          "summary": "Researchers have achieved a significant milestone...",
          "total_results": 10
        })
      }
    ]
  }
}
```

## Testing

Run the test suite to verify the server is working correctly:

```bash
python examples/test_server.py
```

Expected output:
```
============================================================
ZAI MCP Server Test Suite
============================================================

Testing initialization...
✓ Initialize: mcp-zai-server v1.0.0

Testing tools list...
✓ Available tools (3):
  - search_web: Search the web for information using DuckDuckGo
  - fetch_and_summarize: Fetch a website URL and summarize its content using GLM-4.7-Flash
  - search_and_summarize: Search the web, fetch top result, and summarize using GLM-4.7-Flash

Testing resources list...
✓ Available resources (1):
  - zai://status: Current status of ZAI MCP server

Testing resource read...
✓ Server status:
  Status: online
  Model: glm-4.7-flash
  API Endpoint: https://api.z.ai/api/paas/v4
  Tools: search_web, fetch_and_summarize, search_and_summarize

============================================================
✓ All tests passed!
============================================================
```

## Development

### Project Structure

```
zai-mcp-server/
├── src/
│   └── server.py          # Main MCP server implementation
├── docs/
│   ├── ARCHITECTURE.md     # Architecture documentation
│   └── API_REFERENCE.md    # Detailed API reference
├── examples/
│   └── test_server.py      # Test suite and examples
├── requirements.txt           # Python dependencies
├── README.md                # This file
└── .env.example             # Environment variables template
```

### Dependencies

- `aiohttp` - Async HTTP client
- `beautifulsoup4` - HTML parsing
- `openai` - OpenAI-compatible client for ZAI API

## Troubleshooting

### Common Issues

**Server won't start**
- Ensure Python 3.8+ is installed: `python --version`
- Check dependencies are installed: `pip install -r requirements.txt`
- Verify API key is set: `echo $ZAI_API_KEY`

**Search returns no results**
- DuckDuckGo API may have rate limits
- Try with a different query
- Check internet connectivity

**Summarization fails**
- Verify API key is valid at https://z.ai/model-api
- Check API credits/balance
- Ensure URL is accessible

**MCP client can't connect**
- Verify server path in configuration is correct
- Ensure Python3 is in system PATH
- Check file permissions: `chmod +x src/server.py`

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export ZAI_DEBUG=1
python src/server.py
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

- **Issues**: Report bugs and feature requests on GitHub Issues
- **ZAI API Documentation**: https://docs.z.ai
- **MCP Specification**: https://modelcontextprotocol.io

## Acknowledgments

- ZAI for providing the GLM-4.7-Flash API
- DuckDuckGo for the search API
- Model Context Protocol team for the specification
