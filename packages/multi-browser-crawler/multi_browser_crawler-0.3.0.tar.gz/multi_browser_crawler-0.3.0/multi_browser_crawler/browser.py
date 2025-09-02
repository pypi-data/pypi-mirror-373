"""
Browser.py with Playwright + Patchright
=======================================

Modern browser implementation using Playwright with Patchright stealth patches.
Maintains the same API as the original Selenium version but with superior performance.

KEY IMPROVEMENTS:
1. Undetectable automation using Patchright stealth patches
2. Dynamic proxy switching without browser restarts
3. Context-based session management for better performance
4. Thread-safe async operations with minimal locking
5. Advanced proxy rotation strategies (use_proxy: -1, 0, 1, N...)

PERFORMANCE IMPACT: Significantly faster than Selenium (no restart overhead)
"""

import os
import time
import logging
import asyncio
import uuid
from urllib.parse import urljoin
from typing import Dict, Optional, List, Any
from pathlib import Path

try:
    # Use Patchright for stealth capabilities
    from patchright.async_api import async_playwright, Browser as PlaywrightBrowser, BrowserContext, Page
except ImportError:
    raise ImportError("patchright is required. Install with: pip install patchright")

from multi_browser_crawler.debug_port_manager import DebugPortManager
from multi_browser_crawler.utils import safe_remove_directory

logger = logging.getLogger(__name__)


