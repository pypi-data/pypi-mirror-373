"""
Entry point for running multi-browser-crawler as a module.

Usage:
    python -m multi_browser_crawler.browser_cli --help
    python -m multi_browser_crawler.browser_cli fetch https://example.com
"""

from multi_browser_crawler.browser_cli import cli_main

if __name__ == "__main__":
    cli_main()
