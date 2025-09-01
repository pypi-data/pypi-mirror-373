"""
Multi-Browser Crawler Package - Unified Selenium & Playwright
=============================================================

A modern browser automation package supporting both Selenium and Playwright.

Main Components:
- BrowserPoolManager: Modern browser pool with Playwright + Patchright stealth
- PlaywrightBrowser: Modern Playwright browser with Patchright stealth
- DebugPortManager: Debug port allocation for browser instances
- BrowserConfig: Configuration management

Key Features:
- Playwright + Patchright for undetectable automation
- Single proxy relay support (no complex proxy management)
- Thread-safe async operations
- Context-based session management
- Built-in stealth capabilities
- Comprehensive monitoring and statistics
"""

from multi_browser_crawler.browser_pool import SimpleBrowserPool
from multi_browser_crawler.debug_port_manager import DebugPortManager
from multi_browser_crawler.config import BrowserConfig
from multi_browser_crawler import utils

# Create the BrowserPoolManager alias for backward compatibility
BrowserPoolManager = SimpleBrowserPool

__version__ = "0.3.0-playwright-patchright"
__author__ = "Spider MCP Team"
__email__ = "team@spider-mcp.com"


# Clean exports - now using Playwright by default
__all__ = [
    "BrowserPoolManager",     # Backward compatibility alias for SimpleBrowserPool
    "SimpleBrowserPool",      # New auto-scaling pool implementation
    "BrowserConfig",          # Configuration management
    "DebugPortManager",       # Debug port allocation
    "utils",                  # Utility functions
]
