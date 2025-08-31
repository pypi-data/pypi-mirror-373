#!/usr/bin/env python3
"""
Google Search MCP Server using FastMCP
A simple Python implementation for Google Custom Search API

This module provides a Model Context Protocol (MCP) server that integrates
with Google Custom Search API to perform web searches and extract webpage content.
"""

import os
import sys
import logging
import asyncio
from typing import Annotated, Optional, List, Dict, Any, Union

import httpx
from bs4 import BeautifulSoup
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables will be checked in main function
API_KEY: Optional[str] = None
SEARCH_ENGINE_ID: Optional[str] = None
PROXY_URL: Optional[str] = None

# Initialize FastMCP
mcp = FastMCP("Google Search Server")

# Configure HTTP client base configuration
client_config: Dict[str, Any] = {
    'timeout': 30.0,
    'follow_redirects': True,
    'headers': {
        'User-Agent': 'Google-Search-MCP/0.1.0 (Python)'
    }
}

@mcp.tool()
async def google_search(query: Annotated[str, "Search query string (required)"], 
                        num: Annotated[int, "Number of results to return (1-10, default: 5)"] = 5) -> List[Dict[str, str]]:
    """
    Perform a web search using Google Custom Search API.
    
    Args:
        query: Search query string (required)
        num: Number of results to return (1-10, default: 5)
    
    Returns:
        List of search results, each containing:
        - title: Page title
        - link: URL of the page
        - snippet: Brief description/excerpt
    
    Raises:
        Exception: If search fails due to network, API, or other errors
    """
    try:
        # Validate and clamp input parameters
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        
        num = min(max(num, 1), 10)  # Clamp between 1-10
        logger.info(f"Performing search for query: '{query}' (num={num})")
        
        async with httpx.AsyncClient(**client_config) as client:
            response = await client.get(
                'https://www.googleapis.com/customsearch/v1',
                params={
                    'key': API_KEY,
                    'cx': SEARCH_ENGINE_ID,
                    'q': query.strip(),
                    'num': num
                }
            )
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                logger.warning(f"No search results found for query: '{query}'")
                return []
            
            results = []
            for item in items:
                result = {
                    'title': item.get('title', '').strip(),
                    'link': item.get('link', '').strip(),
                    'snippet': item.get('snippet', '').strip()
                }
                results.append(result)
            
            logger.info(f"Successfully retrieved {len(results)} search results")
            return results
            
    except ValueError as e:
        logger.error(f"Invalid search parameters: {e}")
        raise Exception(f"Invalid search parameters: {e}")
    except httpx.TimeoutException as e:
        error_msg = f'Request timeout - check network connection and proxy settings'
        if PROXY_URL:
            error_msg += f' (Using proxy: {PROXY_URL})'
        logger.error(error_msg)
        raise Exception(error_msg)
    except httpx.ConnectError as e:
        error_msg = f'Connection failed - check proxy configuration'
        if PROXY_URL:
            error_msg += f' (Using proxy: {PROXY_URL})'
        logger.error(f"{error_msg}: {e}")
        raise Exception(error_msg)
    except httpx.HTTPStatusError as e:
        error_msg = f'API error: {e.response.status_code}'
        try:
            error_detail = e.response.json().get('error', {}).get('message', e.response.text)
            error_msg += f' - {error_detail}'
        except:
            error_msg += f' - {e.response.text}'
        if PROXY_URL:
            error_msg += f' (Using proxy: {PROXY_URL})'
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f'Search error: {str(e)}'
        if PROXY_URL:
            error_msg += f' (Using proxy: {PROXY_URL})'
        logger.error(error_msg)
        raise Exception(error_msg)