class Browser:
    """
    Thread-safe Playwright browser instance with Patchright stealth.

    MODERN FEATURES:
    - Undetectable automation using Patchright patches
    - Dynamic proxy switching without restarts
    - Context-based session management
    - Thread-safe async operations
    """

    def __init__(self, session_id: str, config: Dict[str, Any], debug_port_manager: DebugPortManager,
                 shared_run_dir: str):
        """
        Initialize a Playwright browser instance with stealth capabilities.

        Args:
            session_id: Unique session identifier (can be user-provided or temp UUID)
            config: Configuration dictionary
            debug_port_manager: Shared debug port manager instance (kept for compatibility)
            shared_run_dir: Shared timestamped run directory from BrowserPoolManager
        """
        # Immutable properties (no locking needed)
        self.session_id = session_id
        self.config = config
        self.debug_port_manager = debug_port_manager
        self.shared_run_dir = shared_run_dir

        # 🔒 THREAD SAFETY: One lock protects all mutable state
        self._state_lock = asyncio.Lock()

        # Browser instance properties (protected by _state_lock)
        self.browser_id = f"pw_{session_id}_{uuid.uuid4().hex[:8]}"
        self._playwright = None
        self._browser: Optional[PlaywrightBrowser] = None
        self._contexts: Dict[str, BrowserContext] = {}  # proxy_key -> context
        self._current_context: Optional[BrowserContext] = None
        self._current_page: Optional[Page] = None
        self._debug_port: Optional[int] = None  # Kept for compatibility

        # Usage tracking (protected by _state_lock)
        self._created_at: float = time.time()
        self._last_used: float = time.time()
        self._request_count: int = 0
        self._in_use: bool = False  # Track if browser is currently being used
        self._is_valid_flag: bool = True  # Flag for efficient validity checking

        # Configuration (immutable after init)
        self.download_images_dir = config.get('download_images_dir', '/tmp/browser_images')
        self.headless = config.get('headless', True)
        self.timeout = config.get('timeout', 30)  # In seconds

        # Store proxy URL from config (single proxy relay)
        self.proxy_url = config.get('proxy_url')
        if self.proxy_url:
            logger.info(f"Browser {self.browser_id} configured to use proxy relay: {self.proxy_url}")

        logger.info(f"Playwright browser {self.browser_id} initialized with session_id: {session_id}")

    # =========================================================================
    # THREAD-SAFE PUBLIC API
    # =========================================================================

    async def start(self) -> None:
        """
        Start the Playwright browser instance with stealth patches.
        THREAD-SAFE: Multiple calls are safe, only starts once.
        """
        async with self._state_lock:
            if self._browser is not None:
                logger.warning(f"Browser {self.browser_id} is already started")
                return

            # All startup operations protected by lock
            await self._start_browser_internal()

    async def is_valid(self) -> bool:
        """
        Check if browser is still valid and responsive.
        THREAD-SAFE: Validation flag updates are atomic.

        Returns:
            True if browser is valid, False otherwise
        """
        async with self._state_lock:
            return await self._check_validity_internal()

    async def mark_in_use(self, in_use: bool) -> None:
        """
        Mark browser as in use or available.
        THREAD-SAFE: Atomic state change with usage tracking.
        
        Args:
            in_use: True to mark as in use, False to mark as available
        """
        async with self._state_lock:
            self._in_use = in_use
            if in_use:
                self._request_count += 1
                self._last_used = time.time()

    async def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get browser usage statistics.
        THREAD-SAFE: Returns consistent snapshot of stats.
        
        Returns:
            Dictionary with usage statistics
        """
        async with self._state_lock:
            return {
                'browser_id': self.browser_id,
                'session_id': self.session_id,
                'request_count': self._request_count,
                'created_at': self._created_at,
                'last_used': self._last_used,
                'age': time.time() - self._created_at,
                'idle_time': time.time() - self._last_used,
                'in_use': self._in_use,
                'is_valid': self._is_valid_flag,
                'has_browser': self._browser is not None,
                'debug_port': self._debug_port
            }

    async def cleanup(self) -> None:
        """
        Clean up browser instance and its resources.
        THREAD-SAFE: All cleanup operations are atomic.
        """
        async with self._state_lock:
            await self._cleanup_internal()

    # =========================================================================
    # THREAD-SAFE PROPERTY ACCESS
    # =========================================================================

    @property
    def is_persistent(self) -> bool:
        """Check if this is a persistent session (immutable property)"""
        return self.session_id is not None and not self.session_id.startswith('browser_')

    async def get_in_use(self) -> bool:
        """Thread-safe access to in_use flag"""
        async with self._state_lock:
            return self._in_use

    async def get_driver_reference(self) -> Optional[PlaywrightBrowser]:
        """Thread-safe access to browser reference (for external operations)"""
        async with self._state_lock:
            return self._browser

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    async def get_age(self) -> float:
        """Get browser age in seconds (thread-safe)"""
        async with self._state_lock:
            return time.time() - self._created_at

    async def get_idle_time(self) -> float:
        """Get browser idle time in seconds (thread-safe)"""
        async with self._state_lock:
            return time.time() - self._last_used

    async def idle_longer_than(self, seconds: float) -> bool:
        """Check if browser has been idle longer than specified time (thread-safe)"""
        idle_time = await self.get_idle_time()
        return idle_time > seconds

    # =========================================================================
    # INTERNAL IMPLEMENTATION (assumes _state_lock is held)
    # =========================================================================

    async def _start_browser_internal(self) -> None:
        """Internal Playwright browser startup (must be called under _state_lock)"""
        try:
            # Allocate debug port (kept for compatibility)
            self._debug_port = await self.debug_port_manager.allocate_port()

            # Log proxy usage if configured
            if self.proxy_url:
                logger.info(f"Browser {self.browser_id} using proxy relay: {self.proxy_url}")

            # Start Playwright with Patchright stealth
            self._playwright = async_playwright()
            playwright = await self._playwright.start()

            # Launch browser with stealth args (no user data dir in args)
            launch_args = self._get_launch_args()

            # Launch browser (don't use persistent context for now to keep it simple)
            logger.info(f"Browser {self.browser_id} launching with headless={self.headless}")

            self._browser = await playwright.chromium.launch(
                headless=self.headless,
                args=launch_args,
                # Patchright automatically applies stealth patches
            )

            logger.info(f"Playwright browser {self.browser_id} started successfully")

        except Exception as e:
            # Cleanup on failure
            if self._debug_port:
                await self.debug_port_manager.release_port(self._debug_port)
                self._debug_port = None
            await self._cleanup_playwright()
            raise RuntimeError(f"Failed to create Playwright browser for {self.browser_id}: {e}")

    def _get_launch_args(self) -> List[str]:
        """Get Chrome launch arguments optimized for stealth."""
        args = [
            # Patchright handles most stealth args automatically, but we can add extras
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-sandbox",  # May be needed in some environments
        ]

        # Add certificate handling for mitmproxy when using proxy
        if self.proxy_url:
            # Use comprehensive certificate ignoring for proxy connections
            # Based on latest Chrome/Chromium documentation
            args.extend([
                "--ignore-certificate-errors-spki-list",
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
                "--allow-running-insecure-content",
                "--ignore-urlfetcher-cert-requests",
                "--disable-web-security",  # Helps with certificate validation
                "--allow-insecure-localhost",  # For local proxy connections
                "--disable-features=VizDisplayCompositor",  # Reduces SSL-related issues
            ])
            logger.info(f"Browser {self.browser_id} configured with comprehensive SSL certificate ignoring for proxy connections")

        # Don't add user data dir here - Playwright handles it separately

        return args

    async def _cleanup_playwright(self) -> None:
        """Clean up Playwright resources."""
        try:
            # Close all contexts
            for context in self._contexts.values():
                try:
                    await context.close()
                except Exception as e:
                    logger.debug(f"Error closing context: {e}")
            self._contexts.clear()

            # Close browser
            if self._browser:
                try:
                    await self._browser.close()
                except Exception as e:
                    logger.debug(f"Error closing browser: {e}")
                self._browser = None

            # Stop playwright
            if self._playwright:
                try:
                    await self._playwright.stop()
                except Exception as e:
                    logger.debug(f"Error stopping playwright: {e}")
                self._playwright = None

        except Exception as e:
            logger.error(f"Error during Playwright cleanup: {e}")

    async def _get_context(self) -> BrowserContext:
        """Get or create browser context."""
        proxy_key = self.proxy_url or "direct"

        if proxy_key not in self._contexts:
            # Create new context
            context_options = {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                # Certificate handling now done at browser level via launch args
            }

            if self.proxy_url:
                context_options['proxy'] = {
                    'server': self.proxy_url
                }

            context = await self._browser.new_context(**context_options)
            self._contexts[proxy_key] = context

            logger.info(f"Created new context for proxy: {proxy_key}")

        return self._contexts[proxy_key]

    # Removed: _get_user_agent method - simple hardcoded string not worth a method

    # Removed: API monitoring methods moved to pool_utils.py

    # Removed: Enhanced wait strategy moved to pool_utils.py (browser_pool has better integrated version)

    # Removed: Ad blocking moved to ad_blocker.py, page cleanup moved to pool_utils.py

    # Removed: _get_cookies method - not used anywhere

    # Removed: _download_images method moved to pool_utils.py

    # Removed: _download_image_from_network method moved to pool_utils.py

    # Removed: _process_api_calls method - API processing now in browser_pool

    async def _check_validity_internal(self) -> bool:
        """Internal validity check (must be called under _state_lock)"""
        # If flag is already False, return immediately
        if not self._is_valid_flag:
            return False

        # If flag is True, perform the actual test
        if not self._browser:
            self._is_valid_flag = False
            return False

        try:
            # Check if Playwright browser is still connected
            if self._browser.is_connected():
                logger.debug(f"Browser {self.browser_id} validation successful")
                return True
            else:
                logger.warning(f"Browser {self.browser_id} is no longer connected")
                self._is_valid_flag = False
                return False
        except Exception as e:
            logger.warning(f"Browser {self.browser_id} validation failed: {e}")
            self._is_valid_flag = False
            return False

    async def _cleanup_internal(self) -> None:
        """Internal cleanup (must be called under _state_lock)"""
        try:
            # Close Playwright browser
            await self._cleanup_playwright()

            # Release debug port
            if self._debug_port:
                await self.debug_port_manager.release_port(self._debug_port)
                self._debug_port = None



            # Mark as invalid
            self._is_valid_flag = False

            logger.info(f"Browser {self.browser_id} cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup of browser {self.browser_id}: {e}")

    # Removed: _fetch_html_internal method - all functionality moved to browser_pool


    # Removed: _apply_post_fetch_strategy method - all functionality moved to pool_utils.py

    # =========================================================================
    # HELPER METHODS
    # =========================================================================



# Removed _create_chrome_options - no longer needed with Playwright

# Removed old Selenium methods - replaced with Playwright implementations above
