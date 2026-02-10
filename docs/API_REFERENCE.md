# API Reference

Complete API reference for ZAI MCP Server.

## MCP Protocol

The server implements Model Context Protocol (MCP) following the JSON-RPC 2.0 specification.

### Initialization

**Method:** `initialize`

Initialize the MCP server and exchange capabilities.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": {
        "listChanged": true
      },
      "sampling": {}
    },
    "clientInfo": {
      "name": "client-name",
      "version": "1.0.0"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {},
      "resources": {}
    },
    "serverInfo": {
      "name": "mcp-zai-server",
      "version": "1.0.0"
    }
  }
}
```

### Tools

#### List Tools

**Method:** `tools/list`

Retrieve all available tools.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "search_web",
        "description": "Search web for information using DuckDuckGo",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "Search query"
            },
            "num_results": {
              "type": "number",
              "description": "Number of results (default: 5, max: 10)",
              "default": 5,
              "minimum": 1,
              "maximum": 10
            }
          },
          "required": ["query"]
        }
      }
    ]
  }
}
```

#### Call Tool

**Method:** `tools/call`

Execute a tool with given parameters.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "search_web",
    "arguments": {
      "query": "machine learning",
      "num_results": 5
    }
  }
}
```

**Response (Success):**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"query\": \"machine learning\",\n  \"count\": 5,\n  \"results\": [...]\n}"
      }
    ]
  }
}
```

**Response (Error):**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"error\": \"Query is required\"}"
      }
    ],
    "isError": true
  }
}
```

### Resources

#### List Resources

**Method:** `resources/list`

Retrieve all available resources.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/list",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "resources": [
      {
        "uri": "zai://status",
        "name": "Server Status",
        "description": "Current status of ZAI MCP server",
        "mimeType": "application/json"
      }
    ]
  }
}
```

#### Read Resource

**Method:** `resources/read`

Read a specific resource.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/read",
  "params": {
    "uri": "zai://status"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "contents": [
      {
        "uri": "zai://status",
        "mimeType": "application/json",
        "text": "{\"status\": \"online\", \"model\": \"glm-4.7-flash\", ...}"
      }
    ]
  }
}
```

## Tool Schemas

### search_web

Searches the web using DuckDuckGo.

**Input Schema:**

| Property | Type | Required | Default | Description |
|----------|------|-----------|---------|-------------|
| `query` | string | Yes | - | Search query |
| `num_results` | number | No | 5 | Number of results (1-10) |

**Output Schema:**

```json
{
  "query": "string",
  "count": "number",
  "results": [
    {
      "title": "string",
      "url": "string",
      "snippet": "string"
    }
  ]
}
```

**Error Conditions:**

- Missing `query` parameter
- Network timeout
- DuckDuckGo service unavailable

### fetch_and_summarize

Fetches a website and summarizes its content using GLM-4.7-Flash.

**Input Schema:**

| Property | Type | Required | Default | Description |
|----------|------|-----------|---------|-------------|
| `url` | string | Yes | - | Website URL to fetch |
| `max_content_length` | number | No | 10000 | Max content length (1000-50000) |

**Output Schema:**

```json
{
  "url": "string",
  "title": "string",
  "summary": "string",
  "content_length": "number"
}
```

**Error Conditions:**

- Missing `url` parameter
- Invalid URL format
- HTTP fetch failure
- GLM API error
- Content too large

### search_and_summarize

Searches the web and summarizes the top result.

**Input Schema:**

| Property | Type | Required | Default | Description |
|----------|------|-----------|---------|-------------|
| `query` | string | Yes | - | Search query |
| `result_index` | number | No | 1 | Which result to fetch (1-10) |

**Output Schema:**

```json
{
  "query": "string",
  "result_index": "number",
  "url": "string",
  "title": "string",
  "summary": "string",
  "total_results": "number"
}
```

**Error Conditions:**

- Missing `query` parameter
- No search results found
- `result_index` out of range
- HTTP fetch failure
- GLM API error

## Error Codes

### JSON-RPC Errors

| Code | Name | Description |
|-------|-------|-------------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid request | Invalid JSON-RPC request |
| -32601 | Method not found | Method does not exist |
| -32602 | Invalid params | Invalid method parameters |
| -32603 | Internal error | Internal JSON-RPC error |

### Server-Specific Errors

| Message | Cause | Solution |
|----------|--------|----------|
| "Query is required" | Missing query parameter | Provide query |
| "URL is required" | Missing URL parameter | Provide URL |
| "Invalid URL format" | Malformed URL | Check URL syntax |
| "No search results found" | Empty search results | Try different query |
| "Failed to fetch" | HTTP error | Check URL and network |
| "Failed to summarize" | GLM API error | Check API key and quota |

## Response Formats

### Content Type

All tool responses use the following content structure:

```json
{
  "content": [
    {
      "type": "text",
      "text": "JSON or plain text result"
    }
  ]
}
```

### Error Response

Error responses include `isError: true`:

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"error\": \"error message\"}"
    }
  ],
  "isError": true
}
```

## Limits

### Request Limits

- **Search timeout**: 20 seconds
- **Fetch timeout**: 30 seconds
- **Max content length**: 10,000 characters (configurable)
- **Max search results**: 10
- **GLM max tokens**: 1,000
- **GLM temperature**: 0.7

### Rate Limiting

- **DuckDuckGo**: Implicit HTTP rate limiting
- **ZAI API**: Based on your API plan
- **Concurrent requests**: Supported via async operations

## Metadata

### Server Information

```json
{
  "name": "mcp-zai-server",
  "version": "1.0.0",
  "protocolVersion": "2024-11-05",
  "capabilities": {
    "tools": {},
    "resources": {}
  }
}
```

### Tool Metadata

Each tool includes:
- `name`: Unique identifier
- `description`: Human-readable description
- `inputSchema`: JSON Schema for parameters
- `outputSchema`: JSON Schema for results (implicit)

## Examples

### Complete Workflow Example

**User:** "Search for latest AI news and summarize the top article"

**MCP Exchange:**

```json
// 1. List tools
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}

// 2. Call search_and_summarize
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "search_and_summarize",
    "arguments": {
      "query": "latest AI news",
      "result_index": 1
    }
  }
}

// 3. Receive summary
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{
      "type": "text",
      "text": JSON.stringify({
        "query": "latest AI news",
        "result_index": 1,
        "url": "https://example.com/ai-news",
        "title": "Major AI Breakthrough Announced",
        "summary": "• Researchers announced a significant breakthrough in...\n• The new model achieves 95% accuracy...\n• Applications expected in healthcare...",
        "total_results": 10
      })
    }]
  }
}
```

## Versioning

### Current Version: 1.0.0

- Initial release
- Core web search functionality
- GLM-4.7-Flash integration
- MCP protocol implementation
