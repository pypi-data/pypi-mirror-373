"""
Spider MCP Client - Main client class
"""

import time
import uuid
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

from .exceptions import (
    SpiderMCPError,
    AuthenticationError,
    ParserNotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ConnectionError,
)


class SpiderMCPClient:
    """
    Official Python client for Spider MCP web scraping API.
    
    Provides easy access to Spider MCP's powerful web scraping capabilities
    with built-in error handling, rate limiting, and retry logic.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8003",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_delay: float = 1.0,
        app_name: Optional[str] = None
    ):
        """
        Initialize Spider MCP client.

        Args:
            api_key: Your Spider MCP API key
            base_url: Base URL of Spider MCP server (default: http://localhost:8003)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            rate_limit_delay: Minimum delay between requests in seconds (default: 1.0)
            app_name: Optional application name for session isolation
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = None

        # Generate unique session ID for this client instance
        self.session_id = str(uuid.uuid4())
        self.app_name = app_name or "spider_mcp_client"

        # Setup session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
            'User-Agent': f'spider-mcp-client/{self._get_version()}'
        })
    
    def _get_version(self) -> str:
        """Get client version"""
        try:
            from . import __version__
            return __version__
        except ImportError:
            return "unknown"
    
    def _wait_if_needed(self):
        """Ensure minimum delay between requests for rate limiting"""
        if self.last_request_time and self.rate_limit_delay > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response JSON data
            
        Raises:
            Various SpiderMCPError subclasses based on error type
        """
        self._wait_if_needed()
        
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                self.last_request_time = time.time()
                
                # Handle different status codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 404:
                    raise ServerError("Endpoint not found")
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code >= 500:
                    raise ServerError(f"Server error: {response.status_code}")
                else:
                    # Try to get error message from response
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('detail', f'HTTP {response.status_code}')
                    except:
                        error_msg = f'HTTP {response.status_code}: {response.text}'
                    raise SpiderMCPError(error_msg)
                    
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise TimeoutError(f"Request timed out after {self.timeout} seconds")
                    
            except requests.exceptions.ConnectionError:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(f"Failed to connect to {self.base_url}")
                    
            except (AuthenticationError, ParserNotFoundError, RateLimitError) as e:
                # Don't retry these errors
                raise e
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise SpiderMCPError(f"Unexpected error: {str(e)}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = (2 ** attempt) * self.rate_limit_delay
                time.sleep(wait_time)
        
        raise SpiderMCPError("Max retries exceeded")
    
    def parse_url(
        self,
        url: str,
        download_images: bool = False,
        session_name: Optional[str] = None,
        retry: int = 1
    ) -> Dict[str, Any]:
        """
        Parse a URL and extract structured data.

        Args:
            url: URL to parse
            download_images: Whether to download and localize images (default: False)
            session_name: Optional session name for additional isolation
            retry: Number of retry attempts on failure (default: 1, 0=no retry, 2+=multiple retries)

        Returns:
            Dictionary containing extracted data with structure:
            {
                'status': 'success|error',
                'url': str,
                'html_data': dict,  # Parsed HTML data
                'api_calls': list,  # Captured API calls
                'downloaded_images': list,  # Downloaded images
                'status_detail': dict  # Metadata and status info
            }

        Raises:
            ParserNotFoundError: If no parser exists for the URL
            AuthenticationError: If API key is invalid
            SpiderMCPError: For other errors
        """
        data = {
            'url': url,
            'download_images': download_images,
            'session_id': self.session_id,
            'app_name': self.app_name
        }

        if session_name:
            data['session_name'] = session_name

        # Retry logic - attempt parse_url with exponential backoff
        last_exception = None
        max_attempts = max(1, retry + 1)  # retry=0 means 1 attempt, retry=1 means 2 attempts, etc.

        for attempt in range(max_attempts):
            try:
                # Add attempt info to session_name for debugging
                if attempt > 0:
                    attempt_session_name = f"{session_name or 'retry'}_{attempt + 1}"
                    data['session_name'] = attempt_session_name

                result = self._make_request('POST', '/parse_url', json=data)

                # Check if result contains an error
                if isinstance(result, dict) and result.get('status') == 'error':
                    error_detail = result.get('status_detail', {})
                    error_msg = error_detail.get('error', result.get('error', 'Unknown error'))

                    if 'no parser' in error_msg.lower():
                        # Parser not found - don't retry, raise immediately
                        raise ParserNotFoundError(f"No parser found for URL: {url}")
                    else:
                        # Other errors - might be retryable
                        if attempt < max_attempts - 1:
                            # Not the last attempt, save exception and continue
                            last_exception = SpiderMCPError(error_msg)
                            continue
                        else:
                            # Last attempt, raise the error
                            raise SpiderMCPError(error_msg)

                # Success - return result
                return result

            except (AuthenticationError, ParserNotFoundError):
                # Don't retry authentication or parser not found errors
                raise
            except (RateLimitError, ServerError, TimeoutError, ConnectionError, SpiderMCPError) as e:
                # These errors might be retryable
                last_exception = e
                if attempt < max_attempts - 1:
                    # Not the last attempt, wait and retry
                    wait_time = (2 ** attempt) * 0.5  # Exponential backoff: 0.5s, 1s, 2s, 4s...
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt, raise the error
                    raise
            except Exception as e:
                # Unknown exception
                last_exception = SpiderMCPError(f"Failed to parse URL: {str(e)}")
                if attempt < max_attempts - 1:
                    # Not the last attempt, wait and retry
                    wait_time = (2 ** attempt) * 0.5
                    time.sleep(wait_time)
                    continue
                else:
                    # Last attempt, raise the error
                    raise last_exception

        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        else:
            raise SpiderMCPError(f"Failed to parse URL after {max_attempts} attempts")
    
    def check_parser(self, url: str) -> Dict[str, Any]:
        """
        Check if a parser exists for the given URL.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with parser information or availability status
        """
        try:
            result = self._make_request('POST', '/parsers/by_url', json={'url': url})
            return result
        except Exception as e:
            raise SpiderMCPError(f"Failed to check parser: {str(e)}")
    
    def get_parsers(self) -> List[Dict[str, Any]]:
        """
        Get list of all available parsers.
        
        Returns:
            List of parser dictionaries
        """
        try:
            result = self._make_request('GET', '/parsers')
            return result.get('parsers', [])
        except Exception as e:
            raise SpiderMCPError(f"Failed to get parsers: {str(e)}")
    
    def close(self):
        """Close the HTTP session"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
