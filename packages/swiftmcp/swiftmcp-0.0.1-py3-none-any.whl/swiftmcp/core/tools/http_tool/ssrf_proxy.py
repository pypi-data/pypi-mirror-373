"""
Proxy requests to avoid SSRF
"""
import logging
import os
import time
from typing import Any, Dict

import httpx

# Configuration
SSRF_PROXY_ALL_URL = os.getenv('SSRF_PROXY_ALL_URL', '')
SSRF_PROXY_HTTP_URL = os.getenv('SSRF_PROXY_HTTP_URL', '')
SSRF_PROXY_HTTPS_URL = os.getenv('SSRF_PROXY_HTTPS_URL', '')
SSRF_DEFAULT_MAX_RETRIES = int(os.getenv('SSRF_DEFAULT_MAX_RETRIES', '3'))

# Proxy configuration
proxies = {
    'http://': SSRF_PROXY_HTTP_URL,
    'https://': SSRF_PROXY_HTTPS_URL
} if SSRF_PROXY_HTTP_URL and SSRF_PROXY_HTTPS_URL else None

# Retry configuration
BACKOFF_FACTOR = 0.5
STATUS_FORCELIST = [429, 500, 502, 503, 504]


def make_request(method: str, url: str, max_retries: int = SSRF_DEFAULT_MAX_RETRIES, **kwargs) -> httpx.Response:
    """
    Make HTTP request with retry logic.
    
    Args:
        method: HTTP method
        url: Request URL
        max_retries: Maximum number of retries
        **kwargs: Additional arguments for the request
        
    Returns:
        HTTP response
        
    Raises:
        Exception: If maximum retries exceeded
    """
    # Handle redirect parameter name change between libraries
    if "allow_redirects" in kwargs:
        allow_redirects = kwargs.pop("allow_redirects")
        if "follow_redirects" not in kwargs:
            kwargs["follow_redirects"] = allow_redirects

    retries = 0
    while retries <= max_retries:
        try:
            # Make request based on proxy configuration
            if SSRF_PROXY_ALL_URL:
                response = httpx.request(method=method, url=url, proxy=SSRF_PROXY_ALL_URL, **kwargs)
            elif proxies:
                response = httpx.request(method=method, url=url, proxies=proxies, **kwargs)
            else:
                response = httpx.request(method=method, url=url, **kwargs)

            # Check if we should retry based on status code
            if response.status_code not in STATUS_FORCELIST:
                return response
            else:
                logging.warning(
                    f"Received status code {response.status_code} for URL {url} which is in the force list"
                )

        except httpx.RequestError as e:
            logging.warning(f"Request to URL {url} failed on attempt {retries + 1}: {e}")

        # Wait before retry with exponential backoff
        retries += 1
        if retries <= max_retries:
            time.sleep(BACKOFF_FACTOR * (2 ** (retries - 1)))

    raise Exception(f"Reached maximum retries ({max_retries}) for URL {url}")


def get(url: str, max_retries: int = SSRF_DEFAULT_MAX_RETRIES, **kwargs) -> httpx.Response:
    """
    Make GET request.
    
    Args:
        url: Request URL
        max_retries: Maximum number of retries
        **kwargs: Additional arguments for the request
        
    Returns:
        HTTP response
    """
    return make_request('GET', url, max_retries=max_retries, **kwargs)


def post(url: str, max_retries: int = SSRF_DEFAULT_MAX_RETRIES, **kwargs) -> httpx.Response:
    """
    Make POST request.
    
    Args:
        url: Request URL
        max_retries: Maximum number of retries
        **kwargs: Additional arguments for the request
        
    Returns:
        HTTP response
    """
    return make_request('POST', url, max_retries=max_retries, **kwargs)


def put(url: str, max_retries: int = SSRF_DEFAULT_MAX_RETRIES, **kwargs) -> httpx.Response:
    """
    Make PUT request.
    
    Args:
        url: Request URL
        max_retries: Maximum number of retries
        **kwargs: Additional arguments for the request
        
    Returns:
        HTTP response
    """
    return make_request('PUT', url, max_retries=max_retries, **kwargs)


def patch(url: str, max_retries: int = SSRF_DEFAULT_MAX_RETRIES, **kwargs) -> httpx.Response:
    """
    Make PATCH request.
    
    Args:
        url: Request URL
        max_retries: Maximum number of retries
        **kwargs: Additional arguments for the request
        
    Returns:
        HTTP response
    """
    return make_request('PATCH', url, max_retries=max_retries, **kwargs)


def delete(url: str, max_retries: int = SSRF_DEFAULT_MAX_RETRIES, **kwargs) -> httpx.Response:
    """
    Make DELETE request.
    
    Args:
        url: Request URL
        max_retries: Maximum number of retries
        **kwargs: Additional arguments for the request
        
    Returns:
        HTTP response
    """
    return make_request('DELETE', url, max_retries=max_retries, **kwargs)


def head(url: str, max_retries: int = SSRF_DEFAULT_MAX_RETRIES, **kwargs) -> httpx.Response:
    """
    Make HEAD request.
    
    Args:
        url: Request URL
        max_retries: Maximum number of retries
        **kwargs: Additional arguments for the request
        
    Returns:
        HTTP response
    """
    return make_request('HEAD', url, max_retries=max_retries, **kwargs)