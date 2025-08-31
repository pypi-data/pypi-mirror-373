# Spider MCP Client Package Information

## 📦 Package Structure

```
spider-mcp-client/
├── 📄 README.md                    # Main documentation
├── 📄 LICENSE                      # MIT License
├── 📄 CHANGELOG.md                 # Version history
├── 📄 MANIFEST.in                  # Package manifest
├── 📄 setup.py                     # Setup script (legacy)
├── 📄 pyproject.toml               # Modern Python packaging
├── 📄 PACKAGE_INFO.md              # This file
│
├── 📁 spider_mcp_client/           # Main package
│   ├── 📄 __init__.py              # Package initialization
│   ├── 📄 client.py                # Main SpiderMCPClient class
│   └── 📄 exceptions.py            # Exception classes
│
├── 📁 tests/                       # Test suite
│   ├── 📄 __init__.py              # Test package init
│   └── 📄 test_client.py           # Client tests
│
├── 📁 examples/                    # Usage examples
│   └── 📄 basic_usage.py           # Basic usage examples
│
└── 📁 scripts/                     # Build/test scripts
    ├── 📄 build.sh                 # Build script
    └── 📄 test.sh                  # Test script
```

## 🚀 Publishing to PyPI

### Prerequisites

1. **Create PyPI account**: https://pypi.org/account/register/
2. **Create API token**: https://pypi.org/manage/account/token/
3. **Install build tools**:
   ```bash
   pip install build twine
   ```

### Build and Publish

```bash
# Navigate to package directory
cd spider_mcp/spider-mcp-client/

# Run tests
./scripts/test.sh

# Build package
./scripts/build.sh

# Upload to Test PyPI (recommended first)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI (production)
python -m twine upload dist/*
```

### Test Installation

```bash
# From Test PyPI
pip install --index-url https://test.pypi.org/simple/ spider-mcp-client

# From PyPI (after publishing)
pip install spider-mcp-client
```

## 📋 Package Features

### ✅ Core Features
- **SpiderMCPClient** - Main client class
- **parse_url()** - Primary parsing method
- **check_parser()** - Parser availability check
- **get_parsers()** - List available parsers
- **Built-in retry logic** - Exponential backoff
- **Rate limiting** - Configurable delays
- **Error handling** - Specific exception types
- **Context manager** - Automatic cleanup
- **Type hints** - Full typing support

### ✅ Exception Hierarchy
```python
SpiderMCPError                    # Base exception
├── AuthenticationError           # Invalid API key
├── ParserNotFoundError          # No parser for URL
├── RateLimitError               # Rate limit exceeded
├── ServerError                  # Server error (5xx)
├── TimeoutError                 # Request timeout
└── ConnectionError              # Connection failed
```

### ✅ Configuration Options
```python
SpiderMCPClient(
    api_key="required",           # API key
    base_url="http://localhost:8003",  # Server URL
    timeout=30,                   # Request timeout
    max_retries=3,               # Retry attempts
    rate_limit_delay=1.0         # Delay between requests
)
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
./scripts/test.sh

# Or manually
python -m pytest tests/ -v
python -m mypy spider_mcp_client/
python -m black --check spider_mcp_client/
python -m flake8 spider_mcp_client/
```

### Test Coverage
- ✅ Client initialization
- ✅ Successful URL parsing
- ✅ Image download functionality
- ✅ Error handling (all exception types)
- ✅ Parser availability checking
- ✅ Rate limiting
- ✅ Context manager support

## 📚 Documentation

### README.md Sections
- ✅ Quick start guide
- ✅ Installation instructions
- ✅ API reference
- ✅ Usage examples
- ✅ Error handling
- ✅ Advanced configuration
- ✅ Contributing guidelines

### Examples Included
- ✅ Basic URL parsing
- ✅ Image download
- ✅ Batch processing
- ✅ Error handling
- ✅ Parser checking
- ✅ Context manager usage

## 🔧 Development

### Code Quality
- ✅ **Black** - Code formatting
- ✅ **Flake8** - Linting
- ✅ **MyPy** - Type checking
- ✅ **Pytest** - Testing framework

### Python Support
- ✅ Python 3.8+
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Type hints for IDE support

### Dependencies
- **requests** - HTTP client
- **typing-extensions** - Type hints (Python <3.10)

## 🎯 Usage After Publishing

### Installation
```bash
pip install spider-mcp-client
```

### Basic Usage
```python
from spider_mcp_client import SpiderMCPClient

client = SpiderMCPClient(api_key="your-api-key")
result = client.parse_url("https://example.com/article")
print(f"Title: {result['title']}")
```

### Error Handling
```python
from spider_mcp_client import SpiderMCPClient, ParserNotFoundError

try:
    result = client.parse_url("https://example.com/article")
except ParserNotFoundError:
    print("No parser available for this website")
```

## 🌟 Benefits for Users

### ✅ Developer Experience
- **One-line installation** - `pip install spider-mcp-client`
- **Simple API** - Single method for most use cases
- **Clear documentation** - Comprehensive examples
- **Type safety** - Full type hints
- **Error clarity** - Specific exception types

### ✅ Production Ready
- **Retry logic** - Handles temporary failures
- **Rate limiting** - Respects server resources
- **Session management** - Automatic cleanup
- **Timeout handling** - Prevents hanging requests
- **Connection pooling** - Efficient HTTP requests

### ✅ Flexibility
- **Configurable** - All aspects customizable
- **Session isolation** - Multiple app contexts
- **Image support** - Optional image download
- **Batch processing** - Handle multiple URLs
- **Context manager** - Automatic resource cleanup

**This package makes Spider MCP accessible to any Python developer with a simple `pip install`!** 🚀
