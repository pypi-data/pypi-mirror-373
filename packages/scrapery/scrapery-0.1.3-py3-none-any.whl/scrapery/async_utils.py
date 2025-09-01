import aiohttp
import asyncio
from typing import Optional, Dict, Any
from .exceptions import NetworkError
from .utils import validate_input

async def fetch_url(
    url: str, 
    session: Optional[aiohttp.ClientSession] = None, 
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    max_redirects: int = 10
) -> str:
    """
    Asynchronously fetch URL content with comprehensive error handling.
    
    Args:
        url: URL to fetch
        session: Optional aiohttp session
        headers: Optional request headers
        timeout: Request timeout in seconds
        max_redirects: Maximum number of redirects to follow
    
    Returns:
        Fetched content as string
    """
    validate_input(url, str)
    
    headers = headers or {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        if session is None:
            connector = aiohttp.TCPConnector(limit=100, ssl=False)
            async with aiohttp.ClientSession(
                connector=connector, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as temp_session:
                async with temp_session.get(
                    url, 
                    allow_redirects=True, 
                    max_redirects=max_redirects
                ) as response:
                    if response.status != 200:
                        raise NetworkError(f"HTTP {response.status}: {response.reason}")
                    return await response.text()
        else:
            async with session.get(
                url, 
                allow_redirects=True, 
                max_redirects=max_redirects
            ) as response:
                if response.status != 200:
                    raise NetworkError(f"HTTP {response.status}: {response.reason}")
                return await response.text()
    except asyncio.TimeoutError:
        raise NetworkError(f"Request timeout for URL: {url}")
    except aiohttp.ClientError as e:
        raise NetworkError(f"Network error for URL {url}: {str(e)}")
    except Exception as e:
        raise NetworkError(f"Unexpected error fetching URL {url}: {str(e)}")

async def fetch_multiple_urls(
    urls: list, 
    concurrency: int = 10,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Fetch multiple URLs concurrently with rate limiting.
    
    Args:
        urls: List of URLs to fetch
        concurrency: Maximum concurrent requests
        headers: Optional request headers
        timeout: Request timeout in seconds
    
    Returns:
        Dictionary with results and errors
    """
    validate_input(urls, list)
    
    semaphore = asyncio.Semaphore(concurrency)
    results = {}
    errors = {}
    
    async def fetch_with_semaphore(url):
        async with semaphore:
            try:
                content = await fetch_url(url, None, headers, timeout)
                results[url] = content
            except NetworkError as e:
                errors[url] = str(e)
    
    tasks = [fetch_with_semaphore(url) for url in urls]
    await asyncio.gather(*tasks)
    
    return {
        'results': results,
        'errors': errors,
        'success_count': len(results),
        'error_count': len(errors)
    }

# 👇 Explicitly define public API
__all__ = [
    "fetch_url",
    "fetch_multiple_urls",
]    