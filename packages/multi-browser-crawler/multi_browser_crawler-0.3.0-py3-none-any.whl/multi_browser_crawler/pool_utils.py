"""
Browser Pool Utilities
======================

Utility functions for browser pool operations including fetch strategies,
slot management, and session handling.
"""

import logging
from typing import List, Dict, Any, Set
from .context_slot import ContextSlot

try:
    from patchright.async_api import Browser as PlaywrightBrowser
except ImportError:
    raise ImportError("patchright is required. Install with: pip install patchright")

logger = logging.getLogger(__name__)


# =============================================================================
# FETCH STRATEGIES
# =============================================================================

async def apply_pre_fetch_strategy(page, strategy: str = 'none') -> None:
    """
    Apply pre-fetch strategy before loading content
    
    Args:
        page: Playwright page instance
        strategy: Pre-fetch strategy ('none', 'blank')
    """
    try:
        if strategy == 'none':
            # No pre-cleanup - reuse page as-is (fastest)
            logger.debug("Pre-fetch strategy: none - reusing page as-is")
            pass
        elif strategy == 'blank':
            # Navigate to blank page before fetch (clean slate)
            logger.debug("Pre-fetch strategy: blank - navigating to about:blank")
            await page.goto("about:blank", wait_until="domcontentloaded", timeout=5000)
        else:
            logger.warning(f"Unknown pre-fetch strategy: {strategy}, defaulting to 'none'")
    except Exception as e:
        logger.debug(f"Pre-fetch strategy '{strategy}' failed: {e}")


async def apply_post_fetch_strategy(page, slot, strategy: str = 'none') -> None:
    """
    Apply post-fetch strategy after loading content
    
    Args:
        page: Playwright page instance
        slot: ContextSlot instance
        strategy: Post-fetch strategy ('none', 'blank', 'page', 'context', 'browser')
    """
    try:
        if strategy == 'none':
            # No cleanup - keep page as-is (fastest)
            logger.debug("Post-fetch strategy: none - keeping page as-is")
            pass
        elif strategy == 'blank':
            # Navigate to blank page and clear storage (balanced)
            logger.debug("Post-fetch strategy: blank - navigating to about:blank and clearing storage")
            await page.goto('about:blank', wait_until='domcontentloaded', timeout=5000)
            await page.evaluate('try { localStorage.clear(); sessionStorage.clear(); } catch(e) {}')
        elif strategy == 'page':
            # Mark slot as bad - maintenance loop will clean up and create new page (slower, clean slate)
            logger.debug("Post-fetch strategy: page - marking slot as bad for page replacement")
            slot.mark_bad("Post-fetch page strategy - page replacement needed")
        elif strategy == 'context':
            # Mark slot as bad - maintenance loop will clean up and create new context (slowest, full isolation)
            logger.debug("Post-fetch strategy: context - marking slot as bad for context replacement")
            slot.mark_bad("Post-fetch context strategy - context replacement needed")
        elif strategy == 'browser':
            # Mark slot as bad - maintenance loop will clean up and create new browser (very slow, complete reset)
            logger.debug("Post-fetch strategy: browser - marking slot as bad for browser replacement")
            slot.mark_bad("Post-fetch browser strategy - browser replacement needed")
        else:
            logger.warning(f"Unknown post-fetch strategy: {strategy}, defaulting to 'blank'")
            # Default to blank cleanup
            await page.goto('about:blank', wait_until='domcontentloaded', timeout=5000)
            await page.evaluate('try { localStorage.clear(); sessionStorage.clear(); } catch(e) {}')
    except Exception as e:
        logger.debug(f"Post-fetch strategy '{strategy}' failed: {e}")


# =============================================================================
# SLOT UTILITIES
# =============================================================================

def group_slots_by_browser(slots: List[ContextSlot]) -> List[Dict[str, Any]]:
    """
    Group slots by browser ID and return browser information
    
    Args:
        slots: List of ContextSlot instances
        
    Returns:
        List of dicts with format: [{'browser': Browser, 'slots': [Slots]}]
    """
    browsers_dict = {}
    
    # Group slots by browser
    for slot in slots:
        browser_id = slot.browser_id
        if browser_id not in browsers_dict:
            browsers_dict[browser_id] = {
                'browser': slot.browser,
                'slots': []
            }
        browsers_dict[browser_id]['slots'].append(slot)
    
    # Convert to list format
    return list(browsers_dict.values())


