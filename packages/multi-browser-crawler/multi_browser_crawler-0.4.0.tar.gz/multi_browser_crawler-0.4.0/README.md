# Multi-Browser Crawler

A focused browser automation package for web scraping and content extraction.

## Features

- **Browser Pool Management**: Auto-scaling browser pools with session management
- **Proxy Support**: Built-in proxy rotation and management  
- **Image Download**: Automatic image capture and localization
- **API Discovery**: Network request capture and pattern matching
- **Session Persistence**: Stateful browsing with cookie/session support

## Installation

```bash
pip install multi-browser-crawler
```

## Quick Start

```python
import asyncio
from multi_browser_crawler import BrowserPoolManager, BrowserConfig

async def main():
    # Simple configuration
    config = BrowserConfig(headless=True, timeout=30)
    pool = BrowserPoolManager(config.to_dict())

    try:
        await pool.initialize()
        
        # Fetch HTML
        result = await pool.fetch_html(
            url="https://example.com",
            session_id="my_session"
        )

        if result['status']['success']:
            print(f"✅ Success! Title: {result.get('title', 'N/A')}")
            print(f"HTML size: {len(result.get('html', ''))} characters")
        else:
            print(f"❌ Error: {result['status'].get('error')}")

    finally:
        await pool.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Options

```python
config = BrowserConfig(
    headless=True,              # Run in headless mode
    timeout=30,                 # Page load timeout (seconds)
    min_browsers=1,             # Minimum browsers in pool
    max_browsers=5,             # Maximum browsers in pool
    proxy_url="http://proxy:8080",  # Optional proxy URL
    download_images_dir="/tmp/images"  # Image download directory
)
```

## API Methods

### fetch_html()

```python
result = await pool.fetch_html(
    url="https://example.com",
    session_id="optional_session",      # For persistent sessions
    timeout=30,                         # Request timeout
    api_patterns=["*/api/*"],          # Capture API calls
    images_to_capture=["*.jpg", "*.png"] # Download images
)
```

**Response format:**
```python
{
    'status': {'success': True, 'url': '...', 'load_time': 1.23},
    'html': '<html>...</html>',
    'title': 'Page Title',
    'api_calls': [...],  # Captured API requests
    'images': [...]      # Downloaded images
}
```

## Session Management

```python
# Persistent session - maintains cookies/state
result1 = await pool.fetch_html(url="https://site.com/login", session_id="user1")
result2 = await pool.fetch_html(url="https://site.com/profile", session_id="user1")

# Non-persistent - fresh browser each time  
result3 = await pool.fetch_html(url="https://site.com", session_id=None)
```

## Proxy Support

```python
# Single proxy
config = BrowserConfig(proxy_url="http://proxy:8080")

# The package integrates with rotating-mitmproxy for advanced proxy rotation
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/ -m "not slow" -v
```

## License

MIT License - see LICENSE file for details.
