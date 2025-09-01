# Changelog

All notable changes to the multi-browser-crawler project will be documented in this file.

## [2.0.0] - 2024-08-19

### 🎯 **MAJOR REWRITE - Ultra-Clean Architecture**

This is a complete rewrite focused on browser fetching operations only.

### ✅ **Added**

- **BrowserPoolManager**: Clean browser pool management with undetected-chromedriver
- **ProxyManager**: Simple proxy management with single regex parsing
- **DebugPortManager**: Thread-safe debug port allocation
- **BrowserConfig**: Clean configuration management
- **browser_cli**: Focused command-line interface for browser operations
- Built-in image downloading in `fetch_html()`
- Built-in API discovery in `fetch_html()`
- Built-in JavaScript execution in `fetch_html()`
- Comprehensive test suite with pytest support
- Single usage example demonstrating all features

### 🗑️ **Removed**

- **utils/ folder**: Eliminated 834 lines of redundant code
- **clients/ folder**: Removed outdated integrations
- **config/ folder**: Consolidated into single config.py
- **exceptions/ folder**: Removed unnecessary complexity
- **api.py**: Removed outdated API wrapper
- **browser_manager.py**: Removed unnecessary abstraction layer
- All redundant examples and documentation

### 🔧 **Changed**

- **CLI renamed**: `multi-browser-crawler` → `browser-cli`
- **Package exports**: Only 4 essential components
- **Configuration**: Single BrowserConfig class
- **Error handling**: Standard Python exceptions
- **Examples**: Single comprehensive usage.py file
- **Tests**: Focused test files for each component

### 📦 **Package Structure**

```
multi-browser-crawler/
├── multi_browser_crawler/
│   ├── browser.py               # BrowserPoolManager
│   ├── proxy_manager.py         # ProxyManager
│   ├── debug_port_manager.py    # DebugPortManager
│   ├── config.py                # BrowserConfig
│   └── browser_cli.py           # CLI
├── examples/usage.py            # Single example
└── tests/                       # Focused tests
```

### 🎯 **Benefits**

- **Eliminated 2,000+ lines** of redundant code
- **Zero redundancy** - every line serves a purpose
- **Direct usage** - no unnecessary wrapper layers
- **Built-in features** - image download, API discovery, JS execution
- **Perfect for integration** - clean 4-component architecture

### 💥 **Breaking Changes**

- Complete API rewrite
- All previous imports are invalid
- Configuration format changed
- CLI commands changed
- Examples and documentation rewritten

### 🚀 **Migration Guide**

```python
# Old (v1.x):
from multi_browser_crawler import BrowserCrawler
crawler = BrowserCrawler(config)

# New (v2.0):
from multi_browser_crawler import BrowserPoolManager, BrowserConfig
config = BrowserConfig(browser_data_dir="/tmp/browsers")
browser_pool = BrowserPoolManager(config.to_dict())
```

---

## [1.x.x] - Previous Versions

Previous versions contained complex folder structures and redundant code.
All functionality has been consolidated and improved in v2.0.0.

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes
