# Spider MCP Client

[![PyPI version](https://badge.fury.io/py/spider-mcp-client.svg)](https://badge.fury.io/py/spider-mcp-client)
[![Python Support](https://img.shields.io/pypi/pyversions/spider-mcp-client.svg)](https://pypi.org/project/spider-mcp-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python client for **Spider MCP** - a professional web scraping API with advanced anti-detection capabilities.

## 🚀 Quick Start

### Installation

```bash
pip install spider-mcp-client
```

### Basic Usage

```python
from spider_mcp_client import SpiderMCPClient

# Initialize client
client = SpiderMCPClient(
    api_key="your-api-key-here",
    base_url="http://localhost:8003"  # Your Spider MCP server
)

# Parse a URL
result = client.parse_url("https://example.com/article")

print(f"Title: {result['title']}")
print(f"Content: {result['content'][:200]}...")
print(f"Images: {len(result.get('images', []))}")
```

## 📋 Features

- ✅ **Simple API** - One method to parse any supported URL
- ✅ **Built-in retry logic** - Automatic retries with exponential backoff
- ✅ **Rate limiting** - Respectful delays between requests
- ✅ **Error handling** - Clear exceptions for different error types
- ✅ **Image support** - Optional image download and localization
- ✅ **Session isolation** - Multiple isolated browser sessions
- ✅ **Type hints** - Full typing support for better IDE experience

## 🔧 API Reference

### SpiderMCPClient

```python
client = SpiderMCPClient(
    api_key="your-api-key",           # Required: Your API key
    base_url="http://localhost:8003", # Spider MCP server URL
    timeout=30,                       # Request timeout (seconds)
    max_retries=3,                    # Max retry attempts
    rate_limit_delay=1.0             # Delay between requests (seconds)
)
```

### parse_url()

```python
result = client.parse_url(
    url="https://example.com/article",  # Required: URL to parse
    download_images=False,              # Optional: Download images
    app_name="my-app"                   # Optional: Session isolation
)
```

**Returns:**
```python
{
    "title": "Article Title",
    "content": "Full article content...",
    "author": "Author Name",
    "publish_date": "2025-01-17",
    "images": ["http://localhost:8003/downloaded_images/image1.jpg"],
    "url": "https://example.com/article",
    "parser_info": {
        "site_name": "example.com",
        "url_name": "article_parser"
    }
}
```

## 📖 Examples

### Basic Article Parsing

```python
from spider_mcp_client import SpiderMCPClient

client = SpiderMCPClient(api_key="sk-1234567890abcdef")

# Parse a news article
result = client.parse_url("https://techcrunch.com/2025/01/17/ai-news")

if result:
    print(f"📰 {result['title']}")
    print(f"✍️  {result.get('author', 'Unknown')}")
    print(f"📅 {result.get('publish_date', 'Unknown')}")
    print(f"📝 Content: {len(result.get('content', ''))} characters")
```

### With Image Download

```python
# Parse with image download
result = client.parse_url(
    url="https://news-site.com/photo-story",
    download_images=True
)

print(f"Downloaded {len(result.get('images', []))} images:")
for img_url in result.get('images', []):
    print(f"  🖼️  {img_url}")
```

### Error Handling

```python
from spider_mcp_client import (
    SpiderMCPClient, 
    ParserNotFoundError, 
    AuthenticationError
)

client = SpiderMCPClient(api_key="your-api-key")

try:
    result = client.parse_url("https://unsupported-site.com/article")
    print(f"Success: {result['title']}")
    
except ParserNotFoundError:
    print("❌ No parser available for this website")
    
except AuthenticationError:
    print("❌ Invalid API key")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

### Batch Processing

```python
import time
from spider_mcp_client import SpiderMCPClient

def batch_parse(urls, api_key, delay=2):
    """Parse multiple URLs with delays"""
    client = SpiderMCPClient(api_key=api_key, rate_limit_delay=delay)
    results = []
    
    for url in urls:
        try:
            print(f"Parsing: {url}")
            result = client.parse_url(url)
            results.append({
                'url': url,
                'title': result.get('title'),
                'success': True
            })
        except Exception as e:
            print(f"Failed {url}: {e}")
            results.append({
                'url': url,
                'error': str(e),
                'success': False
            })
    
    return results

# Usage
urls = [
    "https://site1.com/article1",
    "https://site2.com/article2", 
    "https://site3.com/article3"
]

results = batch_parse(urls, "your-api-key")
successful = [r for r in results if r['success']]
print(f"✅ Successfully parsed: {len(successful)}/{len(urls)} URLs")
```

### Context Manager

```python
# Automatic cleanup with context manager
with SpiderMCPClient(api_key="your-api-key") as client:
    result = client.parse_url("https://example.com/article")
    print(f"Title: {result['title']}")
# Session automatically closed
```

### Check Parser Availability

```python
# Check if parser exists before parsing
parser_info = client.check_parser("https://target-site.com/article")

if parser_info.get('found'):
    print(f"✅ Parser available: {parser_info['parser']['site_name']}")
    result = client.parse_url("https://target-site.com/article")
else:
    print("❌ No parser found for this URL")
```

## 🚨 Exception Types

```python
from spider_mcp_client import (
    SpiderMCPError,        # Base exception
    AuthenticationError,   # Invalid API key
    ParserNotFoundError,   # No parser for URL
    RateLimitError,        # Rate limit exceeded
    ServerError,           # Server error (5xx)
    TimeoutError,          # Request timeout
    ConnectionError        # Connection failed
)
```

## 🔑 Getting Your API Key

1. **Start Spider MCP server:**
   ```bash
   # On your Spider MCP server
   ./restart.sh
   ```

2. **Visit admin interface:**
   ```
   http://localhost:8003/admin/users
   ```

3. **Create/view user and copy API key**

## 🌐 Server Requirements

This client requires a running **Spider MCP server**. The server provides:

- ✅ **Custom parsers** for each website
- ✅ **Undetected ChromeDriver** for Cloudflare bypass  
- ✅ **Professional anti-detection** capabilities
- ✅ **Image processing** and localization
- ✅ **Session management** and isolation

## 📚 Advanced Usage

### Custom Session Names

```python
# Use different sessions for different applications
client = SpiderMCPClient(api_key="your-api-key")

# Session for news parsing
news_result = client.parse_url(
    "https://news-site.com/article",
    app_name="news-parser"
)

# Session for e-commerce parsing  
product_result = client.parse_url(
    "https://shop-site.com/product",
    app_name="product-parser"
)
```

### Configuration

```python
# Production configuration
client = SpiderMCPClient(
    api_key="your-api-key",
    base_url="https://your-spider-mcp-server.com",
    timeout=60,           # Longer timeout for complex pages
    max_retries=5,        # More retries for reliability
    rate_limit_delay=2.0  # Slower rate for respectful scraping
)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI Package:** https://pypi.org/project/spider-mcp-client/
- **GitHub Repository:** https://github.com/spider-mcp/spider-mcp-client
- **Documentation:** https://spider-mcp.readthedocs.io/
- **Spider MCP Server:** https://github.com/spider-mcp/spider-mcp

---

**Made with ❤️ by the Spider MCP Team**