def extract_unique_browsers(slots: List[ContextSlot]) -> List[PlaywrightBrowser]:
    """
    Extract unique browser instances from slots
    
    Args:
        slots: List of ContextSlot instances
        
    Returns:
        List of unique PlaywrightBrowser instances
    """
    browsers = []
    seen_browser_ids = set()
    
    for slot in slots:
        if slot.browser_id not in seen_browser_ids:
            browsers.append(slot.browser)
            seen_browser_ids.add(slot.browser_id)
    
    return browsers


def find_expired_sticky_sessions(slots: List[ContextSlot], ttl_seconds: int) -> List[ContextSlot]:
    """
    Find slots with expired sticky sessions
    
    Args:
        slots: List of ContextSlot instances
        ttl_seconds: TTL for sticky sessions in seconds
        
    Returns:
        List of slots with expired sticky sessions
    """
    expired_slots = []
    
    for slot in slots:
        if slot.is_sticky_expired(ttl_seconds):
            expired_slots.append(slot)
    
    return expired_slots


def expire_sticky_sessions(slots: List[ContextSlot], ttl_seconds: int) -> int:
    """
    Expire sticky sessions that have exceeded TTL

    Args:
        slots: List of ContextSlot instances
        ttl_seconds: TTL for sticky sessions in seconds

    Returns:
        Number of sessions expired
    """
    expired_count = 0

    for slot in slots:
        if slot.is_sticky_expired(ttl_seconds):
            slot.expire_sticky()  # Only sets is_sticky=False
            expired_count += 1

    return expired_count


# =============================================================================
# IMAGE DOWNLOAD UTILITIES
# =============================================================================

async def download_images(image_urls: List[str], base_url: str, page, download_dir: str = None) -> List[Dict[str, Any]]:
    """
    Download images using Playwright context (reusing already loaded images)

    Args:
        image_urls: List of image URLs to download
        base_url: Base URL for resolving relative URLs
        page: Playwright page instance
        download_dir: Directory to save images (optional)

    Returns:
        List of download results with metadata
    """
    downloaded = []

    for url in image_urls:
        try:
            # Resolve relative URLs
            if url.startswith('/'):
                from urllib.parse import urljoin
                url = urljoin(base_url, url)

            # Use Playwright to get the image data from browser cache/context
            try:
                # Load image extraction script from file
                import os
                js_file_path = os.path.join(os.path.dirname(__file__), 'js', 'extract_image.js')
                try:
                    with open(js_file_path, 'r', encoding='utf-8') as f:
                        extract_script = f.read()
                    # Execute the script with the URL parameter
                    image_data = await page.evaluate(f"({extract_script})('{url}')")
                except FileNotFoundError:
                    logger.warning(f"Image extraction JS file not found: {js_file_path}")
                    image_data = None

                if image_data:
                    # Extract base64 data
                    base64_data = image_data['dataURL'].split(',')[1] if image_data['dataURL'] else None

                    # Save to file if download directory is configured
                    local_path = None
                    if base64_data and download_dir:
                        import base64
                        import uuid
                        from datetime import datetime

                        # Create organized directory structure: yyyy/mm/dd/
                        now = datetime.now()
                        date_dir = os.path.join(
                            download_dir,
                            now.strftime('%Y'),
                            now.strftime('%m'),
                            now.strftime('%d')
                        )
                        os.makedirs(date_dir, exist_ok=True)

                        # Generate filename: yyyymmdd_hhmmss_random.ext
                        timestamp = now.strftime('%Y%m%d_%H%M%S')
                        random_suffix = uuid.uuid4().hex[:8]

                        # Determine extension from original URL or default to png
                        original_name = os.path.basename(url)
                        if original_name and '.' in original_name:
                            ext = original_name.split('.')[-1].lower()
                            if ext not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                                ext = 'png'
                        else:
                            ext = 'png'

                        filename = f"{timestamp}_{random_suffix}.{ext}"
                        local_path = os.path.join(date_dir, filename)

                        # Decode and save
                        image_bytes = base64.b64decode(base64_data)
                        with open(local_path, 'wb') as f:
                            f.write(image_bytes)

                    downloaded.append({
                        'url': url,
                        'status': 'success',
                        'method': 'playwright_canvas',
                        'size': len(base64_data) * 3 // 4 if base64_data else 0,  # Approximate size
                        'width': image_data.get('width', 0),
                        'height': image_data.get('height', 0),
                        'natural_width': image_data.get('naturalWidth', 0),
                        'natural_height': image_data.get('naturalHeight', 0),
                        'local_path': local_path,
                        'base64_data': base64_data[:100] + '...' if base64_data else None  # Truncated for logging
                    })
                else:
                    # Fallback: Use Playwright's network interception to get cached response
                    downloaded.append(await _download_image_from_network(url, page))

            except Exception as e:
                logger.debug(f"Canvas method failed for {url}: {e}")
                # Fallback to network method
                downloaded.append(await _download_image_from_network(url, page))

        except Exception as e:
            logger.warning(f"Failed to download image {url}: {e}")
            downloaded.append({
                'url': url,
                'status': 'error',
                'error': str(e)
            })

    return downloaded


