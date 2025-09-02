"""
Context Slot Module

This module contains the ContextSlot class that represents a single browser context slot
in the browser pool system.
"""

import time
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass

try:
    from patchright.async_api import Browser as PlaywrightBrowser, BrowserContext, Page
except ImportError:
    raise ImportError("patchright is required. Install with: pip install patchright")

logger = logging.getLogger(__name__)


@dataclass
class ContextSlot:
    """Single browser context slot"""
    browser_id: int
    context_id: int
    browser: PlaywrightBrowser
    context: BrowserContext
    proxy_url: Optional[str]  # Simple proxy URL instead of proxy manager
    page: Optional[Page] = None  # Persistent page for this slot

    # State
    in_use: bool = False
    is_bad: bool = False

    # Session management (renamed from assigned_client)
    session_id: Optional[str] = None
    app_name: Optional[str] = None
    session_name: Optional[str] = None
    last_request_url: Optional[str] = None
    last_response_json: Optional[Dict[str, Any]] = None
    is_sticky: bool = False

    # Stats
    request_count: int = 0
    created_at: float = 0
    last_used: float = 0

    def __post_init__(self):
        self.created_at = time.time()
        self.last_used = time.time()

    @property
    def slot_id(self) -> str:
        return f"browser_{self.browser_id}_context_{self.context_id}"

    @property
    def assigned_client(self) -> Optional[str]:
        """Compatibility property - returns session_id"""
        return self.session_id

    def mark_bad(self, reason: str):
        """Mark this browser (and all its contexts) as bad"""
        self.is_bad = True
        # Also mark the browser instance as invalid
        self.browser._is_valid_flag = False
        logger.warning(f"Marked browser {self.browser_id} as bad: {reason}")

    def assign_to_request(self, session_id: str, url: str, app_name: str = None, session_name: str = None):
        """
        Immediately assign slot to request with all metadata
        """
        self.session_id = session_id
        self.app_name = app_name
        self.session_name = session_name
        self.last_request_url = url
        self.is_sticky = False  # Don't make sticky by default - let caller decide
        self.in_use = True
        self.last_used = time.time()

        logger.debug(f"Assigned slot {self.slot_id} to session {session_id} for {url}")

    def try_assign_to_request(self, session_id: str, url: str, app_name: str = None, session_name: str = None) -> bool:
        """
        Atomically try to assign slot to request - returns True if successful, False if slot was taken
        """
        # Check and assign atomically using the in_use flag as a lock
        if self.in_use or self.is_sticky:
            return False

        # Atomic assignment
        self.session_id = session_id
        self.app_name = app_name
        self.session_name = session_name
        self.last_request_url = url
        self.is_sticky = False  # Don't make sticky by default - let caller decide
        self.in_use = True
        self.last_used = time.time()

        logger.debug(f"Atomically assigned slot {self.slot_id} to session {session_id} for {url}")
        return True

    def make_sticky(self):
        """Make this slot sticky for session reuse"""
        self.is_sticky = True
        logger.debug(f"Made slot {self.slot_id} sticky for session {self.session_id}")

    def complete_request(self, response_json: Dict[str, Any]):
        """
        Complete request - only set in_use=False, preserve all metadata
        """
        self.last_response_json = response_json
        self.in_use = False  # Only this changes
        self.request_count += 1
        self.last_used = time.time()

        # Keep: session_id, app_name, session_name, last_request_url, is_sticky
        logger.debug(f"Completed request for session {self.session_id} on slot {self.slot_id} (sticky={self.is_sticky})")

    def expire_sticky(self):
        """
        Expire sticky session - only set is_sticky=False, preserve all metadata
        """
        logger.info(f"Expiring sticky session {self.session_id} on slot {self.slot_id} (idle for {time.time() - self.last_used:.1f}s)")
        self.is_sticky = False  # Only this changes

        # Keep: session_id, app_name, session_name, last_request_url, last_response_json

    def is_empty(self) -> bool:
        """Check if slot is available for new sessions"""
        return not self.in_use and not self.is_sticky

    def is_available_for_session(self, session_id: str) -> bool:
        """Check if slot is available for a specific session"""
        return self.session_id == session_id and not self.in_use

    def is_sticky_expired(self, ttl_seconds: int) -> bool:
        """Check if sticky session has expired"""
        if not self.session_id or not self.is_sticky:
            return False
        return (time.time() - self.last_used) > ttl_seconds

    async def get_page(self) -> Page:
        """Get or create the persistent page for this slot"""
        if self.page is None:
            self.page = await self.context.new_page()
            logger.debug(f"Created new page for slot {self.slot_id}")
        return self.page

    async def cleanup(self):
        """Clean up this slot's context and page - browser cleanup is handled by pool"""
        try:
            # Close page first
            if self.page:
                try:
                    if not self.page.is_closed():
                        await self.page.close()
                        logger.debug(f"Closed page for slot {self.slot_id}")
                    else:
                        logger.debug(f"Page for slot {self.slot_id} already closed")
                except Exception as e:
                    logger.debug(f"Error closing page for slot {self.slot_id}: {e}")
                self.page = None

            # Then close context
            if self.context:
                await self.context.close()
                logger.debug(f"Closed context for slot {self.slot_id}")
        except Exception as e:
            logger.debug(f"Error closing context for slot {self.slot_id}: {e}")

        # Note: Browser and playwright cleanup is handled at pool level
        # This slot only manages its own context and page