@mcp.tool()
async def read_webpage(url: Annotated[str, "URL of the webpage to read (required)"]) -> Dict[str, str]:
    """
    Fetch and extract text content from a webpage.
    
    Args:
        url: URL of the webpage to read (required)
    
    Returns:
        Dictionary containing:
        - title: Page title
        - text: Extracted text content (cleaned)
        - url: Original URL
    
    Raises:
        Exception: If webpage fetch fails due to network or parsing errors
    """
    try:
        # Validate URL
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")
        
        url = url.strip()
        if not (url.startswith('http://') or url.startswith('https://')):
            raise ValueError("URL must start with http:// or https://")
        
        logger.info(f"Fetching webpage: {url}")
        
        async with httpx.AsyncClient(**client_config) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
                element.decompose()
            
            # Extract title
            title_element = soup.find('title')
            title_text = title_element.get_text().strip() if title_element else 'No title'
            
            # Extract main content
            # Try to find main content areas first
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                text_content = ' '.join(main_content.get_text().split())
            else:
                # Fallback to body content
                body = soup.find('body')
                if body:
                    text_content = ' '.join(body.get_text().split())
                else:
                    text_content = ' '.join(soup.get_text().split())
            
            # Limit text length to prevent excessive output
            max_length = 10000
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + "... [content truncated]"
            
            result = {
                'title': title_text,
                'text': text_content,
                'url': url
            }
            
            logger.info(f"Successfully extracted content from {url} (title: '{title_text}', text length: {len(text_content)})")
            return result
            
    except ValueError as e:
        logger.error(f"Invalid URL parameter: {e}")
        raise Exception(f"Invalid URL parameter: {e}")
    except httpx.TimeoutException as e:
        error_msg = f'Request timeout while fetching {url} - check network connection and proxy settings'
        if PROXY_URL:
            error_msg += f' (Using proxy: {PROXY_URL})'
        logger.error(error_msg)
        raise Exception(error_msg)
    except httpx.ConnectError as e:
        error_msg = f'Connection failed while fetching {url} - check proxy configuration'
        if PROXY_URL:
            error_msg += f' (Using proxy: {PROXY_URL})'
        logger.error(f"{error_msg}: {e}")
        raise Exception(error_msg)
    except httpx.HTTPStatusError as e:
        error_msg = f'HTTP error {e.response.status_code} while fetching {url}'
        if PROXY_URL:
            error_msg += f' (Using proxy: {PROXY_URL})'
        logger.error(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f'Webpage fetch error for {url}: {str(e)}'
        if PROXY_URL:
            error_msg += f' (Using proxy: {PROXY_URL})'
        logger.error(error_msg)
        raise Exception(error_msg)

def main() -> None:
    """Main entry point for the Google Search MCP Server."""
    # Check for help flag first
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Google Search MCP Server")
        print("")
        print("A Model Context Protocol (MCP) server that provides Google Search functionality.")
        print("")
        print("Usage:")
        print("  google-search-mcp [options]")
        print("  python -m google_search_mcp [options]")
        print("")
        print("Options:")
        print("  -h, --help     Show this help message and exit")
        print("")
        print("Environment Variables:")
        print("  GOOGLE_API_KEY           Google Custom Search API key (required)")
        print("  GOOGLE_SEARCH_ENGINE_ID  Google Custom Search Engine ID (required)")
        print("  PROXY_URL               HTTP/SOCKS proxy URL (optional)")
        return
    
    global API_KEY, SEARCH_ENGINE_ID, PROXY_URL
    
    # Initialize environment variables
    API_KEY = os.getenv('GOOGLE_API_KEY')
    SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    PROXY_URL = os.getenv('PROXY_URL')
    
    # Configure proxy if provided
    if PROXY_URL:
        client_config['proxy'] = PROXY_URL
        logger.info(f"Using proxy: {PROXY_URL}")
    
    # Validate required environment variables
    if not API_KEY:
        logger.error('GOOGLE_API_KEY environment variable is required')
        raise ValueError('GOOGLE_API_KEY environment variable is required')

    if not SEARCH_ENGINE_ID:
        logger.error('GOOGLE_SEARCH_ENGINE_ID environment variable is required')
        raise ValueError('GOOGLE_SEARCH_ENGINE_ID environment variable is required')

    logger.info('Google Search MCP Server initialized successfully')
    
    try:
        logger.info("Starting Google Search MCP Server...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()