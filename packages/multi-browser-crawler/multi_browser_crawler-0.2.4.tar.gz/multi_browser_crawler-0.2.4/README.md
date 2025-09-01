# Multi-Browser Crawler

A clean, focused browser automation package for web scraping and content extraction.

## 🎯 **Ultra-Clean Architecture**

This package provides **4 essential components** for browser automation:

- **BrowserPoolManager**: Browser pool management with undetected-chromedriver
- **ProxyManager**: Simple proxy management with Chrome-ready format
- **DebugPortManager**: Thread-safe debug port allocation
- **BrowserConfig**: Clean configuration management

## ✨ **Key Features**

- **Zero Redundancy**: Every line serves a purpose
- **Built-in Features**: Image download, API discovery, JS execution
- **Direct Usage**: No unnecessary wrapper layers
- **Chrome Integration**: Undetected-chromedriver for stealth browsing
- **Proxy Support**: Single regex parsing, Chrome-ready format
- **Session Management**: Persistent and non-persistent browsers
- **rotating-mitmproxy Integration**: Advanced proxy rotation with SSL handling
- **Google Services Pass-through**: Automatic SSL noise reduction

## 📦 **Installation**

```bash
pip install multi-browser-crawler
```

## 🚀 **Quick Start**

```python
import asyncio
from multi_browser_crawler import BrowserPoolManager, BrowserConfig

async def main():
    # Create configuration dict directly
    config = {
        'headless': True,
        'timeout': 30,
        'browser_data_dir': "tmp/browser-data"
    }

    # Initialize browser pool
    browser_pool = BrowserPoolManager(config)

    try:
        # Fetch a webpage
        result = await browser_pool.fetch_html(
            url="https://example.com",
            session_id=None  # Non-persistent browser
        )

        print(f"✅ Success!")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Load time: {result.get('load_time', 0):.2f}s")
        print(f"   HTML size: {len(result.get('html', ''))} characters")

    finally:
        await browser_pool.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔄 **rotating-mitmproxy Integration**

Multi-browser-crawler integrates with rotating-mitmproxy for advanced proxy rotation and SSL certificate handling.

### **Quick Setup**

1. **Start the proxy server**:

```bash
./restart_proxy_server.sh --verbose quiet --web-port 0
```

2. **Configure browser to use proxy**:

```python
config = BrowserConfig(
    proxy_url="http://localhost:3129",  # rotating-mitmproxy default port
    visible=True,
    timeout=60
)
```

### **Key Benefits**

- **Automatic SSL certificate handling**: No manual certificate installation
- **Built-in Google services pass-through**: Hardcoded elimination of SSL noise for Google APIs
- **Zero configuration**: Google services ignored automatically out of the box
- **Proxy rotation**: Automatic switching across multiple proxy servers
- **Health checking**: Automatic proxy validation and failover

### **Certificate Management**

The `~/.mitmproxy/` folder and certificates are **automatically generated** on first run:

- No manual setup required
- Fresh CA certificate created automatically
- Browser arguments applied automatically when using proxy

📖 **[Complete Integration Guide](docs/rotating-mitmproxy-integration.md)**

## ⚙️ **Configuration**

### **Basic Configuration**

```python
from multi_browser_crawler import BrowserPoolManager

config = {
    'headless': True,                    # Run in headless mode
    'timeout': 30,                       # Page load timeout in seconds
    'browser_data_dir': "tmp/browsers",  # Browser data directory
    'proxy_url': "http://localhost:3129", # Optional proxy relay URL
    'min_browsers': 1,                   # Minimum browsers in pool
    'max_browsers': 5,                   # Maximum browsers in pool
    'idle_timeout': 300,                 # Browser idle timeout (seconds)
    'debug_port_start': 9222,            # Debug port range start
    'debug_port_end': 9322,              # Debug port range end
}
```

### **Environment Variables**

```bash
export BROWSER_HEADLESS=true
export BROWSER_TIMEOUT=30
export BROWSER_DATA_DIR="/tmp/browsers"
export PROXY_FILE_PATH="/path/to/proxies.txt"
export MIN_BROWSERS=1
export MAX_BROWSERS=5
export DEBUG_PORT_START=9222
export DEBUG_PORT_END=9322
```

## 📝 **Proxy File Format**

Create a `proxies.txt` file with one proxy per line:

```
# Basic proxies
127.0.0.1:8080
192.168.1.100:3128
proxy.example.com:8080

# Proxies with authentication
user:pass@192.168.1.1:3128
admin:secret@proxy.example.com:9999

# Complex passwords (supported)
user:complex@pass@host.com:8080
```

## 📚 **Usage Examples**

### **1. Basic Web Scraping**

```python
import asyncio
from multi_browser_crawler import BrowserPoolManager, BrowserConfig

