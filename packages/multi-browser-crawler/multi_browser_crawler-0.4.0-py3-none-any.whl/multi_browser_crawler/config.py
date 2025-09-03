"""
Browser Configuration Management

This module provides configuration classes for the multi-browser-crawler package,
including support for the new auto-scaling browser pool features.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class BrowserConfig:
    """
    Configuration class for browser pool management.

    This class provides a clean interface for configuring browser pools with
    support for auto-scaling, proxy management, and other advanced features.
    """
    
    # Basic browser settings
    headless: bool = True
    timeout: int = 30
    
    # Auto-scaling configuration (new features)
    min_browsers: int = 2
    max_browsers: int = 6
    contexts_per_browser: int = 4
    
    # Proxy configuration (simplified - single rotation proxy server)
    proxy_url: Optional[str] = None
    
    # Legacy compatibility
    browsers_count: Optional[int] = None  # For backward compatibility
    
    # Advanced settings
    download_images_dir: str = "/tmp/browser_images"
    shared_run_dir: str = "/tmp/browser_pool"
    
    # Debug settings
    debug_start_port: int = 9222
    debug_port_count: int = 100
    
    def __post_init__(self):
        """Post-initialization validation and compatibility handling."""
        # Handle legacy browsers_count parameter
        if self.browsers_count is not None:
            self.min_browsers = self.browsers_count
            self.max_browsers = self.browsers_count
            
        # Proxy configuration is simplified - single proxy URL only
            
        # Validation
        if self.min_browsers < 1:
            raise ValueError("min_browsers must be at least 1")
        if self.max_browsers < self.min_browsers:
            raise ValueError("max_browsers must be >= min_browsers")

        # Validate proxy URL format if provided
        if self.proxy_url:
            from urllib.parse import urlparse
            parsed = urlparse(self.proxy_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid proxy URL format: {self.proxy_url}. Expected format: http://host:port")
        if self.contexts_per_browser < 1:
            raise ValueError("contexts_per_browser must be at least 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format for internal use."""
        config_dict = {
            'headless': self.headless,
            'timeout': self.timeout,
            'min_browsers': self.min_browsers,
            'max_browsers': self.max_browsers,
            'contexts_per_browser': self.contexts_per_browser,
            'proxy_url': self.proxy_url,

            'download_images_dir': self.download_images_dir,
            'shared_run_dir': self.shared_run_dir,
            'debug_start_port': self.debug_start_port,
            'debug_port_count': self.debug_port_count,
        }
        
        # Add legacy compatibility
        if self.browsers_count is not None:
            config_dict['browsers_count'] = self.browsers_count
            
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BrowserConfig':
        """Create BrowserConfig from dictionary."""
        # Filter out unknown keys
        known_keys = {
            'headless', 'timeout', 'min_browsers', 'max_browsers',
            'contexts_per_browser', 'proxy_url', 'browsers_count',
            'download_images_dir', 'shared_run_dir', 'debug_start_port', 'debug_port_count'
        }

        filtered_dict = {k: v for k, v in config_dict.items() if k in known_keys}
        return cls(**filtered_dict)
    
    def with_scaling(self, min_browsers: int, max_browsers: int) -> 'BrowserConfig':
        """Create a new config with updated scaling parameters."""
        new_config = BrowserConfig(**self.to_dict())
        new_config.min_browsers = min_browsers
        new_config.max_browsers = max_browsers
        return new_config
    
    def with_proxy(self, proxy_url: str) -> 'BrowserConfig':
        """Create a new config with updated proxy settings."""
        new_config = BrowserConfig(**self.to_dict())
        new_config.proxy_url = proxy_url
        return new_config


# Convenience functions for common configurations
def create_basic_config(headless: bool = True) -> BrowserConfig:
    """Create a basic browser configuration."""
    return BrowserConfig(
        headless=headless
    )


def create_scaling_config(min_browsers: int = 2, max_browsers: int = 6) -> BrowserConfig:
    """Create a configuration with custom scaling parameters."""
    return BrowserConfig(
        min_browsers=min_browsers,
        max_browsers=max_browsers
    )


def create_proxy_config(proxy_url: str) -> BrowserConfig:
    """Create a configuration with proxy support."""
    return BrowserConfig(
        proxy_url=proxy_url
    )


def create_legacy_config(browsers_count: int = 4) -> BrowserConfig:
    """Create a legacy-compatible configuration with fixed browser count."""
    return BrowserConfig(
        browsers_count=browsers_count
    )
