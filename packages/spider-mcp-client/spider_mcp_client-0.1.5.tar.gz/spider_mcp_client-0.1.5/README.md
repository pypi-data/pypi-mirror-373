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

print(f"Status: {result['status']}")
print(f"Title: {result['html_data'].get('title', 'N/A')}")
print(f"Parser: {result['status_detail']['parser_used']}")
print(f"API Calls: {len(result['api_calls'])}")
print(f"Images: {len(result['downloaded_images'])}")
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
    session_name="my-session",          # Optional: Session name
    retry=1                             # Optional: Retry attempts (default: 1)
)
```

**Returns:**

```python
{
    "status": "success",
    "url": "https://example.com/article",
    "html_data": {
        "type": "article",
        "title": "Article Title",
        "content": "Full article content...",
        "author": "Author Name",
        "publish_date": "2025-01-17"
    },
    "api_calls": [...],  # Captured API calls
    "downloaded_images": [...],  # Downloaded images
    "status_detail": {
        "parser_used": "example.com - article_parser",
        "parser_id": 123,
        "success": true
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

if result['status'] == 'success':
    html_data = result['html_data']
    print(f"📰 {html_data.get('title', 'N/A')}")
    print(f"✍️  {html_data.get('author', 'Unknown')}")
    print(f"📅 {html_data.get('publish_date', 'Unknown')}")
    print(f"🔧 Parser: {result['status_detail']['parser_used']}")
```

### With Image Download

```python
# Parse with image download
result = client.parse_url(
    url="https://news-site.com/photo-story",
    download_images=True
)

if result['status'] == 'success':
    images = result['downloaded_images']
    print(f"Downloaded {len(images)} images:")
    for img_url in images:
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
    if result['status'] == 'success':
        print(f"Success: {result['html_data'].get('title', 'N/A')}")
    else:
        print(f"Parse failed: {result['status_detail'].get('error', 'Unknown error')}")

except ParserNotFoundError:
    print("❌ No parser available for this website")

except AuthenticationError:
    print("❌ Invalid API key")

except Exception as e:
    print(f"❌ Error: {e}")
```

### With Retry Logic

```python
# Parse with automatic retries
result = client.parse_url(
    url="https://sometimes-slow-site.com/article",
    retry=3  # Will attempt up to 4 times (initial + 3 retries)
)

if result['status'] == 'success':
    print(f"✅ Success: {result['html_data'].get('title')}")
    print(f"🔧 Parser: {result['status_detail']['parser_used']}")
else:
    print(f"❌ Failed: {result['status_detail'].get('error')}")
```

### API Calls and Images

```python
# Parse a page that makes API calls and has images
result = client.parse_url(
    url="https://dynamic-site.com/article",
    download_images=True
)

if result['status'] == 'success':
    print(f"📰 Title: {result['html_data'].get('title')}")
    print(f"🌐 API calls captured: {len(result['api_calls'])}")
    print(f"🖼️  Images downloaded: {len(result['downloaded_images'])}")

    # Show captured API calls
    for api_call in result['api_calls']:
        print(f"  📡 {api_call['method']} {api_call['url']}")
```

### Check Parser Availability

```python
# Check if parser exists before parsing
parser_info = client.check_parser("https://target-site.com/article")

if parser_info.get('found'):
    print(f"✅ Parser available: {parser_info['parser']['site_name']}")
    result = client.parse_url("https://target-site.com/article")
    if result['status'] == 'success':
        print(f"📰 {result['html_data'].get('title')}")
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

### Session Isolation

```python
# Use session names for browser isolation
client = SpiderMCPClient(api_key="your-api-key")

# Each session gets its own browser context
result1 = client.parse_url(
    "https://site.com/page1",
    session_name="session-1"
)

result2 = client.parse_url(
    "https://site.com/page2",
    session_name="session-2"
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
