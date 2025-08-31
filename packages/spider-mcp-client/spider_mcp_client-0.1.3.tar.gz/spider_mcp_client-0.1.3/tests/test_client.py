"""
Tests for Spider MCP Client
"""

import pytest
import requests_mock
from spider_mcp_client import SpiderMCPClient, ParserNotFoundError, AuthenticationError


class TestSpiderMCPClient:
    """Test cases for SpiderMCPClient"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = SpiderMCPClient(
            api_key="test-api-key",
            base_url="http://test-server:8003",
            rate_limit_delay=0  # No delay for tests
        )
    
    def test_client_initialization(self):
        """Test client initialization"""
        assert self.client.api_key == "test-api-key"
        assert self.client.base_url == "http://test-server:8003"
        assert self.client.timeout == 30
        assert self.client.max_retries == 3
    
    def test_parse_url_success(self, requests_mock):
        """Test successful URL parsing"""
        # Mock successful response
        mock_response = {
            "title": "Test Article",
            "content": "Test content here...",
            "author": "Test Author",
            "url": "https://example.com/article"
        }
        
        requests_mock.post("http://test-server:8003/parse_url", json=mock_response)

        result = self.client.parse_url("https://example.com/article")

        assert result["title"] == "Test Article"
        assert result["content"] == "Test content here..."
        assert result["author"] == "Test Author"

        # Check request was made correctly
        assert len(requests_mock.request_history) == 1
        request = requests_mock.request_history[0]
        assert request.headers["X-API-Key"] == "test-api-key"
        assert request.json()["url"] == "https://example.com/article"
    
    def test_parse_url_with_images(self, requests_mock):
        """Test URL parsing with image download"""
        mock_response = {
            "title": "Test Article",
            "content": "Test content...",
            "images": ["http://test-server:8003/downloaded_images/image1.jpg"]
        }
        
        requests_mock.post("http://test-server:8003/parse_url", json=mock_response)

        result = self.client.parse_url(
            "https://example.com/article",
            download_images=True
        )

        assert len(result["images"]) == 1
        assert "image1.jpg" in result["images"][0]

        # Check request included download_images=True
        request = requests_mock.request_history[0]
        assert request.json()["download_images"] is True
    
    def test_parser_not_found_error(self, requests_mock):
        """Test ParserNotFoundError handling"""
        mock_response = {
            "error": "No parser found for this URL",
            "status": "noparser"
        }
        
        requests_mock.post("http://test-server:8003/parse_url", json=mock_response)
        
        with pytest.raises(ParserNotFoundError):
            self.client.parse_url("https://unsupported-site.com/article")
    
    def test_authentication_error(self, requests_mock):
        """Test AuthenticationError handling"""
        requests_mock.post("http://test-server:8003/parse_url", status_code=401)
        
        with pytest.raises(AuthenticationError):
            self.client.parse_url("https://example.com/article")
    
    def test_check_parser(self, requests_mock):
        """Test parser availability check"""
        mock_response = {
            "found": True,
            "parser": {
                "id": 123,
                "site_name": "example.com",
                "url_name": "article"
            }
        }
        
        requests_mock.post("http://test-server:8003/parsers/by_url", json=mock_response)
        
        result = self.client.check_parser("https://example.com/article")
        
        assert result["found"] is True
        assert result["parser"]["site_name"] == "example.com"
    
    def test_get_parsers(self, requests_mock):
        """Test getting list of parsers"""
        mock_response = {
            "parsers": [
                {"id": 1, "site_name": "site1.com"},
                {"id": 2, "site_name": "site2.com"}
            ]
        }
        
        requests_mock.get("http://test-server:8003/parsers", json=mock_response)
        
        result = self.client.get_parsers()
        
        assert len(result) == 2
        assert result[0]["site_name"] == "site1.com"
        assert result[1]["site_name"] == "site2.com"
    
    def test_context_manager(self):
        """Test context manager functionality"""
        with SpiderMCPClient(api_key="test-key") as client:
            assert client.api_key == "test-key"
        # Session should be closed after context exit
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        import time
        
        client = SpiderMCPClient(
            api_key="test-key",
            rate_limit_delay=0.1  # 100ms delay
        )
        
        # Simulate first request
        client.last_request_time = time.time()
        
        # This should cause a delay
        start_time = time.time()
        client._wait_if_needed()
        elapsed = time.time() - start_time
        
        # Should have waited at least the delay time
        assert elapsed >= 0.09  # Allow for small timing variations
