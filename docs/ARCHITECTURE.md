# Architecture

## Overview

The ZAI MCP Server implements the Model Context Protocol (MCP) to provide web search and content summarization capabilities powered by ZAI's GLM-4.7-Flash model.

## Components

### 1. Core Server (`src/server.py`)

**ZAIMCPServer Class**

The main class that handles MCP protocol communication:

- `__init__()`: Initialize OpenAI client with ZAI credentials
- `search_web()`: Perform web searches via DuckDuckGo
- `fetch_website()`: Fetch and parse HTML content
- `summarize_with_glm()`: Generate summaries using GLM-4.7-Flash
- `handle_*()`: Tool-specific request handlers
- `get_tools()`: Return available tool definitions
- `get_resources()`: Return server resources
- `read_resource()`: Handle resource requests
- `run()`: Main MCP server loop

### 2. Protocol Handlers

**JSON-RPC 2.0 Methods**

| Method | Description |
|---------|-------------|
| `initialize` | Server initialization handshake |
| `tools/list` | List available tools |
| `tools/call` | Execute a tool |
| `resources/list` | List available resources |
| `resources/read` | Read a resource |
| `notifications/initialized` | Notification that initialization is complete |

### 3. Web Search Module

Uses DuckDuckGo HTML interface for web search:

```python
search_url = "https://duckduckgo.com/html/?q={query}"
```

**Process:**
1. Fetch HTML results from DuckDuckGo
2. Parse with BeautifulSoup
3. Extract: title, URL, and snippet for each result
4. Return structured results

**Benefits:**
- No API key required
- No rate limits (based on HTTP)
- Clean, structured results

### 4. Content Fetcher

Fetches and processes web content:

**Steps:**
1. Send HTTP GET request with proper User-Agent
2. Parse HTML with BeautifulSoup
3. Remove unwanted elements (scripts, styles, ads, navigation)
4. Extract body text
5. Clean and normalize whitespace
6. Limit to maximum length (default: 10,000 chars)

**Cleaning Rules:**
- Remove: `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, `<aside>`
- Remove elements with "ad" in class name
- Normalize whitespace (multiple spaces to single space)
- Trim to specified length

### 5. Summarization Module

Uses ZAI's GLM-4.7-Flash model:

**API Call:**
```python
response = await client.chat.completions.create(
    model="glm-4.7-flash",
    messages=[...],
    max_tokens=1000,
    temperature=0.7
)
```

**System Prompt:**
```
"You are a helpful assistant that summarizes web content. Provide clear, 
concise summaries highlighting main points. Use bullet points when appropriate."
```

**Model Selection:**
- GLM-4.7-Flash: Fast responses, good for summarization
- Temperature: 0.7 (balanced creativity and accuracy)
- Max Tokens: 1000 (enough for detailed summaries)

### 6. Tool Implementations

#### search_web

**Flow:**
1. Validate input (query required)
2. Call DuckDuckGo search
3. Format results as JSON
4. Return structured response

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {"type": "string"},
    "num_results": {"type": "number", "default": 5}
  },
  "required": ["query"]
}
```

#### fetch_and_summarize

**Flow:**
1. Validate input (URL required, check URL format)
2. Fetch website content
3. Clean and extract text
4. Call GLM-4.7-Flash for summarization
5. Return summary with metadata

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "url": {"type": "string"},
    "max_content_length": {"type": "number", "default": 10000}
  },
  "required": ["url"]
}
```

#### search_and_summarize

**Flow:**
1. Validate input (query required)
2. Search web (get top 10 results)
3. Validate result index
4. Fetch target result's content
5. Summarize with GLM-4.7-Flash
6. Return combined results

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {"type": "string"},
    "result_index": {"type": "number", "default": 1}
  },
  "required": ["query"]
}
```

### 7. Resource Management

**Available Resources:**

| URI | Type | Description |
|-----|------|-------------|
| `zai://status` | JSON | Server status and configuration |

**Status Resource Structure:**
```json
{
  "status": "online",
  "model": "glm-4.7-flash",
  "api_endpoint": "https://api.z.ai/api/paas/v4",
  "tools": ["search_web", "fetch_and_summarize", "search_and_summarize"]
}
```

### 8. Error Handling

**Error Categories:**

1. **Validation Errors**
   - Missing required parameters
   - Invalid URL format
   - Parameter out of range

2. **Network Errors**
   - HTTP connection failures
   - Timeouts (configured: 20s for search, 30s for fetch)
   - DNS resolution issues

3. **API Errors**
   - Invalid API key
   - Rate limits exceeded
   - Model unavailable
   - Quota exceeded

