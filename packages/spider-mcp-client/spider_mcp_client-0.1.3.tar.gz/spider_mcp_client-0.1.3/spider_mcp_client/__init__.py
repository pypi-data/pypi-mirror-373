"""
Spider MCP Client - Official Python client for Spider MCP web scraping API
"""

__version__ = "0.1.3"
__author__ = "importal"
__email__ = "xychen@msn.com"

from .client import SpiderMCPClient
from .exceptions import (
    SpiderMCPError,
    AuthenticationError,
    ParserNotFoundError,
    RateLimitError,
    ServerError,
)

__all__ = [
    "SpiderMCPClient",
    "SpiderMCPError",
    "AuthenticationError", 
    "ParserNotFoundError",
    "RateLimitError",
    "ServerError",
]
