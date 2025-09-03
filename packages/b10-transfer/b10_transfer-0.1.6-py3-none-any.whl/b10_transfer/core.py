"""Core file transfer operations for b10-transfer.

This module provides generic file transfer functionality with space monitoring
and error handling for b10fs operations.
"""

import logging
import shutil
from pathlib import Path

from .utils import (
    timed_fn,
    safe_execute,
    safe_unlink,
)
from .space_monitor import (
    check_sufficient_disk_space,
    CacheSpaceMonitor,
    CacheOperationInterrupted,
    run_monitored_process,
    worker_process,
)
from .constants import (
    B10FS_CACHE_DIR,
    REQUIRED_B10FS_SPACE_MB,
    MIN_LOCAL_SPACE_MB,
    OperationStatus,
)

logger = logging.getLogger(__name__)


@timed_fn(logger=logger, name="Transferring file")
@safe_execute("Transfer failed", OperationStatus.ERROR)
def transfer(source: str, dest: str) -> OperationStatus:
    """Transfer a file from source to destination with space monitoring.

    This function copies a file from source to destination using the same
    monitored process approach as the cache operations. It monitors disk space
    at the destination and can interrupt the transfer if space becomes insufficient.

    Args:
        source: Path to the source file to copy.
        dest: Path to the destination where the file will be copied.

    Returns:
        OperationStatus:
              OperationStatus.SUCCESS if transfer was successful
              OperationStatus.ERROR if transfer failed due to insufficient disk space,
                file not found, or other errors.

    Raises:
        CacheOperationInterrupted: If transfer interrupted due to insufficient
                                  disk space (caught and returns OperationStatus.ERROR).
        Exception: Any other errors during transfer (caught and returns OperationStatus.ERROR).
    """
    source_path = Path(source)
    dest_path = Path(dest)

    # Validate source file exists
    if not source_path.exists():
        logger.error(f"Source file does not exist: {source}")
        return OperationStatus.ERROR

    # Create destination directory if it doesn't exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine appropriate space threshold based on destination directory
    dest_dir = dest_path.parent
    if str(dest_dir).startswith(B10FS_CACHE_DIR):
        # Transferring to b10fs - use b10fs space requirements
        space_threshold_mb = REQUIRED_B10FS_SPACE_MB
        logger.debug(
            f"Transfer to b10fs detected, using {space_threshold_mb:.1f}MB threshold"
        )
    else:
        # Transferring to local directory - use local space requirements
        space_threshold_mb = MIN_LOCAL_SPACE_MB
        logger.debug(
            f"Transfer to local directory detected, using {space_threshold_mb:.1f}MB threshold"
        )

    # Initial disk space check
    check_sufficient_disk_space(dest_dir, space_threshold_mb, "file transfer")
    logger.debug(
        f"Initial space check passed: {space_threshold_mb:.1f}MB required at destination"
    )

    # Start background space monitoring for destination directory
    space_monitor = CacheSpaceMonitor(space_threshold_mb, dest_dir)
    space_monitor.start()

    try:
        # Run monitored copy process
        logger.info(f"Starting transfer: {source} -> {dest}")
        run_monitored_process(
            _cache_copy_worker,
            (str(source_path), str(dest_path)),
            space_monitor,
            "file transfer",
            cleanup_func=lambda: safe_unlink(
                dest_path, f"Failed to cleanup interrupted transfer {dest_path}"
            ),
        )

        logger.info("File transfer complete")
        return OperationStatus.SUCCESS

    except CacheOperationInterrupted as e:
        logger.warning(f"File transfer interrupted: {e}")
        return OperationStatus.ERROR

    finally:
        space_monitor.stop()


@worker_process("Copy was cancelled before starting")
def _cache_copy_worker(source_path_str: str, dest_path_str: str) -> None:
    """Worker process that handles file copy operations.

    This function runs in a separate process to copy files between locations.
    It can be terminated externally if disk space becomes insufficient.

    Args:
        source_path_str: String path to the source file to copy.
        dest_path_str: String path where the file will be copied.
    """
    source_path = Path(source_path_str)
    dest_path = Path(dest_path_str)

    shutil.copy2(source_path, dest_path)