**Error Response Format:**
```json
{
  "jsonrpc": "2.0",
  "id": <request-id>,
  "result": {
    "content": [
      {
        "type": "text",
        "text": JSON.stringify({"error": "error message"})
      }
    ],
    "isError": true
  }
}
```

### 9. Configuration

**Environment Variables:**

| Variable | Description | Default | Required |
|----------|-------------|---------|-----------|
| `ZAI_API_KEY` | ZAI API key | - | Yes |
| `ZAI_DEBUG` | Enable debug logging | 0 | No |

**Hardcoded Configuration:**

```python
ZAI_BASE_URL = "https://api.z.ai/api/paas/v4"
MODEL = "glm-4.7-flash"
MAX_TOKENS = 1000
TEMPERATURE = 0.7
MAX_CONTENT_LENGTH = 10000
SEARCH_TIMEOUT = 20  # seconds
FETCH_TIMEOUT = 30  # seconds
```

### 10. Performance Considerations

**Optimizations:**

1. **Async Operations**
   - All I/O operations use aiohttp
   - Non-blocking for better concurrency
   - Efficient handling of multiple requests

2. **Content Limiting**
   - Default 10,000 characters to prevent excessive processing
   - Prevents OOM on very large pages
   - Fast enough for summarization

3. **Connection Pooling**
   - aiohttp manages connection reuse
   - Reduces TLS handshake overhead
   - Better for repeated requests

4. **Caching Opportunities**
   - DuckDuckGo results could be cached
   - Frequently fetched URLs could be cached
   - Implement in future versions

### 11. Security

**Security Measures:**

1. **API Key Protection**
   - Never logged to stdout
   - Environment variable only
   - Not included in error messages

2. **Content Sanitization**
   - Removes scripts and styles
   - No code execution
   - Text-only output

3. **URL Validation**
   - urllib.parse for URL validation
   - Prevents SSRF attacks
   - Only HTTP/HTTPS schemes allowed

4. **Rate Limiting**
   - Respects DuckDuckGo's implicit limits
   - Can be enhanced with explicit rate limiting
   - Prevents abuse

### 12. Extensibility

**Adding New Tools:**

1. Define tool in `get_tools()`
2. Implement handler method
3. Add case in `tools/call` handler
4. Update documentation

**Example:**
```python
def get_tools(self) -> List[Dict[str, Any]]:
    return [
        # existing tools...
        {
            "name": "my_new_tool",
            "description": "Description here",
            "inputSchema": {...}
        }
    ]

async def handle_my_new_tool(self, args: Dict[str, Any]):
    # Implementation
    pass

# In run() method:
elif message.get("method") == "tools/call":
    name = message["params"].get("name")
    if name == "my_new_tool":
        result_data = await self.handle_my_new_tool(arguments)
```

### 13. Testing Strategy

**Test Coverage:**

1. **Unit Tests** (planned)
   - Test each method in isolation
   - Mock external dependencies
   - Verify error handling

2. **Integration Tests**
   - Test full MCP protocol flow
   - Verify JSON-RPC responses
   - Check tool execution

3. **End-to-End Tests**
   - Test with actual MCP clients
   - Verify real web searches
   - Check summarization quality

### 14. Deployment

**Requirements:**
- Python 3.8+
- Stable internet connection
- Valid ZAI API key
- ~50MB disk space

**Recommended Deployment:**

1. **Development**: Run directly with Python
2. **Production**: Use process manager (systemd, supervisord)
3. **Docker**: Create container image (future)
4. **Serverless**: Deploy to AWS Lambda/Azure Functions (future)

## Data Flow

### Typical Request Flow

```
User Request
    ↓
[MCP Client] → [ZAI MCP Server]
    ↓
Validation → Tool Selection
    ↓
DuckDuckGo Search / Web Fetch
    ↓
GLM-4.7-Flash API Call
    ↓
Summary Generation
    ↓
[MCP Client] ← [Response]
    ↓
Display to User
```

### Error Recovery Flow

```
Error Detected
    ↓
Log Error to stderr
    ↓
Return Error Response
    ↓
[MCP Client] Receives Error
    ↓
Retry or Display Error Message
```

## Future Enhancements

1. **Caching Layer**
   - Redis or in-memory cache
   - TTL-based expiration
   - Reduces API calls

2. **Additional Search Providers**
   - Google Custom Search API
   - Bing Search API
   - User-selectable providers

3. **Advanced Summarization**
   - Multi-page summarization
   - Comparative summarization
   - Custom length parameters

4. **Streaming Responses**
   - Stream GLM responses
   - Real-time summarization
   - Better UX for long content

5. **Metrics & Monitoring**
   - Request counting
   - Success/failure rates
   - Performance metrics
