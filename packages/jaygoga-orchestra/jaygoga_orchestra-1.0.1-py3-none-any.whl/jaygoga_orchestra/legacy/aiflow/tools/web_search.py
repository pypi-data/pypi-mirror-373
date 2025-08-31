"""
Web Search Tool for AIFlow agents.

Provides real web search capabilities using multiple search engines.
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus
from .base_tool import BaseTool


class WebSearchTool(BaseTool):
    """
    Web search tool that provides agents with real-time web search capabilities.
    
    Supports multiple search engines and returns structured results.
    """
    
    def __init__(
        self,
        search_engine: str = "serper",
        max_results: int = 5,
        timeout: int = 10,
        api_key: Optional[str] = None
    ):
        """
        Initialize the web search tool.

        Args:
            search_engine: Search engine to use ("serper", "duckduckgo", "bing")
            max_results: Maximum number of search results to return
            timeout: Request timeout in seconds
            api_key: API key for search services (Serper, Bing, etc.)
        """
        super().__init__(
            name="web_search",
            description="Search the web for current information on any topic using real APIs"
        )
        self.search_engine = search_engine
        self.max_results = max_results
        self.timeout = timeout
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
    
    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a web search.
        
        Args:
            query: Search query string
            **kwargs: Additional parameters
            
        Returns:
            Dict containing search results
        """
        try:
            if self.search_engine == "serper":
                results = await self._search_serper(query)
            elif self.search_engine == "duckduckgo":
                results = await self._search_duckduckgo(query)
            elif self.search_engine == "bing":
                results = await self._search_bing(query)
            else:
                results = await self._search_serper(query)  # Default to Serper

            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "search_engine": self.search_engine
            }
            
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "results": []
            }
    
    async def _search_duckduckgo(self, query: str) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo with real API calls only."""
        # Try instant answer API first
        try:
            results = await self._search_duckduckgo_instant(query)
            if results:
                return results
        except Exception as e:
            print(f"DuckDuckGo instant API failed: {e}")

        # Fallback to HTML scraping
        try:
            results = await self._search_duckduckgo_html(query)
            if results:
                return results
        except Exception as e:
            print(f"DuckDuckGo HTML scraping failed: {e}")

        # NO SIMULATION - Return empty results with clear error
        raise Exception(f"All web search methods failed for query: '{query}'. No simulation results provided.")

    async def _search_serper(self, query: str) -> List[Dict[str, Any]]:
        """Search using Serper Google Search API."""
        if not self.api_key:
            raise Exception("Serper API key not provided. Set SERPER_API_KEY environment variable or pass api_key parameter.")

        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": self.max_results
        }

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []

                    # Process organic search results
                    for item in data.get("organic", [])[:self.max_results]:
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "source": "Serper Google Search"
                        })

                    return results
                else:
                    error_text = await response.text()
                    raise Exception(f"Serper API returned status {response.status}: {error_text}")

    async def _search_duckduckgo_instant(self, query: str) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo Instant Answer API."""
        encoded_query = quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []

                    # Extract instant answer
                    if data.get("Abstract"):
                        results.append({
                            "title": data.get("AbstractText", "")[:100] + "...",
                            "url": data.get("AbstractURL", ""),
                            "snippet": data.get("Abstract", ""),
                            "source": "DuckDuckGo Instant Answer"
                        })

                    # Extract related topics
                    for topic in data.get("RelatedTopics", [])[:self.max_results-1]:
                        if isinstance(topic, dict) and "Text" in topic:
                            results.append({
                                "title": topic.get("Text", "")[:100] + "...",
                                "url": topic.get("FirstURL", ""),
                                "snippet": topic.get("Text", ""),
                                "source": "DuckDuckGo Related"
                            })

                    return results[:self.max_results]
                else:
                    raise Exception(f"DuckDuckGo API returned status {response.status}")
    
    async def _search_duckduckgo_html(self, query: str) -> List[Dict[str, Any]]:
        """Fallback HTML scraping for DuckDuckGo."""
        encoded_query = quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    # Simple HTML parsing for search results
                    results = []
                    
                    # This is a simplified parser - in production you'd use BeautifulSoup
                    import re
                    
                    # Extract search result patterns
                    pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
                    matches = re.findall(pattern, html)
                    
                    for i, (url, title) in enumerate(matches[:self.max_results]):
                        if url and title:
                            results.append({
                                "title": title.strip(),
                                "url": url,
                                "snippet": f"Search result for: {query}",
                                "source": "DuckDuckGo HTML"
                            })
                    
                    return results
                else:
                    return []


    
    async def _search_bing(self, query: str) -> List[Dict[str, Any]]:
        """Search using Bing Web Search API (requires API key)."""
        # This would require a Bing API key
        # For now, fallback to DuckDuckGo
        return await self._search_duckduckgo(query)
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for web search."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute"
                }
            },
            "required": ["query"]
        }
    
    def format_results_for_llm(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results for LLM consumption.
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Formatted string of search results
        """
        if not results:
            return "No search results found."
        
        formatted = "Web Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result.get('title', 'No title')}**\n"
            formatted += f"   URL: {result.get('url', 'No URL')}\n"
            formatted += f"   Summary: {result.get('snippet', 'No summary')}\n"
            formatted += f"   Source: {result.get('source', 'Unknown')}\n\n"
        
        return formatted
