"""
API Capture Module for Multi-Browser-Crawler
============================================

Universal API capture and handling for both fetch_html and discover_api_calls.
Supports two modes:
- "discovery": Capture all requests, filter to API calls, trim for size reduction
- "patterns": Only capture requests matching specific URL patterns
"""

import time
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class ApiCapture:
    """Universal API capture and handling for both fetch_html and discover_api_calls"""
    
    def __init__(self, mode: str = "discovery", api_patterns: Optional[List[str]] = None):
        """
        Initialize API capture
        
        Args:
            mode: "discovery" (capture all) or "patterns" (capture only matching patterns)
            api_patterns: List of URL patterns to match (only used in "patterns" mode)
        """
        self.mode = mode
        self.api_patterns = api_patterns or []
        self.captured_calls = []
        self.total_requests = 0
        
    def should_capture(self, url: str) -> bool:
        """Determine if this URL should be captured based on mode and patterns"""
        if self.mode == "discovery":
            # Capture all, will filter later
            return True
        elif self.mode == "patterns":
            # Only capture if matches patterns
            if not self.api_patterns:
                return False
            return any(pattern in url for pattern in self.api_patterns)
        return False
        
    async def setup_monitoring(self, page):
        """Setup response monitoring on the page"""
        async def handle_response(response):
            try:
                self.total_requests += 1
                url = response.url

                if self.should_capture(url):
                    # Capture response data for API calls
                    response_data = None
                    try:
                        content_type = response.headers.get('content-type', '').lower()
                        if 'json' in content_type:
                            response_data = await response.json()
                        elif 'xml' in content_type or 'text' in content_type:
                            response_data = await response.text()
                    except Exception as e:
                        logger.debug(f"Could not parse response data for {url}: {e}")

                    self.captured_calls.append({
                        'url': url,  # Fixed: use 'url' instead of 'url_path'
                        'method': response.request.method,
                        'status': response.status,
                        'content_type': response.headers.get('content-type', ''),
                        'response': response_data,  # Added: actual response data
                        'timestamp': time.time()
                    })
            except Exception as e:
                logger.debug(f"Error capturing API response: {e}")

        page.on('response', handle_response)
        
    def get_results(self) -> list:
        """Get API calls - simplified to just return the calls"""
        if self.mode == "discovery":
            # Filter to actual API calls and trim for size
            api_calls = self._filter_api_calls(self.captured_calls)
            # Limit to reduce size - keep first few of each type
            return self._trim_api_calls(api_calls, max_per_pattern=3)
        elif self.mode == "patterns":
            # Return all captured calls (already filtered by patterns)
            return self.captured_calls
        else:
            return []
        
    def _filter_api_calls(self, captured_calls: list) -> list:
        """Filter captured network requests to identify actual API calls"""
        api_calls = []
        for call in captured_calls:
            content_type = call.get('content_type', '').lower()
            url = call.get('url', '')  # Fixed: use 'url' instead of 'url_path'

            # Consider as API call if content type or URL suggests API
            is_api_call = (
                'json' in content_type or 'xml' in content_type or
                'api' in url.lower() or 'ajax' in url.lower() or
                '/v1/' in url or '/v2/' in url or
                call.get('method') in ['POST', 'PUT', 'PATCH', 'DELETE']
            )

            if is_api_call:
                api_calls.append(call)

        return api_calls
        
    def _trim_api_calls(self, api_calls: list, max_per_pattern: int = 3) -> list:
        """Trim API calls to reduce size - keep first few of each URL pattern"""
        pattern_counts = {}
        trimmed_calls = []

        for call in api_calls:
            url = call['url']  # Fixed: use 'url' instead of 'url_path'
            # Create a pattern key based on URL structure
            pattern_key = self._get_url_pattern(url)

            if pattern_counts.get(pattern_key, 0) < max_per_pattern:
                trimmed_calls.append(call)
                pattern_counts[pattern_key] = pattern_counts.get(pattern_key, 0) + 1

        return trimmed_calls
        
    def _get_url_pattern(self, url: str) -> str:
        """Extract URL pattern for grouping similar calls"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            # Group by domain + path structure (remove query params and specific IDs)
            path = parsed.path
            # Replace numbers with placeholder for grouping
            import re
            path = re.sub(r'/\d+', '/{id}', path)
            return f"{parsed.netloc}{path}"
        except:
            return url
