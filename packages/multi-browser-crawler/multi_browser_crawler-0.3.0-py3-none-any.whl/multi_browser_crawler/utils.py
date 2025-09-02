#!/usr/bin/env python3
"""
Utility Functions
================

Common utility functions used across the multi-browser-crawler package.
"""

import os
import logging
import shutil
from typing import List

logger = logging.getLogger(__name__)


def safe_remove_directory(dir_path: str, description: str = "directory") -> bool:
    """
    Safely remove a directory with proper error handling and logging.

    Args:
        dir_path: Path to the directory to remove
        description: Human-readable description for logging

    Returns:
        True if removal was successful, False otherwise
    """
    try:
        shutil.rmtree(dir_path)
        dir_name = os.path.basename(dir_path)
        logger.info(f"Cleaned up {description}: {dir_name}")
        return True
    except Exception as e:
        dir_name = os.path.basename(dir_path)
        logger.debug(f"Could not clean up {description} {dir_name}: {e} (not critical)")
        return False


def cleanup_leftover_browser_data(browser_data_dir: str, keep_recent_count: int = 3) -> None:
    """
    Clean up leftover browser data from previous runs.
    Keeps only the most recent timestamped directories.

    Args:
        browser_data_dir: Base directory containing timestamped browser data folders
        keep_recent_count: Number of recent directories to keep (default: 3)
    """
    if not os.path.exists(browser_data_dir):
        return

    try:
        # Get all timestamped directories (format: YYYYMMDD_HHMMSS)
        timestamped_dirs = []
        for item in os.listdir(browser_data_dir):
            item_path = os.path.join(browser_data_dir, item)
            if os.path.isdir(item_path) and len(item) == 15 and item[8] == '_':
                try:
                    # Validate timestamp format
                    timestamp = item.replace('_', '')
                    int(timestamp)  # Should be a valid number
                    timestamped_dirs.append((item, item_path))
                except ValueError:
                    continue

        # Sort by timestamp (newest first)
        timestamped_dirs.sort(reverse=True)

        # Remove old directories, keeping only the most recent ones
        dirs_to_remove = timestamped_dirs[keep_recent_count:]
        
        if dirs_to_remove:
            logger.info(f"Cleaning up {len(dirs_to_remove)} old browser data directories")
            
            for dir_name, dir_path in dirs_to_remove:
                safe_remove_directory(dir_path, f"old browser data directory {dir_name}")
                
            logger.info(f"Kept {min(len(timestamped_dirs), keep_recent_count)} recent browser data directories")
        else:
            logger.debug("No old browser data directories to clean up")

    except Exception as e:
        logger.warning(f"Error during leftover browser data cleanup: {e}")


def get_timestamped_directories(base_dir: str) -> List[str]:
    """
    Get list of timestamped directories in a base directory.
    
    Args:
        base_dir: Base directory to search in
        
    Returns:
        List of timestamped directory names, sorted newest first
    """
    if not os.path.exists(base_dir):
        return []
    
    timestamped_dirs = []
    try:
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path) and len(item) == 15 and item[8] == '_':
                try:
                    # Validate timestamp format
                    timestamp = item.replace('_', '')
                    int(timestamp)  # Should be a valid number
                    timestamped_dirs.append(item)
                except ValueError:
                    continue
    except Exception as e:
        logger.warning(f"Error reading timestamped directories from {base_dir}: {e}")
    
    # Sort by timestamp (newest first)
    timestamped_dirs.sort(reverse=True)
    return timestamped_dirs


def ensure_directory_exists(dir_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        dir_path: Path to the directory
        
    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {dir_path}: {e}")
        return False
