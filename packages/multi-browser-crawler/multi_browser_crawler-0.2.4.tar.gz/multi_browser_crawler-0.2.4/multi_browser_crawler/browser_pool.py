"""
Simplified Browser Pool with Auto-Scaling

This module implements a simplified browser pool with dynamic auto-scaling capabilities.
It maintains a pool of browser contexts that can scale between min/max limits based on demand,
providing both predictable performance and efficient resource utilization.

Key Features:
- Dynamic auto-scaling between min/max browser limits
- Sticky session support for client persistence
- Automatic bad browser detection and replacement
- Proxy rotation per context
- Background maintenance and health monitoring
- Simplified client interface
"""

import asyncio
import time
import uuid
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

try:
    from patchright.async_api import async_playwright, Browser as PlaywrightBrowser, BrowserContext, Page
except ImportError:
    raise ImportError("patchright is required. Install with: pip install patchright")

from .context_slot import ContextSlot
from .ad_blocker import setup_ad_blocking
from .api_capture import ApiCapture
from .browser import Browser
from .proxy_manager import ProxyManager
from .pool_utils import (
    apply_pre_fetch_strategy,
    apply_post_fetch_strategy,
    group_slots_by_browser,
    extract_unique_browsers,
    expire_sticky_sessions,
    download_images,
    run_page_cleanup
)

logger = logging.getLogger(__name__)

# Removed ProxyManager class - using simple proxy URL approach

