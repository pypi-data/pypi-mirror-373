#!/usr/bin/env python3
"""
Browser CLI for Multi-Browser Crawler
=====================================

Clean, focused command-line interface for browser fetching operations.
"""

import argparse
import asyncio
import json
import sys
import os
from typing import Dict, Any

from multi_browser_crawler.browser_pool import BrowserPoolManager
from multi_browser_crawler.proxy_manager import ProxyManager


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="browser-cli",
        description="Browser fetching with proxy support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch a single URL
  browser-cli fetch https://example.com

  # Fetch with proxy relay
  browser-cli fetch https://example.com --proxy-url http://localhost:8080

  # Fetch with custom timeout
  browser-cli fetch https://example.com --timeout 60
        """
    )

    # Global options
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Page load timeout in seconds (default: 30)"
    )

    parser.add_argument(
        "--proxy-url",
        type=str,
        help="Single proxy relay URL (e.g., http://localhost:8080)"
    )



    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch a URL")
    fetch_parser.add_argument("url", help="URL to fetch")

    fetch_parser.add_argument(
        "--js-action",
        type=str,
        help="JavaScript to execute after page load"
    )
    fetch_parser.add_argument(
        "--output",
        type=str,
        help="Output file for HTML content"
    )



    return parser


async def cmd_fetch(args) -> int:
    """Handle fetch command."""
    try:
        # Create config dict directly
        config = {
            'headless': args.headless,
            'timeout': args.timeout,
            'proxy_url': args.proxy_url
        }

        # Initialize browser pool
        browser_pool = BrowserPoolManager(config)

        print(f"🌐 Fetching: {args.url}")

        # Fetch the URL
        fetch_params = {
            'url': args.url,
            'session_id': None,  # Use non-persistent browser for CLI
        }

        # Only add js_action if provided
        if args.js_action:
            fetch_params['js_action'] = args.js_action

        result = await browser_pool.fetch_html(**fetch_params)

        if result.get('error'):
            print(f"❌ Error: {result['error']}")
            return 1

        print(f"✅ Success!")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Load time: {result.get('load_time', 0):.2f}s")
        print(f"   HTML size: {len(result.get('html', ''))} characters")

        # Save to file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result.get('html', ''))
            print(f"   Saved to: {args.output}")

        # Cleanup
        await browser_pool.shutdown()
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1





async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to command handlers
    if args.command == "fetch":
        return await cmd_fetch(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


def cli_main():
    """Synchronous entry point for setuptools."""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()