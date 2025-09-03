"""
Proxy Manager for Multi-Browser-Crawler
========================================

Manages a pool of proxy servers and provides random proxy selection
for browser contexts with health monitoring and failover capabilities.
"""

import random
import time
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class ProxyInfo:
    """Information about a proxy server"""
    url: str
    protocol: str = "http"  # http, https, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    is_healthy: bool = True
    last_used: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    last_failure_time: float = 0.0
    
    def __post_init__(self):
        """Parse proxy URL to extract components"""
        if "://" in self.url:
            self.protocol = self.url.split("://")[0]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 100.0
    
    @property
    def playwright_config(self) -> Dict[str, str]:
        """Get Playwright-compatible proxy configuration"""
        config = {"server": self.url}
        
        if self.username and self.password:
            config["username"] = self.username
            config["password"] = self.password
            
        return config
    
    def record_success(self):
        """Record a successful request"""
        self.success_count += 1
        self.last_used = time.time()
        self.is_healthy = True
    
    def record_failure(self):
        """Record a failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        # Mark as unhealthy if failure rate is too high
        if self.success_rate < 50 and self.failure_count >= 3:
            self.is_healthy = False
            logger.warning(f"Proxy {self.url} marked as unhealthy (success rate: {self.success_rate:.1f}%)")


class ProxyManager:
    """
    Manages a pool of proxy servers with health monitoring and rotation.
    
    Features:
    - Random proxy selection
    - Health monitoring and failover
    - Success/failure tracking
    - Automatic proxy recovery
    - Thread-safe operations
    """
    
    def __init__(self, proxy_list: List[str], health_check_interval: float = 300.0):
        """
        Initialize proxy manager.
        
        Args:
            proxy_list: List of proxy URLs (e.g., ["http://proxy1:8080", "socks5://proxy2:1080"])
            health_check_interval: Seconds between health check attempts for failed proxies
        """
        self.proxy_list = []
        self.health_check_interval = health_check_interval
        self._lock = Lock()
        
        # Parse and create ProxyInfo objects
        for proxy_url in proxy_list:
            try:
                proxy_info = self._parse_proxy_url(proxy_url)
                self.proxy_list.append(proxy_info)
                logger.info(f"Added proxy: {proxy_info.url} ({proxy_info.protocol})")
            except Exception as e:
                logger.error(f"Failed to parse proxy URL '{proxy_url}': {e}")
        
        if not self.proxy_list:
            logger.warning("No valid proxies configured - direct connections will be used")
        else:
            logger.info(f"Proxy manager initialized with {len(self.proxy_list)} proxies")
    
    def _parse_proxy_url(self, proxy_url: str) -> ProxyInfo:
        """Parse proxy URL and extract authentication if present"""
        # Handle URLs with authentication: http://user:pass@proxy:port
        if "@" in proxy_url:
            protocol_part, rest = proxy_url.split("://", 1)
            auth_part, server_part = rest.split("@", 1)
            
            if ":" in auth_part:
                username, password = auth_part.split(":", 1)
                return ProxyInfo(
                    url=f"{protocol_part}://{server_part}",
                    protocol=protocol_part,
                    username=username,
                    password=password
                )
        
        return ProxyInfo(url=proxy_url)
    
    def get_random_proxy(self) -> Optional[Dict[str, Any]]:
        """
        Get a random healthy proxy configuration for Playwright.
        
        Returns:
            Playwright-compatible proxy config dict, or None if no proxies available
        """
        with self._lock:
            if not self.proxy_list:
                return None
            
            # Get healthy proxies
            healthy_proxies = [p for p in self.proxy_list if p.is_healthy]
            
            # If no healthy proxies, try to recover some
            if not healthy_proxies:
                self._attempt_proxy_recovery()
                healthy_proxies = [p for p in self.proxy_list if p.is_healthy]
            
            # Still no healthy proxies
            if not healthy_proxies:
                logger.warning("No healthy proxies available - returning None")
                return None
            
            # Select random proxy
            selected_proxy = random.choice(healthy_proxies)
            selected_proxy.last_used = time.time()
            
            logger.debug(f"Selected proxy: {selected_proxy.url} (success rate: {selected_proxy.success_rate:.1f}%)")
            return selected_proxy.playwright_config
    
    def _attempt_proxy_recovery(self):
        """Attempt to recover proxies that have been marked as unhealthy"""
        current_time = time.time()
        
        for proxy in self.proxy_list:
            if not proxy.is_healthy:
                # Check if enough time has passed since last failure
                time_since_failure = current_time - proxy.last_failure_time
                
                if time_since_failure >= self.health_check_interval:
                    # Reset proxy to healthy for retry
                    proxy.is_healthy = True
                    logger.info(f"Attempting to recover proxy: {proxy.url}")
    
    def record_proxy_result(self, proxy_config: Dict[str, Any], success: bool):
        """
        Record the result of using a proxy.
        
        Args:
            proxy_config: The proxy config dict that was used
            success: Whether the request was successful
        """
        if not proxy_config or "server" not in proxy_config:
            return
        
        proxy_url = proxy_config["server"]
        
        with self._lock:
            # Find the proxy by URL
            for proxy in self.proxy_list:
                if proxy.url == proxy_url:
                    if success:
                        proxy.record_success()
                        logger.debug(f"Proxy {proxy_url} success recorded (rate: {proxy.success_rate:.1f}%)")
                    else:
                        proxy.record_failure()
                        logger.debug(f"Proxy {proxy_url} failure recorded (rate: {proxy.success_rate:.1f}%)")
                    break
    
    def get_proxy_stats(self) -> List[Dict[str, Any]]:
        """Get statistics for all proxies"""
        with self._lock:
            stats = []
            for proxy in self.proxy_list:
                stats.append({
                    "url": proxy.url,
                    "protocol": proxy.protocol,
                    "is_healthy": proxy.is_healthy,
                    "success_count": proxy.success_count,
                    "failure_count": proxy.failure_count,
                    "success_rate": proxy.success_rate,
                    "last_used": proxy.last_used,
                    "last_failure_time": proxy.last_failure_time
                })
            return stats
    
    def get_healthy_proxy_count(self) -> int:
        """Get count of healthy proxies"""
        with self._lock:
            return len([p for p in self.proxy_list if p.is_healthy])
    
    def reset_proxy_stats(self):
        """Reset all proxy statistics"""
        with self._lock:
            for proxy in self.proxy_list:
                proxy.success_count = 0
                proxy.failure_count = 0
                proxy.is_healthy = True
                proxy.last_failure_time = 0.0
            logger.info("All proxy statistics reset")