class SimpleBrowserPool:
    """Simplified browser context pool with auto-scaling"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # Auto-scaling configuration
        self.min_browsers = config.get('min_browsers', 2)
        self.max_browsers = config.get('max_browsers', 6)
        self.contexts_per_browser = config.get('contexts_per_browser', 4)

        # Sticky session TTL (default 5 minutes)
        self.sticky_ttl_seconds = config.get('sticky_ttl_seconds', 300)

        # Context recycling configuration
        self.max_requests_per_context = config.get('max_requests_per_context', 500)

        # Pool state
        self.slots: List[ContextSlot] = []
        self.bad_browsers: Set[int] = set()  # Browser IDs that need replacement

        # Configuration - Proxy Management
        self.proxy_url = config.get('proxy_url')  # Single proxy URL (direct use, no proxy manager)
        proxy_list = config.get('proxy_list', [])  # Proxy list parameter (uses proxy manager)

        # Initialize proxy manager - only for proxy lists, not single proxy URLs
        # Priority: proxy_url overrides proxy_list
        if self.proxy_url:
            # Direct proxy URL takes priority - no proxy manager needed
            self.proxy_manager = None
            logger.info(f"BrowserPoolManager initialized with single proxy URL (direct): {self.proxy_url}")
        elif proxy_list:
            # Use proxy manager for proxy lists (with rotation and health checking)
            self.proxy_manager = ProxyManager(proxy_list)
            logger.info(f"BrowserPoolManager initialized with ProxyManager: {len(proxy_list)} proxies")
        else:
            # No proxy configuration
            self.proxy_manager = None
            logger.info("BrowserPoolManager initialized without proxy configuration")

        self.headless = config.get('headless', True)
        self.timeout = config.get('timeout', 30)
        self.download_images_dir = config.get('download_images_dir')

        # Stats
        self.stats = {
            'requests_served': 0,
            'browsers_created': 0,
            'browsers_replaced': 0,
            'errors': 0,
            'concurrent_request_errors': 0,
            'dynamic_browsers_created': 0
        }

        # Locks (single lock for all pool state)
        self._pool_lock = asyncio.Lock()

        # Background tasks
        self._maintenance_task: Optional[asyncio.Task] = None
        self._initialized = False
        self._shutting_down = False

        # Track browser ID allocation
        self._next_browser_id = 0

        logger.info(f"SimpleBrowserPool configured: min={self.min_browsers}, max={self.max_browsers}, contexts_per_browser={self.contexts_per_browser}")

    async def initialize(self):
        """Initialize the browser pool"""
        if self._initialized:
            return

        logger.info("Initializing simplified browser pool...")

        try:
            await self._ensure_browser_count()

            # Start background maintenance task
            self._maintenance_task = asyncio.create_task(self._maintenance_loop())

            self._initialized = True
            total_slots = len(self.slots)
            current_browsers = set(slot.browser_id for slot in self.slots)
            logger.info(f"Browser pool initialized: {total_slots} context slots ready ({len(current_browsers)} browsers, min: {self.min_browsers}, max: {self.max_browsers})")

        except Exception as e:
            logger.error(f"Failed to initialize browser pool: {e}")
            await self.shutdown()
            raise

    async def _create_browser_with_contexts_return_slots(self, browser_id: int) -> List[ContextSlot]:
        """Create a browser with all its contexts and return the slots (doesn't add to pool)"""
        playwright_instance = None
        browser = None
        created_slots = []

        try:
            # Start playwright
            playwright_instance = async_playwright()
            playwright = await playwright_instance.start()

            # Launch browser
            browser = await playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    # TLS/Certificate handling for proxies
                    "--ignore-certificate-errors",
                    "--ignore-ssl-errors",
                    "--ignore-certificate-errors-spki-list",
                    "--disable-web-security",
                    "--allow-running-insecure-content",
                    # Proxy-specific settings
                    "--disable-features=VizDisplayCompositor"
                ]
            )

            # Browser validity is handled through slot marking, not direct flags

            # Create all contexts for this browser
            for context_id in range(self.contexts_per_browser):
                # Create context with proxy (if configured)
                context_options = {
                    'viewport': {'width': 1920, 'height': 1080},
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    # TLS/Certificate handling for proxies
                    'ignore_https_errors': True,  # Ignore SSL certificate errors
                    'accept_downloads': False,    # Disable downloads for security
                    'java_script_enabled': True   # Ensure JS is enabled
                }

                # Configure proxy - either from proxy manager (for lists) or direct URL
                proxy_config = None
                if self.proxy_manager:
                    # Use proxy manager for proxy lists (with rotation and health checking)
                    proxy_config = self.proxy_manager.get_random_proxy()
                    if proxy_config:
                        context_options['proxy'] = proxy_config
                        logger.info(f"Creating context {context_id} with proxy: {proxy_config['server']}")
                        logger.info(f"Proxy config: {proxy_config}")
                    else:
                        logger.warning(f"No healthy proxies available for context {context_id} - using direct connection")
                elif self.proxy_url:
                    # Use direct proxy URL (no proxy manager overhead)
                    proxy_config = {'server': self.proxy_url}
                    context_options['proxy'] = proxy_config
                    logger.info(f"Creating context {context_id} with proxy: {self.proxy_url}")
                    logger.info(f"Proxy config: {proxy_config}")
                else:
                    logger.info(f"Creating context {context_id} with direct connection (no proxy)")

                context = await browser.new_context(**context_options)

                # Create page for this context
                page = await context.new_page()

                # Create slot
                slot = ContextSlot(
                    browser_id=browser_id,
                    context_id=context_id,
                    browser=browser,
                    context=context,
                    proxy_url=proxy_config['server'] if proxy_config else None,
                    page=page
                )

                # Store full proxy config for tracking (add as custom attribute)
                slot.proxy_config = proxy_config

                created_slots.append(slot)

            self.stats['browsers_created'] += 1
            logger.debug(f"Created browser {browser_id} with {len(created_slots)} contexts")
            return created_slots

        except Exception as e:
            # Clean up partial creation
            for slot in created_slots:
                await slot.cleanup()

            if browser and playwright_instance:
                try:
                    await browser.close()
                    await playwright_instance.stop()
                except:
                    pass

            raise RuntimeError(f"Failed to create browser {browser_id}: {e}")

    async def _add_browser_with_contexts(self):
        """Create a browser with all its contexts and add to pool immediately"""
        try:
            browser_id = self._next_browser_id
            self._next_browser_id += 1

            # Create browser and contexts (slow operation - outside lock)
            new_slots = await self._create_browser_with_contexts_return_slots(browser_id)

            # Quick addition to pool (with lock)
            async with self._pool_lock:
                self.slots.extend(new_slots)

            # Track if this was demand-driven creation
            current_browsers_after = set(slot.browser_id for slot in self.slots)

            logger.info(f"Created browser {browser_id} with {len(new_slots)} contexts (total browsers: {len(current_browsers_after)})")

        except Exception as e:
            logger.error(f"Failed to create browser {browser_id}: {e}")


    async def get_slot(self, session_id: str, url: str, app_name: str = None, session_name: str = None, sticky: bool = False) -> ContextSlot:
        """
        Get and assign a slot for a session with clear sticky/non-sticky logic separation

        For sticky=True: Search for existing session_id, error if in use
        For sticky=False: Randomly assign least recently used available slot

        Waits up to 30 seconds for an available slot before failing
        Returns: slot
        """
        if not self._initialized:
            raise RuntimeError("Browser pool not initialized")

        if self._shutting_down:
            raise RuntimeError("Browser pool is shutting down")

        start_time = time.time()
        wait_timeout = 30.0  # 30 seconds max wait
        retry_interval = 0.1  # 100ms between attempts

        while True:
            selected_slot = None

            # Try to get and assign slot with clear sticky/non-sticky separation
            async with self._pool_lock:
                if sticky:
                    # STICKY=TRUE: Look for existing session_id, error if in use
                    for slot in self.slots:
                        if slot.session_id == session_id:
                            if slot.in_use:
                                raise RuntimeError(f"Sticky session {session_id} is already in use. Sequential access required.")

                            # Found existing sticky session - assign to request
                            slot.assign_to_request(session_id, url, app_name, session_name)
                            slot.make_sticky()  # Ensure it stays sticky
                            selected_slot = slot
                            logger.debug(f"Reusing sticky session {session_id} on slot {slot.slot_id}")
                            break

                    # If no existing sticky session found, get least recently used slot and make it sticky
                    if selected_slot is None:
                        available_slots = [slot for slot in self.slots if slot.is_empty()]
                        if available_slots:
                            # Sort by last_used (ascending) to get least recently used
                            available_slots.sort(key=lambda s: s.last_used)
                            selected_slot = available_slots[0]
                            selected_slot.assign_to_request(session_id, url, app_name, session_name)
                            selected_slot.make_sticky()
                            logger.debug(f"Created new sticky session {session_id} on slot {selected_slot.slot_id}")

                else:
                    # STICKY=FALSE: Randomly assign least recently used available slot
                    # Do NOT match by session_id - always get a fresh available slot
                    available_slots = [slot for slot in self.slots if slot.is_empty()]
                    if available_slots:
                        # Sort by last_used (ascending) to get least recently used
                        available_slots.sort(key=lambda s: s.last_used)
                        selected_slot = available_slots[0]
                        selected_slot.assign_to_request(session_id, url, app_name, session_name)
                        # Do NOT make sticky - leave as non-sticky
                        logger.debug(f"Assigned non-sticky session {session_id} to least recently used slot {selected_slot.slot_id}")

            # If we got a slot, return it
            if selected_slot is not None:
                elapsed = time.time() - start_time
                if elapsed > 0.5:  # Log if we had to wait significantly
                    logger.info(f"Assigned slot to session {session_id} (sticky={sticky}) after {elapsed:.1f}s wait")
                return selected_slot

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed >= wait_timeout:
                raise RuntimeError(f"No available slots after waiting {elapsed:.1f}s (capacity: {len(self.slots)} slots, sticky={sticky})")

            # Wait before retrying
            await asyncio.sleep(retry_interval)

    def return_slot(self, slot: ContextSlot, response_data: Dict[str, Any] = None):
        """
        Return a slot after request completion - only sets in_use=False, preserves metadata
        """
        if response_data:
            slot.complete_request(response_data)
        else:
            # Simple return without response data
            slot.in_use = False
            slot.last_used = time.time()

    async def _maintenance_loop(self):
        """Background maintenance: remove bad browsers, clean expired sticky sessions, and ensure target count"""
        while self._initialized and not self._shutting_down:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds

                # Clean up expired sticky sessions first
                await self._cleanup_expired_sticky_sessions()

                # Recycle high-usage contexts
                await self._recycle_high_usage_contexts()

                # Remove bad slots (contexts)
                await self._remove_bad_slots()

                # Remove bad browsers (playwright instances)
                await self._remove_invalid_browsers()

                # Then ensure we have enough browsers
                await self._ensure_browser_count()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in maintenance loop: {e}")

    async def _cleanup_expired_sticky_sessions(self):
        """
        Expire sticky sessions - only set is_sticky=False, preserve metadata
        """
        async with self._pool_lock:
            expired_count = expire_sticky_sessions(self.slots, self.sticky_ttl_seconds)

        if expired_count > 0:
            logger.info(f"Expired {expired_count} sticky sessions (metadata preserved)")

    async def _recycle_high_usage_contexts(self):
        """Recycle contexts that have exceeded the maximum request count"""
        if self.max_requests_per_context <= 0:  # Feature disabled
            return

        if not self.slots:
            return

        recycled_count = 0

        async with self._pool_lock:
            for slot in self.slots:
                # Only recycle contexts that are not currently in use and have exceeded the limit
                if (not slot.in_use and
                    slot.request_count >= self.max_requests_per_context and
                    not slot.is_bad):

                    # Mark slot as bad so it gets recycled by the maintenance loop
                    slot.is_bad = True
                    recycled_count += 1

                    logger.info(f"Marked context {slot.slot_id} for recycling after {slot.request_count} requests (limit: {self.max_requests_per_context})")

        if recycled_count > 0:
            logger.info(f"Marked {recycled_count} high-usage contexts for recycling")

    async def _remove_bad_slots(self):
        """Remove bad browsers and clean up their resources (but maintain minimum)"""
        bad_slots_to_remove = []

        # Quick removal from pool (with lock)
        async with self._pool_lock:
            # Find bad slots that are not in use
            all_bad_slots = [
                slot for slot in self.slots
                if slot.is_bad and not slot.in_use
            ]

            if not all_bad_slots:
                return
            browsers_with_bad_slots = set(slot.browser_id for slot in all_bad_slots)
            self.slots = [slot for slot in self.slots if slot not in all_bad_slots]
            logger.info(f"Removing {len(all_bad_slots)} bad slots from browsers: {browsers_with_bad_slots}")

        # Expensive cleanup outside lock
        if all_bad_slots:
            cleanup_tasks = [slot.cleanup() for slot in all_bad_slots]
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            logger.info(f"Cleaned up {len(bad_slots_to_remove)} bad slots")

    async def _remove_invalid_browsers(self):
        """Remove invalid browsers - first remove from slots (with lock), then remove browser instances"""
        browsers_to_remove = []

        async with self._pool_lock:
            # Get browsers and check which ones need removal
            browsers_info = self.get_browsers_from_slots()

            for browser_info in browsers_info:
                browser = browser_info['browser']
                slots = browser_info['slots']

                # Check if any slots are marked as bad and all slots are free
                has_bad_slots = any(slot.is_bad for slot in slots)
                all_slots_free = all(not slot.in_use for slot in slots)

                if has_bad_slots and all_slots_free:
                    browsers_to_remove.append(browser_info)

            # Remove all slots for browsers that need to be removed
            for browser_to_remove in browsers_to_remove:
                slots_to_remove = browser_to_remove['slots']
                browser_id = slots_to_remove[0].browser_id if slots_to_remove else None

                # Remove slots from pool
                for slot in slots_to_remove:
                    if slot in self.slots:
                        self.slots.remove(slot)

                if browser_id:
                    logger.info(f"Removed all slots for browser {browser_id}")

        # Destroy browsers outside lock
        for browser_to_remove in browsers_to_remove:
            browser = browser_to_remove['browser']
            slots = browser_to_remove['slots']
            browser_id = slots[0].browser_id if slots else "unknown"

            try:
                # Handle cleanup for Playwright Browser objects (not our Browser wrapper)
                if browser:
                    if hasattr(browser, 'cleanup'):
                        # Our Browser wrapper class
                        await browser.cleanup()
                    else:
                        # Playwright Browser object - close directly
                        await browser.close()
                    logger.debug(f"Cleaned up browser {browser_id}")
            except Exception as e:
                logger.error(f"Error cleaning up browser {browser_id}: {e}")

        if browsers_to_remove:
            logger.info(f"Cleaned up {len(browsers_to_remove)} invalid browsers")

    async def _ensure_browser_count(self):
        """Auto-scaling based on truly empty slots"""
        async with self._pool_lock:
            current_browsers = set(slot.browser_id for slot in self.slots)
            current_browser_count = len(current_browsers)

            # Count truly empty slots (no metadata, available for any session)
            empty_slots = sum(1 for slot in self.slots if slot.is_empty())

            # Need more browsers if:
            # 1. Below minimum, OR
            # 2. No empty slots AND below maximum (demand-driven scaling)
            need_browser = (
                current_browser_count < self.min_browsers or
                (empty_slots == 0 and current_browser_count < self.max_browsers)
            )

            if not need_browser:
                return

        await self._add_browser_with_contexts()

    def get_browsers_from_slots(self) -> List[Dict[str, Any]]:
        """Get browser information from slots in simplified format: [{'browser': Browser, 'slots': [Slots]}]"""
        return group_slots_by_browser(self.slots)

    def get_browsers(self) -> List[PlaywrightBrowser]:
        """Get array of browser instances from slots"""
        return extract_unique_browsers(self.slots)

    async def set_scaling_limits(self, min_browsers: int = None, max_browsers: int = None):
        """Dynamically adjust browser scaling limits"""
        if min_browsers is not None:
            if min_browsers < 1:
                raise ValueError("Minimum browsers must be at least 1")
            self.min_browsers = min_browsers

        if max_browsers is not None:
            if max_browsers < self.min_browsers:
                raise ValueError("Maximum browsers must be >= minimum browsers")
            self.max_browsers = max_browsers

        logger.info(f"Browser scaling limits updated: min={self.min_browsers}, max={self.max_browsers}")

        # Trigger immediate maintenance check to adjust if needed
        if self._maintenance_task and not self._maintenance_task.done():
            # The maintenance loop will pick up the new limits on next iteration
            pass

    async def get_status(self) -> Dict[str, Any]:
        """Get detailed pool status with full session history"""
        # Handle uninitialized state
        if not self._initialized:
            return {
                'pool_summary': {
                    'total_slots': 0,
                    'empty_slots': 0,
                    'active_sticky_slots': 0,
                    'expired_sticky_slots': 0,
                    'in_use_slots': 0,
                    'total_browsers': 0,
                    'current_browsers': 0,  # Compatibility field
                    'min_browsers': self.min_browsers,
                    'max_browsers': self.max_browsers,
                    'contexts_per_browser': self.contexts_per_browser,
                    'scaling_headroom': 0,
                    'initialized': False,
                    'shutting_down': self._shutting_down
                },
                'stats': self.stats.copy(),
                'slot_categories': {
                    'empty': [],
                    'active_sticky': [],
                    'expired_sticky': [],
                    'in_use': []
                },
                'browser_ids': [],
                'slots': []
            }

        # NO LOCK NEEDED - Just reading current state snapshot
        # Slight inconsistency is acceptable for monitoring purposes
        # This prevents admin page refreshes from blocking concurrent requests

        # Categorize slots for better visibility
        empty_slots = []
        active_sticky_slots = []
        expired_sticky_slots = []
        in_use_slots = []

        # Direct read without lock - atomic property access in Python
        for slot in self.slots:  # List iteration is atomic
            slot_info = {
                'slot_id': slot.slot_id,
                'browser_id': slot.browser_id,
                'context_id': slot.context_id,
                'in_use': slot.in_use,
                'is_sticky': slot.is_sticky,
                'session_id': slot.session_id,
                'app_name': slot.app_name,
                'session_name': slot.session_name,
                'last_request_url': slot.last_request_url,
                'idle_time': time.time() - slot.last_used if slot.last_used else 0,
                'request_count': slot.request_count,
                'is_bad': slot.is_bad,
                'last_response_status': slot.last_response_json.get('status') if slot.last_response_json else None
            }

            if slot.in_use:
                in_use_slots.append(slot_info)
            elif slot.is_sticky:
                active_sticky_slots.append(slot_info)
            elif slot.session_id:  # Has metadata but not sticky (expired)
                expired_sticky_slots.append(slot_info)
            else:
                empty_slots.append(slot_info)

        # Count actual browsers - snapshot read
        current_browsers = set(slot.browser_id for slot in self.slots)
        current_browser_count = len(current_browsers)

        return {
            'pool_summary': {
                'total_slots': len(self.slots),
                'empty_slots': len(empty_slots),
                'active_sticky_slots': len(active_sticky_slots),
                'expired_sticky_slots': len(expired_sticky_slots),
                'in_use_slots': len(in_use_slots),
                'total_browsers': current_browser_count,
                'current_browsers': current_browser_count,  # Compatibility field
                'min_browsers': self.min_browsers,
                'max_browsers': self.max_browsers,
                'contexts_per_browser': self.contexts_per_browser,
                'scaling_headroom': max(0, self.max_browsers - current_browser_count),
                'max_requests_per_context': self.max_requests_per_context,
                'initialized': self._initialized,
                'shutting_down': self._shutting_down
            },
            'stats': self.stats.copy(),
            'slot_categories': {
                'empty': empty_slots,
                'active_sticky': active_sticky_slots,
                'expired_sticky': expired_sticky_slots,
                'in_use': in_use_slots
            },
            'browser_ids': sorted(current_browsers),
            'slots': [
                {
                    'slot_id': slot.slot_id,
                    'in_use': slot.in_use,
                    'is_bad': slot.is_bad,
                    'session_id': slot.session_id,
                    'request_count': slot.request_count,

                    'idle_time': time.time() - slot.last_used,
                    'age': time.time() - slot.created_at
                }
                for slot in self.slots
            ]
        }

    async def shutdown(self):
        """Shutdown the pool"""
        if self._shutting_down:
            return

        logger.info("Shutting down browser pool...")
        self._shutting_down = True
        self._initialized = False

        # Cancel maintenance task
        if self._maintenance_task:
            self._maintenance_task.cancel()
            try:
                await self._maintenance_task
            except asyncio.CancelledError:
                pass

        # Wait for all slots to be released (with timeout)
        async with self._pool_lock:
            wait_start = time.time()
            while any(slot.in_use for slot in self.slots) and (time.time() - wait_start) < 30:
                logger.info("Waiting for active requests to complete...")
                await asyncio.sleep(1)

        # Clean up all resources
        cleanup_tasks = []
        async with self._pool_lock:
            for slot in self.slots:
                cleanup_tasks.append(slot.cleanup())
            self.slots.clear()

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        logger.info("Browser pool shutdown complete")





    async def _execute_page_request(self, url: str, session_id: str, app_name: str = None, session_name: str = None,
                                   js_action: Optional[str] = None, timeout: Optional[int] = None,
                                   wait_time: int = 5, ad_blocker: bool = True,
                                   block_content_types: Optional[List[str]] = None,
                                   setup_api_monitoring: bool = False, api_patterns: Optional[List[str]] = None,
                                   pre_fetch_strategy: str = 'none', post_fetch_strategy: str = 'none',
                                   images_to_capture: Optional[List[str]] = None, cleanup_page: str = 'none',
                                   sticky: bool = False) -> Dict[str, Any]:
        """
        Core method for executing page requests - shared by fetch_html and discover_api_calls

        Args:
            url: URL to load
            session_id: Session ID for session management
            app_name: Application name for tracking
            session_name: Session name for tracking
            js_action: JavaScript to execute after page load
            timeout: Request timeout in seconds
            wait_time: Additional wait time for content/APIs to load
            ad_blocker: Whether to enable ad blocking
            block_content_types: List of content types to block (e.g., ['script', 'stylesheet', 'image'])
            setup_api_monitoring: Whether to monitor API calls (discovery mode)
            api_patterns: List of URL patterns to capture (patterns mode)
            pre_fetch_strategy: Pre-request cleanup strategy:
                - 'none': No pre-cleanup, reuse page as-is (default, fastest)
                - 'blank': Navigate to about:blank before fetch (clean slate)
            post_fetch_strategy: Post-request cleanup strategy:
                - 'none': No cleanup, keep page as-is (default, fastest)
                - 'blank': Navigate to about:blank, clear storage (balanced)
                - 'page': Close page, create new one next request (slower, clean slate)
                - 'context': Close context, create new one next request (slowest, full isolation)
                - 'browser': Close browser, create new one next request (very slow, complete reset)
            images_to_capture: List of image URLs to download
            cleanup_page: Page cleanup mode ('none', 'simple', 'aggressive')
            sticky: Whether to make the session sticky for reuse (default: False)

        Returns:
            Dictionary with unified format: {status, html, title, api_calls, images}
            - status.cleanup contains cleanup results if cleanup was performed
        """
        logger.debug(f"_execute_page_request ENTRY for URL: {url}, session: {session_id}")

        try:
            logger.debug(f"Checking initialization status...")
            if not self._initialized:
                raise RuntimeError("Browser pool not initialized")

            if self._shutting_down:
                raise RuntimeError("Browser pool is shutting down")

            start_time = time.time()
            logger.debug(f"_execute_page_request initialization complete for URL: {url}, session: {session_id}")
        except Exception as e:
            logger.error(f"Error in _execute_page_request initialization: {e}")
            return {
                'status': {
                    'success': False,
                    'error': f'Initialization error: {str(e)}',
                    'url': url,
                    'load_time': 0
                },
                'html': None,
                'title': None,
                'api_calls': [],
                'images': []
            }

        # Step 1: Get slot with sticky parameter (sticky logic now handled inside get_slot)
        try:
            selected_slot = await self.get_slot(session_id, url, app_name, session_name, sticky)

        except Exception as e:
            logger.error(f"Failed to get slot for session {session_id}: {e}")
            return {
                'status': {
                    'success': False,
                    'error': f"Slot allocation failed: {str(e)}",
                    'url': url,
                    'load_time': time.time() - start_time
                },
                'html': None,
                'title': None,
                'api_calls': [],
                'images': []
            }

        # Step 2: Perform the request (outside lock)
        page = None  # Predefine to avoid locals() check
        try:
            # Get the persistent page for this slot
            page = await selected_slot.get_page()

            # Apply pre-fetch strategy
            await apply_pre_fetch_strategy(page, pre_fetch_strategy)

            # Set timeout
            page.set_default_timeout((timeout or self.timeout) * 1000)

            # Setup ad blocking if requested
            if ad_blocker:
                await setup_ad_blocking(page, enabled=True)

            # Setup content type blocking if requested
            if block_content_types:
                async def block_content_types_handler(route):
                    """Block specific content types"""
                    request = route.request
                    if request.resource_type in block_content_types:
                        await route.abort()
                    else:
                        await route.continue_()

                await page.route('**/*', block_content_types_handler)

            # Setup API monitoring if requested
            api_capture = None
            if setup_api_monitoring or api_patterns:
                # Determine mode based on parameters
                if setup_api_monitoring:
                    api_capture = ApiCapture(mode="discovery")
                else:
                    api_capture = ApiCapture(mode="patterns", api_patterns=api_patterns)

                await api_capture.setup_monitoring(page)

            # Apply page cleanup if requested (before navigation)
            cleanup_result = {}
            if cleanup_page and cleanup_page != 'none':
                cleanup_result = await run_page_cleanup(page, cleanup_page)

            # Navigate to URL
            operation_type = "API discovery" if setup_api_monitoring else "HTML fetch"
            logger.info(f"{operation_type} from {url} (session: {session_id}, app: {app_name}, slot: {selected_slot.slot_id})")
            await page.goto(url, wait_until='domcontentloaded')

            # Execute custom JavaScript if provided
            if js_action:
                try:
                    # Basic security validation
                    dangerous_patterns = ['eval(', 'Function(', 'innerHTML', 'document.write', 'setTimeout(', 'setInterval(']
                    if any(pattern in js_action for pattern in dangerous_patterns):
                        logger.warning(f"Potentially unsafe JavaScript detected: {js_action[:100]}...")
                        raise ValueError("Unsafe JavaScript pattern detected")

                    await page.evaluate(js_action)
                    logger.debug(f"Executed custom JavaScript for {operation_type}")

                    # Enhanced wait strategy (only when JS is executed)
                    await asyncio.sleep(2)  # Universal politeness wait

                    try:
                        # Wait for network idle
                        await page.wait_for_load_state('networkidle', timeout=8000)
                    except:
                        # If network idle fails, use additional wait time
                        await asyncio.sleep(wait_time if setup_api_monitoring else 1)

                    # Final wait for API calls if monitoring
                    if setup_api_monitoring:
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"JavaScript execution failed during {operation_type}: {e}")

            # Standard wait for non-JS requests
            else:
                await asyncio.sleep(wait_time if setup_api_monitoring else 1)

            # Collect results - minimal essential fields only (moved outside else block)
            html_content = None if setup_api_monitoring else await page.content()
            page_title = await page.title()

            # Get API results if monitoring was set up
            api_calls = []
            if api_capture:
                api_calls = api_capture.get_results()  # Simplified: get_results() now returns list directly

            # Download images if requested
            images = []
            if images_to_capture:
                images = await download_images(images_to_capture, page.url, page, self.download_images_dir)

            # Create status object with metadata
            status_info = {
                'success': True,
                'url': page.url,
                'load_time': time.time() - start_time
            }

            # Add cleanup stats to status if cleanup was performed
            if cleanup_result:
                status_info['cleanup'] = cleanup_result

            results = {
                'status': status_info,
                'html': html_content,
                'title': page_title,
                'api_calls': api_calls,
                'images': images
            }

            # Record proxy success if proxy was used
            if self.proxy_manager and hasattr(selected_slot, 'proxy_config') and selected_slot.proxy_config:
                self.proxy_manager.record_proxy_result(selected_slot.proxy_config, success=True)

            # Return slot with success
            self.return_slot(selected_slot, results)
            logger.debug(f"Returning successful results: {type(results)} - {list(results.keys()) if results else 'None'}")
            return results

        except Exception as e:
            # Intelligent error classification - only mark browser as bad for serious issues
            should_mark_bad = self._should_mark_browser_bad(e)

            if selected_slot:
                # Record proxy failure if proxy was used
                if self.proxy_manager and hasattr(selected_slot, 'proxy_config') and selected_slot.proxy_config:
                    self.proxy_manager.record_proxy_result(selected_slot.proxy_config, success=False)

                if should_mark_bad:
                    selected_slot.mark_bad(f"Browser/context failure: {e}")
                    logger.warning(f"Marked browser {selected_slot.browser_id} as bad due to: {e}")
                else:
                    logger.info(f"Recoverable error for browser {selected_slot.browser_id}: {e}")

                self.return_slot(selected_slot)

            self.stats['errors'] += 1
            logger.error(f"Request failed for session {session_id}: {e}")
            error_result = {
                'status': {
                    'success': False,
                    'error': str(e),
                    'url': url,
                    'load_time': time.time() - start_time
                },
                'html': None,
                'title': None,
                'api_calls': [],
                'images': []
            }
            logger.debug(f"Returning error results: {type(error_result)} - {list(error_result.keys())}")
            return error_result

        # This should never be reached, but ensures method never returns None
        logger.error(f"_execute_page_request reached end without return for URL: {url}, session: {session_id}")
        return {
            'status': {
                'success': False,
                'error': 'Method reached end without return',
                'url': url,
                'load_time': 0
            },
            'html': None,
            'title': None,
            'api_calls': [],
            'images': []
        }

    async def fetch_html(self, url: str, session_id: str, app_name: str = None, session_name: str = None,
                        api_patterns: Optional[List[str]] = None, js_action: Optional[str] = None,
                        timeout: Optional[int] = None, wait_time: int = 5, ad_blocker: bool = True,
                        block_content_types: Optional[List[str]] = None,
                        pre_fetch_strategy: str = 'none', post_fetch_strategy: str = 'none',
                        images_to_capture: Optional[List[str]] = None, cleanup_page: str = 'none',
                        sticky: bool = False) -> Dict[str, Any]:
        """
        Fetch HTML with strict session management and immediate slot assignment

        Args:
            url: URL to fetch
            session_id: Session ID for session management
            app_name: Application name for tracking
            session_name: Session name for tracking
            api_patterns: List of URL patterns to capture API calls (e.g., ['/api/', '/graphql'])
            js_action: JavaScript to execute after page load
            timeout: Request timeout in seconds
            wait_time: Additional wait time for content to load
            ad_blocker: Whether to enable ad blocking
            block_content_types: List of content types to block (e.g., ['script', 'stylesheet', 'image'])
            pre_fetch_strategy: Pre-request cleanup strategy ('none', 'blank')
            post_fetch_strategy: Post-request cleanup strategy ('none', 'blank', 'page', 'context', 'browser')
            images_to_capture: List of image URLs to download
            cleanup_page: Page cleanup mode ('none', 'simple', 'aggressive')
            sticky: Whether to make the session sticky for reuse (default: False)

        Returns:
            Dictionary with unified format: {status, html, title, api_calls, images}
            - status.cleanup contains cleanup results if cleanup was performed
        """
        result = await self._execute_page_request(
            url=url,
            session_id=session_id,
            app_name=app_name,
            session_name=session_name,
            js_action=js_action,
            timeout=timeout,
            wait_time=wait_time,
            ad_blocker=ad_blocker,
            block_content_types=block_content_types,
            setup_api_monitoring=False,
            api_patterns=api_patterns,
            pre_fetch_strategy=pre_fetch_strategy,
            post_fetch_strategy=post_fetch_strategy,
            images_to_capture=images_to_capture,
            cleanup_page=cleanup_page,
            sticky=sticky
        )

        # Handle case where _execute_page_request returns None
        if result is None:
            logger.error(f"_execute_page_request returned None for URL: {url}, session: {session_id}")
            result = {
                'status': {
                    'success': False,
                    'error': '_execute_page_request returned None',
                    'url': url,
                    'load_time': 0
                },
                'html': None,
                'title': None,
                'api_calls': [],
                'images': []
            }

        # Update stats for successful requests
        status_info = result.get('status', {})
        if isinstance(status_info, dict) and status_info.get('success', False):
            self.stats['requests_served'] += 1
        elif result.get('status') == 'success':  # Legacy compatibility
            self.stats['requests_served'] += 1

        return result

    def _should_mark_browser_bad(self, error: Exception) -> bool:
        """
        Intelligent error classification to determine if browser should be marked as bad.

        Based on Playwright error handling best practices:
        - Only mark bad for serious browser/context corruption issues
        - Keep browser for recoverable network/timeout/content errors

        Args:
            error: The exception that occurred

        Returns:
            True if browser should be marked as bad, False if error is recoverable
        """
        error_str = str(error).lower()
        error_type = type(error).__name__

        # 🚨 CRITICAL ERRORS - Mark browser as bad (browser/context corruption)
        critical_patterns = [
            # Browser process failures
            'browser has been closed',
            'browser process exited',
            'browser disconnected',
            'target closed',
            'target crashed',
            'context closed',
            'context disposed',

            # Memory/resource exhaustion
            'out of memory',
            'memory allocation failed',
            'resource exhausted',

            # Browser corruption
            'browser is not connected',
            'execution context was destroyed',
            'cannot find execution context',
            'page has been closed',
            'frame was detached',
        ]

        for pattern in critical_patterns:
            if pattern in error_str:
                logger.warning(f"Critical browser error detected: {pattern} in {error_str}")
                return True

        # ✅ RECOVERABLE ERRORS - Keep browser (network/content/timeout issues)
        recoverable_patterns = [
            # Network errors (very common with proxies)
            'net::err_proxy_connection_failed',
            'net::err_connection_refused',
            'net::err_connection_timeout',
            'net::err_connection_reset',
            'net::err_network_changed',
            'net::err_internet_disconnected',
            'net::err_name_not_resolved',
            'net::err_timed_out',
            'net::err_failed',

            # Timeout errors (page load issues, not browser issues)
            'timeout',
            'navigation timeout',
            'waiting for selector',
            'waiting for element',
            'page.goto: timeout',
            'page.click: timeout',
            'page.waitfor',

            # Content/parsing errors
            'unsafe javascript pattern detected',
            'javascript execution failed',
            'element not found',
            'selector not found',
            'no node found',
            'element is not attached',
            'element is not visible',
            'element is not enabled',

            # HTTP/server errors
            'http error',
            'status code',
            '404',
            '500',
            '502',
            '503',
            '504',

            # Security/permission errors
            'permission denied',
            'access denied',
            'cors',
            'cross-origin',
            'security policy violation',
        ]

        for pattern in recoverable_patterns:
            if pattern in error_str:
                logger.debug(f"Recoverable error detected: {pattern} in {error_str}")
                return False

        # 🤔 UNKNOWN ERRORS - Conservative approach: don't mark as bad
        # Better to have a slower browser than no browser
        logger.info(f"Unknown error type '{error_type}': {error_str[:100]}... - keeping browser (conservative)")
        return False

    async def discover_api_calls(self, url: str, session_id: str = None, js_action: Optional[str] = None,
                                timeout: Optional[int] = None, wait_time: int = 5,
                                ad_blocker: bool = True, block_content_types: Optional[List[str]] = None,
                                pre_fetch_strategy: str = 'none', post_fetch_strategy: str = 'none',
                                images_to_capture: Optional[List[str]] = None,
                                cleanup_page: str = 'none', sticky: bool = False) -> Dict[str, Any]:
        """
        Discover all API calls made during page load for parser development.

        This method is similar to fetch_html but focuses on API discovery rather than HTML content.
        It loads a page, waits for API calls to complete, and returns discovered API calls.

        Args:
            url: URL to analyze for API calls
            session_id: Session ID for session management (optional)
            js_action: JavaScript to execute after page load (optional)
            timeout: Request timeout in seconds (None = use default)
            wait_time: Additional wait time for API calls to complete
            ad_blocker: Whether to enable ad blocking

        Returns:
            List of discovered API calls with metadata
        """
        # Use a dedicated session for API discovery if none provided
        if session_id is None:
            session_id = f"api_discovery_{int(time.time())}"

        result = await self._execute_page_request(
            url=url,
            session_id=session_id,
            app_name="api_discovery",
            session_name="discover_api_calls",
            js_action=js_action,
            timeout=timeout,
            wait_time=wait_time,
            ad_blocker=ad_blocker,
            block_content_types=block_content_types,
            setup_api_monitoring=True,
            pre_fetch_strategy=pre_fetch_strategy,
            post_fetch_strategy=post_fetch_strategy,
            images_to_capture=images_to_capture,
            cleanup_page=cleanup_page,
            sticky=sticky
        )

        # Return the unified format (same as fetch_html)
        return result


# SpiderMCPClient removed - belongs in spider_mcp project, not multi-browser-crawler