async def _download_image_from_network(url: str, page) -> Dict[str, Any]:
    """
    Fallback method: Download image using Playwright's network context

    Args:
        url: Image URL to download
        page: Playwright page instance

    Returns:
        Download result with metadata
    """
    try:
        # Use the same context as the page to leverage cookies/auth
        context = page.context

        # Create a new page for the image request to avoid interfering with main page
        image_page = await context.new_page()

        try:
            # Navigate to the image URL
            response = await image_page.goto(url, timeout=10000)

            if response and response.status == 200:
                # Get the image data
                image_data = await response.body()

                return {
                    'url': url,
                    'status': 'success',
                    'method': 'playwright_network',
                    'size': len(image_data),
                    'width': 0,  # Network method doesn't provide dimensions
                    'height': 0,
                    'natural_width': 0,
                    'natural_height': 0,
                    'local_path': None,  # Network method doesn't save to file by default
                    'base64_data': None  # Network method doesn't provide base64
                }
            else:
                return {
                    'url': url,
                    'status': 'error',
                    'error': f"HTTP {response.status if response else 'No response'}",
                    'method': 'playwright_network'
                }

        finally:
            await image_page.close()

    except Exception as e:
        return {
            'url': url,
            'status': 'error',
            'error': str(e),
            'method': 'playwright_network'
        }


# =============================================================================
# PAGE CLEANUP UTILITIES
# =============================================================================

async def run_page_cleanup(page, cleanup_mode: str) -> Dict[str, Any]:
    """
    Run page cleanup based on specified mode

    Args:
        page: Playwright page instance
        cleanup_mode: Cleanup mode ('simple', 'aggressive', 'none')

    Returns:
        Cleanup statistics and results
    """
    cleanup_stats = {'mode': cleanup_mode, 'elements_removed': 0}

    try:
        if cleanup_mode == 'aggressive':
            # Load aggressive cleanup script from file
            import os
            js_file_path = os.path.join(os.path.dirname(__file__), 'js', 'cleanup_page.js')
            try:
                with open(js_file_path, 'r', encoding='utf-8') as f:
                    cleanup_script = f.read()
                result = await page.evaluate(cleanup_script)
                cleanup_stats['elements_removed'] = result.get('elementsRemoved', 0)
                cleanup_stats['categories_cleaned'] = result.get('categoriesCleaned', [])
            except FileNotFoundError:
                logger.warning(f"Page cleanup JS file not found: {js_file_path}")
                # Fallback to simple inline cleanup
                result = await page.evaluate("""
                    () => {
                        let removed = 0;
                        // Remove ads, popups, overlays
                        const selectors = [
                            '[class*="ad"]', '[id*="ad"]', '[class*="popup"]',
                            '[class*="overlay"]', '[class*="modal"]'
                        ];
                        selectors.forEach(selector => {
                            document.querySelectorAll(selector).forEach(el => {
                                el.remove();
                                removed++;
                            });
                        });
                        return {elementsRemoved: removed};
                    }
                """)
                cleanup_stats['elements_removed'] = result.get('elementsRemoved', 0)

        elif cleanup_mode == 'simple':
            # Simple cleanup - remove common ad/popup elements
            result = await page.evaluate("""
                () => {
                    let removed = 0;
                    const selectors = ['.ad', '#ad', '.popup', '.overlay'];
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            el.remove();
                            removed++;
                        });
                    });
                    return {elementsRemoved: removed};
                }
            """)
            cleanup_stats['elements_removed'] = result.get('elementsRemoved', 0)

        # 'none' mode does nothing

    except Exception as e:
        logger.warning(f"Page cleanup failed: {e}")
        cleanup_stats['error'] = str(e)

    return cleanup_stats
