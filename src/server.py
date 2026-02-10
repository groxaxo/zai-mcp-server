#!/usr/bin/env python3
"""
ZAI MCP Server - Web search and summarization using GLM-4.7-Flash
"""

import json
import os
import sys
from typing import Any, Dict, List
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from openai import AsyncOpenAI

ZAI_API_KEY = os.environ.get("ZAI_API_KEY", "")
ZAI_BASE_URL = "https://api.z.ai/api/paas/v4"


class ZAIMCPServer:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=ZAI_API_KEY, base_url=ZAI_BASE_URL)

    async def search_web(
        self, query: str, num_results: int = 5
    ) -> List[Dict[str, str]]:
        """Search web using DuckDuckGo"""
        search_url = f"https://duckduckgo.com/html/?q={query}"

        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; MCP-ZAI-Server/1.0)"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {response.status}")

                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    results = []

                    for result in soup.find_all("div", class_="result")[:num_results]:
                        title_elem = result.find(class_="result__title")
                        url_elem = result.find("a", class_="result__url")
                        snippet_elem = result.find(class_="result__snippet")

                        title = title_elem.get_text(strip=True) if title_elem else ""
                        url = url_elem.get("href", "") if url_elem else ""
                        snippet = (
                            snippet_elem.get_text(strip=True) if snippet_elem else ""
                        )

                        if url:
                            results.append(
                                {
                                    "title": title,
                                    "url": url,
                                    "snippet": snippet[:200] if snippet else "",
                                }
                            )

                    return results
        except Exception as e:
            print(f"Search error: {e}", file=sys.stderr)
            return []

    async def fetch_website(self, url: str) -> Dict[str, str]:
        """Fetch website content"""
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MCP-ZAI-Server/1.0)"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {response.status}")

                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    for element in soup(["script", "style", "nav", "footer", "header"]):
                        element.decompose()

                    title = (
                        soup.title.string
                        if soup.title
                        else soup.h1.string
                        if soup.h1
                        else url
                    )

                    content = soup.body.get_text() if soup.body else ""
                    content = " ".join(content.split())[:10000]

                    return {
                        "content": content,
                        "title": title.strip() if title else url,
                    }
        except Exception as e:
            raise Exception(f"Failed to fetch {url}: {str(e)}")

    async def summarize_with_glm(self, content: str, url: str) -> str:
        """Summarize content using GLM-4.7-Flash"""
        try:
            response = await self.client.chat.completions.create(
                model="glm-4.7-flash",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes web content. Provide clear, concise summaries highlighting main points. Use bullet points when appropriate.",
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize the following content from {url}:\n\n{content}",
                    },
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            return (
                response.choices[0].message.content
                if response.choices
                else "Unable to generate summary."
            )
        except Exception as e:
            print(f"GLM error: {e}", file=sys.stderr)
            raise Exception(f"Failed to summarize: {str(e)}")

    async def handle_search_web(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_web tool"""
        query = args.get("query")
        num_results = args.get("num_results", 5)

        if not query:
            raise Exception("Query is required")

        results = await self.search_web(query, min(num_results, 10))

        return {
            "query": query,
            "count": len(results),
            "results": [
                {
                    "title": r["title"],
                    "url": r["url"],
                    "snippet": r["snippet"],
                }
                for r in results
            ],
        }

    async def handle_fetch_and_summarize(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fetch_and_summarize tool"""
        url = args.get("url")

        if not url:
            raise Exception("URL is required")

        from urllib.parse import urlparse

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise Exception("Invalid URL format")

        website_data = await self.fetch_website(url)
        summary = await self.summarize_with_glm(website_data["content"], url)

        return {
            "url": url,
            "title": website_data["title"],
            "summary": summary,
            "content_length": len(website_data["content"]),
        }

    async def handle_search_and_summarize(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_and_summarize tool"""
        query = args.get("query")
        result_index = args.get("result_index", 1) - 1

        if not query:
            raise Exception("Query is required")

        results = await self.search_web(query, 10)

        if not results:
            return {"query": query, "error": "No search results found"}

        target_result = results[min(result_index, len(results) - 1)]
        website_data = await self.fetch_website(target_result["url"])
        summary = await self.summarize_with_glm(
            website_data["content"], target_result["url"]
        )

        return {
            "query": query,
            "result_index": result_index + 1,
            "url": target_result["url"],
            "title": website_data["title"],
            "summary": summary,
            "total_results": len(results),
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return available tools"""
        return [
            {
                "name": "search_web",
                "description": "Search the web for information using DuckDuckGo",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {
                            "type": "number",
                            "description": "Number of results (default: 5, max: 10)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 10,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "fetch_and_summarize",
                "description": "Fetch a website URL and summarize its content using GLM-4.7-Flash",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Website URL to fetch and summarize",
                        },
                        "max_content_length": {
                            "type": "number",
                            "description": "Maximum content length (default: 10000)",
                            "default": 10000,
                            "minimum": 1000,
                            "maximum": 50000,
                        },
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "search_and_summarize",
                "description": "Search the web, fetch top result, and summarize using GLM-4.7-Flash",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "result_index": {
                            "type": "number",
                            "description": "Which result to fetch (default: 1)",
                            "default": 1,
                            "minimum": 1,
                            "maximum": 10,
                        },
                    },
                    "required": ["query"],
                },
            },
        ]

    def get_resources(self) -> List[Dict[str, Any]]:
        """Return available resources"""
        return [
            {
                "uri": "zai://status",
                "name": "Server Status",
                "description": "Current status of ZAI MCP server",
                "mimeType": "application/json",
            }
        ]

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource"""
        if uri == "zai://status":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(
                    {
                        "status": "online",
                        "model": "glm-4.7-flash",
                        "api_endpoint": ZAI_BASE_URL,
                        "tools": [
                            "search_web",
                            "fetch_and_summarize",
                            "search_and_summarize",
                        ],
                    },
                    indent=2,
                ),
            }

        raise Exception(f"Unknown resource: {uri}")

    async def run(self):
        """Run the MCP server"""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                message = json.loads(line.strip())

                if message.get("method") == "tools/list":
                    result = {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "result": {"tools": self.get_tools()},
                    }
                elif message.get("method") == "resources/list":
                    result = {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "result": {"resources": self.get_resources()},
                    }
                elif message.get("method") == "resources/read":
                    uri = message["params"].get("uri")
                    try:
                        resource = await self.read_resource(uri)
                        result = {
                            "jsonrpc": "2.0",
                            "id": message.get("id"),
                            "result": {"contents": [resource]},
                        }
                    except Exception as e:
                        result = {
                            "jsonrpc": "2.0",
                            "id": message.get("id"),
                            "error": {"code": -32602, "message": str(e)},
                        }
                elif message.get("method") == "tools/call":
                    name = message["params"].get("name")
                    arguments = message["params"].get("arguments", {})

                    try:
                        if name == "search_web":
                            result_data = await self.handle_search_web(arguments)
                        elif name == "fetch_and_summarize":
                            result_data = await self.handle_fetch_and_summarize(
                                arguments
                            )
                        elif name == "search_and_summarize":
                            result_data = await self.handle_search_and_summarize(
                                arguments
                            )
                        else:
                            raise Exception(f"Unknown tool: {name}")

                        result = {
                            "jsonrpc": "2.0",
                            "id": message.get("id"),
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result_data, indent=2),
                                    }
                                ]
                            },
                        }
                    except Exception as e:
                        result = {
                            "jsonrpc": "2.0",
                            "id": message.get("id"),
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps({"error": str(e)}, indent=2),
                                    }
                                ],
                                "isError": True,
                            },
                        }
                elif message.get("method") == "initialize":
                    result = {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}, "resources": {}},
                            "serverInfo": {
                                "name": "mcp-zai-server",
                                "version": "1.0.0",
                            },
                        },
                    }
                elif message.get("method") == "notifications/initialized":
                    continue
                else:
                    result = {
                        "jsonrpc": "2.0",
                        "id": message.get("id"),
                        "error": {"code": -32601, "message": "Method not found"},
                    }

                print(json.dumps(result), flush=True)

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Error processing message: {e}", file=sys.stderr)


async def main():
    if not ZAI_API_KEY:
        print("Error: ZAI_API_KEY environment variable is required", file=sys.stderr)
        sys.exit(1)

    server = ZAIMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
