"""Cooperative cleanup utilities for b10-transfer.

This module provides cooperative cleanup functionality where each pod/replica
helps maintain the health of shared resources in b10fs by removing stale
lock files and incomplete cache files.
"""

import fnmatch
import time
import logging
from pathlib import Path
from typing import List, Tuple

from .constants import (
    B10FS_CACHE_DIR,
    CACHE_INCOMPLETE_SUFFIX,
    CLEANUP_LOCK_TIMEOUT_SECONDS,
    CLEANUP_INCOMPLETE_TIMEOUT_SECONDS,
)
from .utils import safe_execute, safe_unlink

logger = logging.getLogger(__name__)


@safe_execute("Failed to find stale files", [])
def _find_stale_files(
    directory: Path, pattern: str, timeout_seconds: int
) -> List[Path]:
    """Find files matching pattern that are older than timeout_seconds.

    Args:
        directory: Directory to search in
        pattern: Glob pattern to match files (only searches current directory, not subdirs)
        timeout_seconds: Age threshold in seconds

    Returns:
        List of Path objects for stale files
    """
    if not directory.exists():
        return []

    current_time = time.time()
    stale_files = []

    # Use iterdir() + fnmatch for explicit file-only matching in current directory

    for file_path in directory.iterdir():
        # Skip directories - we only want files
        if not file_path.is_file():
            logger.warning(
                f"Found non-file in b10fs cache directory: {file_path}, skipping consideration for deletion in cleanup phase."
            )
            continue

        # Check if filename matches pattern for the type of file we're looking for
        if not fnmatch.fnmatch(file_path.name, pattern):
            logger.warning(
                f"Found non-matching file in b10fs cache directory: {file_path}, skipping consideration for deletion in cleanup phase."
            )
            continue

        try:
            file_age = current_time - file_path.stat().st_mtime
            if file_age > timeout_seconds:
                stale_files.append(file_path)
        except OSError:
            # File might have been deleted already
            continue

    return stale_files


@safe_execute("Failed to cleanup files", 0)
def _cleanup_files(files: List[Path], file_type: str) -> int:
    """Clean up a list of files and return count of successfully cleaned files.

    Args:
        files: List of file paths to clean up
        file_type: Description of file type for logging (e.g., "lock", "incomplete")

    Returns:
        Number of files successfully cleaned up
    """
    cleaned_count = 0

    for file_path in files:
        try:
            file_age = time.time() - file_path.stat().st_mtime
            safe_unlink(
                file_path, f"Failed to clean stale {file_type} file: {file_path}"
            )
            cleaned_count += 1
            logger.debug(
                f"Cleaned stale {file_type} file: {file_path.name} (age: {file_age:.1f}s)"
            )
        except OSError:
            # File might have been deleted by another pod
            continue

    return cleaned_count


@safe_execute("Cooperative cleanup failed", None)
def cooperative_cleanup_b10fs() -> None:
    """Clean up stale shared resources in b10fs cooperatively.

    Each pod/replica calls this function to help maintain system health by
    removing files that are likely orphaned due to pod crashes or failures.

    Removes:
    - Lock files older than CLEANUP_LOCK_TIMEOUT_SECONDS (*.lock)
    - Incomplete cache files older than CLEANUP_INCOMPLETE_TIMEOUT_SECONDS (*.incomplete*)

    Does NOT remove:
    - Final cache files (*.latest.tar.gz) - these are the actual cached results
    - Files newer than the configured thresholds (may be from active operations)

    This function is safe to run concurrently from multiple pods as file
    deletion operations are atomic and missing files are handled gracefully.
    """
    b10fs_dir = Path(B10FS_CACHE_DIR)
    if not b10fs_dir.exists():
        logger.debug("b10fs cache directory doesn't exist, skipping cleanup")
        return

    # Find and clean stale lock files
    stale_locks = _find_stale_files(b10fs_dir, "*.lock", CLEANUP_LOCK_TIMEOUT_SECONDS)
    cleaned_locks = _cleanup_files(stale_locks, "lock")

    # Find and clean stale incomplete cache files
    incomplete_pattern = f"*{CACHE_INCOMPLETE_SUFFIX}*"
    stale_incomplete = _find_stale_files(
        b10fs_dir, incomplete_pattern, CLEANUP_INCOMPLETE_TIMEOUT_SECONDS
    )
    cleaned_incomplete = _cleanup_files(stale_incomplete, "incomplete cache")

    # Log summary
    total_cleaned = cleaned_locks + cleaned_incomplete
    if total_cleaned > 0:
        logger.info(
            f"Cooperative cleanup: removed {cleaned_locks} stale locks, "
            f"{cleaned_incomplete} incomplete files"
        )
    else:
        logger.debug("Cooperative cleanup: no stale files found")


def get_cleanup_info() -> dict:
    """Get information about cleanup configuration and current state.

    Returns:
        dict: Dictionary containing cleanup configuration and statistics:
            - lock_timeout_seconds: Current lock file cleanup threshold
            - incomplete_timeout_seconds: Current incomplete file cleanup threshold
            - b10fs_cache_dir: Path to b10fs cache directory
            - b10fs_exists: Whether b10fs cache directory exists
            - stale_locks_count: Number of lock files that would be cleaned
            - stale_incomplete_count: Number of incomplete files that would be cleaned
    """
    b10fs_dir = Path(B10FS_CACHE_DIR)

    info = {
        "lock_timeout_seconds": CLEANUP_LOCK_TIMEOUT_SECONDS,
        "incomplete_timeout_seconds": CLEANUP_INCOMPLETE_TIMEOUT_SECONDS,
        "b10fs_cache_dir": str(b10fs_dir),
        "b10fs_exists": b10fs_dir.exists(),
        "stale_locks_count": len(
            _find_stale_files(b10fs_dir, "*.lock", CLEANUP_LOCK_TIMEOUT_SECONDS)
        ),
        "stale_incomplete_count": len(
            _find_stale_files(
                b10fs_dir,
                f"*{CACHE_INCOMPLETE_SUFFIX}*",
                CLEANUP_INCOMPLETE_TIMEOUT_SECONDS,
            )
        ),
    }

    return info