async def basic_scraping():
    config = {
        'headless': True,
        'browser_data_dir': "tmp/browser-data"
    }

    browser_pool = BrowserPoolManager(config)

    try:
        result = await browser_pool.fetch_html(
            url="https://httpbin.org/html",
            session_id=None
        )

        print(f"Status: {result['status']}")
        print(f"HTML: {result['html'][:100]}...")

    finally:
        await browser_pool.shutdown()

asyncio.run(basic_scraping())
```

### **2. Using Proxies**

```python
async def proxy_scraping():
    config = {
        'headless': True,
        'browser_data_dir': "tmp/browser-data",
        'proxy_url': "http://localhost:3129"  # Use proxy relay
    }

    browser_pool = BrowserPoolManager(config)

    try:
        result = await browser_pool.fetch_html(
            url="https://httpbin.org/ip",
            session_id=None
        )

        print(f"IP: {result['html']}")

    finally:
        await browser_pool.shutdown()
```

### **3. Persistent Sessions**

```python
async def persistent_session():
    config = BrowserConfig(browser_data_dir="tmp/browser-data")
    browser_pool = BrowserPoolManager(config.to_dict())

    try:
        # First request - set cookie
        result1 = await browser_pool.fetch_html(
            url="https://httpbin.org/cookies/set/test/value123",
            session_id="my_session"  # Persistent session
        )

        # Second request - check cookie (same session)
        result2 = await browser_pool.fetch_html(
            url="https://httpbin.org/cookies",
            session_id="my_session"  # Same session
        )

        print("Cookie persisted between requests!")

    finally:
        await browser_pool.shutdown()
```

### **4. JavaScript Execution**

```python
async def javascript_execution():
    config = BrowserConfig(browser_data_dir="tmp/browser-data")
    browser_pool = BrowserPoolManager(config.to_dict())

    try:
        result = await browser_pool.fetch_html(
            url="https://httpbin.org/html",
            session_id=None,
            js_action="document.title = 'Modified by JS';"
        )

        print(f"Modified title: {result.get('title')}")

    finally:
        await browser_pool.shutdown()
```

### **5. Image Downloading**

```python
async def download_images():
    config = BrowserConfig(
        browser_data_dir="tmp/browser-data",
        download_images_dir="tmp/images"
    )

    browser_pool = BrowserPoolManager(config.to_dict())

    try:
        result = await browser_pool.fetch_html(
            url="https://example.com",
            session_id=None,
            download_images=True  # Enable image downloading
        )

        print(f"Downloaded images: {result.get('downloaded_images', [])}")

    finally:
        await browser_pool.shutdown()
```

### **6. API Discovery**

```python
async def api_discovery():
    config = {'browser_data_dir': "tmp/browser-data"}
    browser_pool = BrowserPoolManager(config)

    try:
        result = await browser_pool.fetch_html(
            url="https://spa-app.example.com",
            session_id=None,
            capture_api_calls=True  # Enable API discovery
        )

        print(f"API calls: {result.get('api_calls', [])}")

    finally:
        await browser_pool.shutdown()
```

## 🖥️ **CLI Usage**

```bash
# Fetch a single URL
python -m multi_browser_crawler.browser_cli fetch https://example.com

# Fetch with proxy
python -m multi_browser_crawler.browser_cli fetch https://example.com --proxy-file proxies.txt

# Test proxies
python -m multi_browser_crawler.browser_cli test-proxies proxies.txt
```

## 🧪 **Testing**

### **Quick Test Run**

```bash
# Run all tests with the test runner
python run_tests.py

# Run only quick tests (skip slow real-world tests)
python run_tests.py --quick

# Run specific test categories
python run_tests.py --unit          # Unit tests only
python run_tests.py --integration   # Integration tests only
python run_tests.py --cleanup       # Cleanup and ad blocking tests
python run_tests.py --realworld     # Real-world site tests
```

### **Manual Testing**

```bash
# Test page cleanup and ad blocking features
python tests/test_cleanup_and_adblock.py

# Test real-world sites (SlickDeals, WenXueCity, Creaders)
python tests/test_realworld_sites.py

# Test enhanced features (API discovery, image download)
python tests/test_enhanced_features_manual.py

# Test API pattern matching
python tests/test_api_pattern_matching.py
```

### **Pytest Testing**

```bash
# Run all pytest tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_browser.py -v
python -m pytest tests/test_enhanced_features.py -v
python -m pytest tests/test_cleanup_adblock_realworld.py -v

# Run tests with markers
python -m pytest tests/ -v -m "not slow"  # Skip slow tests
```

### **Usage Examples**

```bash
# Run usage examples
python examples/01_basic_usage.py
python examples/02_advanced_features.py
python examples/03_session_management.py
python examples/04_enhanced_features.py
```

## 📄 **License**

MIT License - see LICENSE file for details.

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 **Support**

- **GitHub Issues**: Report bugs and request features
- **Documentation**: [Coding Principles](docs/coding_principles.md) and [Examples](examples/)
- **Examples**: Comprehensive usage patterns and principle demonstrations
