"""
Ad Blocker for Multi-Browser-Crawler
====================================

Simple ad blocking implementation using Chrome DevTools Protocol to block
common ad networks and tracking domains. This replaces the complex database
rules with a maintainable Python file.

Usage:
    ad_blocker = AdBlocker()
    blocked_patterns = ad_blocker.get_block_patterns()
    # Use with Chrome CDP: Network.setBlockedURLs
"""

import logging
from typing import List, Set, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class AdBlocker:
    """Simple ad blocker with common ad network patterns"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._blocked_domains = self._get_blocked_domains()
        self._blocked_patterns = self._get_blocked_patterns()
        
    def _get_blocked_domains(self) -> Set[str]:
        """Get list of ad/tracking domains to block"""
        return {
            # Google Ads
            'googleadservices.com',
            'googlesyndication.com',
            'doubleclick.net',
            'googletagmanager.com',
            'googletagservices.com',
            'google-analytics.com',
            'googleanalytics.com',
            '2mdn.net',
            
            # Facebook/Meta
            'facebook.com/tr',
            'connect.facebook.net',
            'facebook.net',
            
            # Amazon
            'amazon-adsystem.com',
            'assoc-amazon.com',
            
            # Microsoft
            'bing.com/maps/embed',
            'clarity.ms',
            
            # Major Ad Networks
            'adnxs.com',           # AppNexus/Xandr
            'adsrvr.org',          # The Trade Desk
            'advertising.com',     # AOL/Verizon
            'adsystem.com',        # Various
            'criteo.com',          # Criteo
            'outbrain.com',        # Outbrain
            'taboola.com',         # Taboola
            'pubmatic.com',        # PubMatic
            'rubiconproject.com',  # Rubicon
            'openx.net',           # OpenX
            'casalemedia.com',     # Index Exchange
            'rlcdn.com',           # Rubicon
            'serving-sys.com',     # Sizmek
            'turn.com',            # Turn/Amobee
            'adsafeprotected.com', # Integral Ad Science
            'moatads.com',         # Moat/Oracle
            'scorecardresearch.com', # ComScore
            'quantserve.com',      # Quantcast
            'bluekai.com',         # Oracle BlueKai
            'adsafeprotected.com', # IAS
            'doubleverify.com',    # DoubleVerify
            'innovid.com',         # Innovid
            'teads.tv',            # Teads
            'smartadserver.com',   # Smart AdServer
            'amazon-adsystem.com', # Amazon DSP
            'adsafeprotected.com', # IAS
            'freestar.io',         # Freestar
            
            # Social Media Tracking
            'twitter.com/i/adsct',
            'analytics.twitter.com',
            'linkedin.com/px',
            'snap.licdn.com',
            'pinterest.com/ct',
            'analytics.pinterest.com',
            'tiktok.com/i18n/pixel',
            'analytics.tiktok.com',
            
            # Analytics & Tracking
            'hotjar.com',
            'fullstory.com',
            'logrocket.com',
            'segment.com',
            'mixpanel.com',
            'amplitude.com',
            'heap.io',
            'kissmetrics.com',
            'crazyegg.com',
            'optimizely.com',
            'gtm.js',
            
            # Video Ad Networks
            'spotxchange.com',
            'springserve.com',
            'aniview.com',
            'cedato.com',
            'beachfront.com',
            'contextweb.com',
            'rhythmone.com',
            'undertone.com',
            'yieldmo.com',
            'sovrn.com',
            
            # Mobile Ad Networks
            'applovin.com',
            'unity3d.com/ads',
            'chartboost.com',
            'vungle.com',
            'ironsrc.com',
            'tapjoy.com',
            'adcolony.com',
            
            # Affiliate Networks
            'cj.com',              # Commission Junction
            'linksynergy.com',     # Rakuten
            'shareasale.com',      # ShareASale
            'impact.com',          # Impact
            'partnerize.com',      # Partnerize
            'awin1.com',           # Awin
            'tradedoubler.com',    # Tradedoubler
            
            # CDN/Tracking Services
            'jsdelivr.net/npm/gtag',
            'unpkg.com/gtag',
            'cdnjs.cloudflare.com/ajax/libs/gtag',
        }
    
    def _get_blocked_patterns(self) -> List[str]:
        """Get URL patterns to block"""
        return [
            # Google Analytics & Tag Manager
            '*google-analytics.com/analytics.js*',
            '*google-analytics.com/ga.js*',
            '*googletagmanager.com/gtm.js*',
            '*googletagmanager.com/gtag/*',
            
            # Google Ads
            '*googlesyndication.com/pagead/*',
            '*googleadservices.com/pagead/*',
            '*doubleclick.net/gampad/*',
            '*doubleclick.net/pfadx/*',
            
            # Facebook Pixel
            '*facebook.com/tr*',
            '*connect.facebook.net/*/fbevents.js*',
            
            # Common ad paths
            '*/ads/*',
            '*/ad/*',
            '*/advert/*',
            '*/advertisement/*',
            '*/advertising/*',
            '*/adsystem/*',
            '*/adservice/*',
            '*/adserver/*',
            '*/adnxs/*',
            '*/doubleclick/*',
            '*/googlesyndication/*',
            '*/googleadservices/*',
            
            # Tracking pixels
            '*/pixel*',
            '*/track*',
            '*/analytics*',
            '*/metrics*',
            '*/beacon*',
            
            # Video ads
            '*/videoads/*',
            '*/video-ads/*',
            '*/vast/*',
            '*/vpaid/*',
            
            # Social tracking
            '*/twitter/ads/*',
            '*/linkedin/px/*',
            '*/pinterest/ct/*',
            '*/tiktok/pixel/*',
            
            # Generic patterns
            '*_ads_*',
            '*-ads-*',
            '*ads.*',
            '*ad.*',
            '*.ads.*',
        ]
    
    def get_block_patterns(self) -> List[str]:
        """Get all URL patterns to block"""
        if not self.enabled:
            return []
            
        patterns = []
        
        # Add domain-based patterns
        for domain in self._blocked_domains:
            patterns.append(f'*{domain}*')
            
        # Add specific URL patterns
        patterns.extend(self._blocked_patterns)
        
        return patterns
    
    def should_block_url(self, url: str) -> bool:
        """Check if a URL should be blocked"""
        if not self.enabled:
            return False
            
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc
            path = parsed.path
            
            # Check domain blocking
            for blocked_domain in self._blocked_domains:
                if blocked_domain in domain:
                    return True
            
            # Check path patterns
            full_url = url.lower()
            for pattern in self._blocked_patterns:
                # Simple pattern matching (could be improved with regex)
                pattern_clean = pattern.replace('*', '')
                if pattern_clean in full_url:
                    return True
                    
            return False
            
        except Exception as e:
            logger.debug(f"Error checking URL for blocking: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ad blocker statistics"""
        return {
            'enabled': self.enabled,
            'blocked_domains': len(self._blocked_domains),
            'blocked_patterns': len(self._blocked_patterns),
            'total_rules': len(self._blocked_domains) + len(self._blocked_patterns)
        }
    
    def add_custom_domain(self, domain: str) -> None:
        """Add a custom domain to block"""
        self._blocked_domains.add(domain.lower())
        
    def add_custom_pattern(self, pattern: str) -> None:
        """Add a custom URL pattern to block"""
        self._blocked_patterns.append(pattern.lower())
        
    def remove_domain(self, domain: str) -> bool:
        """Remove a domain from blocking"""
        try:
            self._blocked_domains.remove(domain.lower())
            return True
        except KeyError:
            return False
    
    def enable(self) -> None:
        """Enable ad blocking"""
        self.enabled = True
        
    def disable(self) -> None:
        """Disable ad blocking"""
        self.enabled = False


# Default instance for easy importing
default_ad_blocker = AdBlocker()


def get_ad_block_patterns(enabled: bool = True) -> List[str]:
    """Convenience function to get ad blocking patterns"""
    if not enabled:
        return []
    return default_ad_blocker.get_block_patterns()


def should_block_url(url: str, enabled: bool = True) -> bool:
    """Convenience function to check if URL should be blocked"""
    if not enabled:
        return False
    return default_ad_blocker.should_block_url(url)


async def setup_ad_blocking(page, enabled: bool = True) -> None:
    """
    Setup ad blocking for a Playwright page using comprehensive ad blocker rules

    Args:
        page: Playwright page instance
        enabled: Whether to enable ad blocking
    """
    if not enabled:
        return

    async def block_ads(route):
        """Route handler that blocks ads using comprehensive ad blocker logic"""
        url_to_check = route.request.url
        if should_block_url(url_to_check, enabled=True):
            await route.abort()
        else:
            await route.continue_()

    await page.route('**/*', block_ads)
