#!/usr/bin/env python3
"""
Basic usage examples for spider-mcp-client
"""

from spider_mcp_client import SpiderMCPClient, ParserNotFoundError, AuthenticationError


def basic_example():
    """Basic usage example"""
    print("🕷️  Spider MCP Client - Basic Example")
    print("=" * 50)
    
    # Initialize client
    client = SpiderMCPClient(
        api_key="your-api-key-here",  # Replace with your actual API key
        base_url="http://localhost:8003"  # Your Spider MCP server
    )
    
    # Parse a URL
    try:
        result = client.parse_url("https://example.com/article")
        
        print(f"✅ Successfully parsed URL!")
        print(f"📰 Title: {result.get('title', 'N/A')}")
        print(f"✍️  Author: {result.get('author', 'N/A')}")
        print(f"📅 Date: {result.get('publish_date', 'N/A')}")
        print(f"📝 Content: {len(result.get('content', ''))} characters")
        print(f"🖼️  Images: {len(result.get('images', []))} images")
        
    except ParserNotFoundError:
        print("❌ No parser found for this URL")
        print("💡 You need to create a parser for this website first")
        
    except AuthenticationError:
        print("❌ Authentication failed - check your API key")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def image_download_example():
    """Example with image download"""
    print("\n🖼️  Image Download Example")
    print("=" * 50)
    
    client = SpiderMCPClient(api_key="your-api-key-here")
    
    try:
        result = client.parse_url(
            "https://news-site.com/photo-story",
            download_images=True  # Download and localize images
        )
        
        print(f"✅ Parsed with images!")
        print(f"📰 Title: {result.get('title', 'N/A')}")
        print(f"🖼️  Downloaded {len(result.get('images', []))} images:")
        
        for i, img_url in enumerate(result.get('images', []), 1):
            print(f"   {i}. {img_url}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def batch_processing_example():
    """Example of batch processing multiple URLs"""
    print("\n📦 Batch Processing Example")
    print("=" * 50)
    
    urls = [
        "https://site1.com/article1",
        "https://site2.com/article2",
        "https://site3.com/article3"
    ]
    
    client = SpiderMCPClient(
        api_key="your-api-key-here",
        rate_limit_delay=2.0  # 2 second delay between requests
    )
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"📄 Processing {i}/{len(urls)}: {url}")
        
        try:
            result = client.parse_url(url)
            results.append({
                'url': url,
                'title': result.get('title'),
                'success': True
            })
            print(f"   ✅ Success: {result.get('title', 'No title')}")
            
        except ParserNotFoundError:
            print(f"   ❌ No parser for {url}")
            results.append({'url': url, 'success': False, 'error': 'No parser'})
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({'url': url, 'success': False, 'error': str(e)})
    
    # Summary
    successful = [r for r in results if r['success']]
    print(f"\n📊 Results: {len(successful)}/{len(urls)} URLs parsed successfully")


def parser_check_example():
    """Example of checking parser availability"""
    print("\n🔍 Parser Check Example")
    print("=" * 50)
    
    client = SpiderMCPClient(api_key="your-api-key-here")
    
    test_urls = [
        "https://techcrunch.com/article",
        "https://unknown-site.com/article"
    ]
    
    for url in test_urls:
        try:
            parser_info = client.check_parser(url)
            
            if parser_info.get('found'):
                parser = parser_info['parser']
                print(f"✅ Parser found for {url}")
                print(f"   📝 Site: {parser.get('site_name')}")
                print(f"   🏷️  Name: {parser.get('url_name')}")
                
                # Now parse the URL
                result = client.parse_url(url)
                print(f"   📰 Title: {result.get('title', 'N/A')}")
            else:
                print(f"❌ No parser found for {url}")
                
        except Exception as e:
            print(f"❌ Error checking {url}: {e}")


def context_manager_example():
    """Example using context manager"""
    print("\n🔧 Context Manager Example")
    print("=" * 50)
    
    # Automatic cleanup with context manager
    with SpiderMCPClient(api_key="your-api-key-here") as client:
        try:
            result = client.parse_url("https://example.com/article")
            print(f"✅ Title: {result.get('title', 'N/A')}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("🔒 Session automatically closed")


def main():
    """Run all examples"""
    print("🕷️  Spider MCP Client Examples")
    print("=" * 60)
    print("💡 Make sure to replace 'your-api-key-here' with your actual API key!")
    print("🌐 Make sure your Spider MCP server is running on localhost:8003")
    print()
    
    # Run examples
    basic_example()
    image_download_example()
    batch_processing_example()
    parser_check_example()
    context_manager_example()
    
    print("\n🎉 Examples complete!")
    print("📚 Check the README.md for more detailed documentation")


if __name__ == "__main__":
    main()
