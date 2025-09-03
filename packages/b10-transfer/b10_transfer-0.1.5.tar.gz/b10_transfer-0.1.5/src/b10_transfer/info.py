import logging
from pathlib import Path
from typing import Dict, Any

from .environment import get_cache_filename, get_environment_key
from .archive import get_file_size_mb
from .constants import (
    TORCH_CACHE_DIR,
    B10FS_CACHE_DIR,
    CACHE_PREFIX,
    CACHE_LATEST_SUFFIX,
    CACHE_FILE_EXTENSION,
)
from .utils import safe_execute, _is_b10fs_enabled

logger = logging.getLogger(__name__)


@safe_execute("Failed to calculate local cache size", None)
def _calculate_local_cache_size(torch_dir: Path) -> float:
    """Calculate the total size of local torch cache directory in megabytes.

    Args:
        torch_dir: Path to the torch cache directory to measure.

    Returns:
        float: Total size of all files in the directory in MB, or None if
               calculation fails (handled by decorator).

    Raises:
        Exception: Any filesystem errors during directory traversal
                  (caught by decorator and returns None).
    """
    # FIXME(SR): I guess directory structure could change here while rglob is running/iterating, so this is not safe.
    # But this is for debuggging anyways, we can remove/revisit this later. Not critical imho.
    local_size = sum(f.stat().st_size for f in torch_dir.rglob("*") if f.is_file())
    return local_size / (1024 * 1024)


@safe_execute("Error reading cache file", None)
def _process_cache_file(cache_file: Path) -> Dict[str, Any]:
    """Extract metadata information from a cache file.

    Args:
        cache_file: Path to the cache file to process.

    Returns:
        Dict[str, Any]: Dictionary containing cache file metadata with keys:
            - filename: The cache file name
            - environment_key: Extracted environment identifier
            - size_mb: File size in megabytes
            - is_current_environment: Whether this matches current environment
            - created_time: File creation timestamp
        Returns None if processing fails (handled by decorator).

    Raises:
        Exception: Any errors reading file metadata (caught by decorator).
    """
    # Extract env key: cache_a1b2c3d4e5f6.latest.tar.gz
    env_key = cache_file.name.replace(CACHE_PREFIX, "").replace(
        f"{CACHE_LATEST_SUFFIX}{CACHE_FILE_EXTENSION}", ""
    )

    return {
        "filename": cache_file.name,
        "environment_key": env_key,
        "size_mb": get_file_size_mb(cache_file),
        "is_current_environment": env_key == get_environment_key(),
        "created_time": cache_file.stat().st_mtime,
    }


def get_cache_info() -> Dict[str, Any]:
    """Get comprehensive information about the current cache state.

    This function provides a snapshot of both local and b10fs cache status,
    including existence, sizes, and environment information. It safely handles
    cases where b10fs is unavailable or directories don't exist.

    Returns:
        Dict[str, Any]: Dictionary containing cache information with keys:
            - environment_key: Current environment identifier hash
            - local_cache_exists: Whether local torch cache has content
            - b10fs_enabled: Whether b10fs filesystem is available
            - b10fs_cache_exists: Whether cache exists on b10fs
            - local_cache_size_mb: Local cache size in MB (if exists)
            - b10fs_cache_size_mb: B10fs cache size in MB (if exists)

    Raises:
        No exceptions are raised; errors are handled gracefully with None values.
    """
    torch_dir = Path(TORCH_CACHE_DIR)
    b10fs_dir = Path(B10FS_CACHE_DIR)
    cache_filename = get_cache_filename()
    cache_file = (
        b10fs_dir / f"{cache_filename}{CACHE_LATEST_SUFFIX}{CACHE_FILE_EXTENSION}"
    )

    info = {
        "environment_key": get_environment_key(),
        "local_cache_exists": torch_dir.exists() and any(torch_dir.iterdir()),
        "b10fs_enabled": _is_b10fs_enabled(),
        "b10fs_cache_exists": cache_file.exists() if _is_b10fs_enabled() else False,
    }

    # Add size info
    if info["local_cache_exists"]:
        info["local_cache_size_mb"] = _calculate_local_cache_size(torch_dir)

    if info["b10fs_cache_exists"] and _is_b10fs_enabled():
        info["b10fs_cache_size_mb"] = get_file_size_mb(cache_file)

    return info


def list_available_caches() -> Dict[str, Any]:
    """List all available cache files with their metadata and environment info.

    This function scans the b10fs directory for all cache files and returns
    detailed information about each one, including which environment they
    belong to and their creation times. Results are sorted by creation time.

    Returns:
        Dict[str, Any]: Dictionary containing cache listing with keys:
            - caches: List of cache file dictionaries (from _process_cache_file)
            - current_environment: Current environment identifier
            - total_caches: Total number of cache files found
            - current_cache_exists: Whether current environment has a cache
            - b10fs_enabled: Whether b10fs is available
            - error: Error message if b10fs is not enabled

    Raises:
        No exceptions are raised; individual file errors are handled gracefully
        and problematic files are skipped.
    """
    if not _is_b10fs_enabled():
        return {
            "caches": [],
            "current_environment": get_environment_key(),
            "b10fs_enabled": False,
            "error": "b10fs is not enabled",
        }

    b10fs_dir = Path(B10FS_CACHE_DIR)

    if not b10fs_dir.exists():
        return {
            "caches": [],
            "current_environment": get_environment_key(),
            "b10fs_enabled": True,
        }

    caches = []

    # Find all latest cache files
    for cache_file in b10fs_dir.glob(
        f"{CACHE_PREFIX}*{CACHE_LATEST_SUFFIX}{CACHE_FILE_EXTENSION}"
    ):
        cache_info = _process_cache_file(cache_file)
        if cache_info:
            caches.append(cache_info)

    # Sort by creation time (newest first)
    caches.sort(key=lambda x: x["created_time"], reverse=True)

    return {
        "caches": caches,
        "current_environment": get_environment_key(),
        "total_caches": len(caches),
        "current_cache_exists": any(c["is_current_environment"] for c in caches),
        "b10fs_enabled": True,
    }
