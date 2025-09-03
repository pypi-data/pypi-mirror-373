"""
Spider MCP Client Exceptions
"""


class SpiderMCPError(Exception):
    """Base exception for Spider MCP client errors"""
    pass


class AuthenticationError(SpiderMCPError):
    """Raised when API key authentication fails"""
    pass


class ParserNotFoundError(SpiderMCPError):
    """Raised when no parser is found for the given URL"""
    pass


class RateLimitError(SpiderMCPError):
    """Raised when rate limit is exceeded"""
    pass


class ServerError(SpiderMCPError):
    """Raised when server returns an error"""
    pass


class TimeoutError(SpiderMCPError):
    """Raised when request times out"""
    pass


class ConnectionError(SpiderMCPError):
    """Raised when connection to server fails"""
    pass
