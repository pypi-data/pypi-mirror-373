"""Space monitoring utilities for b10-tcache.

This module provides disk space monitoring functionality to prevent cache operations
from exhausting available disk space and causing system instability.
"""

import time
import logging
import shutil
import threading
import multiprocessing
from pathlib import Path
from multiprocessing import Process, Queue
from functools import wraps

from .constants import WorkerStatus, SPACE_MONITOR_CHECK_INTERVAL_SECONDS

logger = logging.getLogger(__name__)


class CacheOperationInterrupted(Exception):
    """Raised when a cache operation is interrupted due to insufficient disk space."""

    pass


def worker_process(cancelled_message: str):
    """Decorator for worker process functions to handle common try/catch/result_queue pattern.

    This decorator wraps worker functions to:
    1. Check for cancellation before starting
    2. Handle exceptions and put appropriate status in result_queue
    3. Put success status on completion

    Args:
        cancelled_message: Message to send if the worker is cancelled before starting

    Usage:
        @worker_process("Operation was cancelled before starting")
        def my_worker(arg1, arg2, result_queue, stop_event):
            # Your worker logic here
            # No need to handle try/catch or result_queue.put()
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            # Extract result_queue and stop_event from the end of args
            *worker_args, result_queue, stop_event = args

            try:
                # Check for stop signal before starting
                if stop_event.is_set():
                    result_queue.put((WorkerStatus.CANCELLED.value, cancelled_message))
                    return

                # Call the actual worker function with just the worker args
                func(*worker_args)

                # If we get here, the function completed successfully
                result_queue.put((WorkerStatus.SUCCESS.value, None))

            except Exception as e:
                result_queue.put((WorkerStatus.ERROR.value, str(e)))

        return wrapper

    return decorator


def get_available_disk_space_mb(path: Path) -> float:
    """Get available disk space in megabytes for the given path.

    This function returns the available disk space for the filesystem
    containing the specified path. It's useful for checking if there's
    enough space before performing disk-intensive operations.

    Args:
        path: Path to check disk space for. The path's parent directory
              will be used if the path itself doesn't exist.

    Returns:
        float: Available disk space in megabytes, or 0.0 if unable to
               determine (e.g., path doesn't exist or permission denied).

    Raises:
        No exceptions are raised; OSError is caught and returns 0.0.
    """
    try:
        # Ensure we check an existing directory
        check_path = path
        while not check_path.exists() and check_path != check_path.parent:
            check_path = check_path.parent

        if not check_path.exists():
            return 0.0

        # Get disk usage stats
        _, _, free_bytes = shutil.disk_usage(check_path)
        return free_bytes / (1024 * 1024)
    except OSError:
        return 0.0


def check_sufficient_disk_space(
    path: Path, required_mb: float, operation_name: str = "operation"
) -> None:
    """Check if there's sufficient disk space for an operation.

    This function verifies that the filesystem has enough available space
    for the specified operation, raising an exception if insufficient space
    is available.

    Args:
        path: Path where the operation will write data.
        required_mb: Required disk space in megabytes.
        operation_name: Name of the operation for error messages.

    Raises:
        CacheValidationError: If insufficient disk space is available.
    """
    from .utils import CacheValidationError

    available_mb = get_available_disk_space_mb(path)
    if available_mb < required_mb:
        raise CacheValidationError(
            f"Insufficient disk space for {operation_name}: "
            f"required {required_mb:.1f}MB, available {available_mb:.1f}MB"
        )


class CacheSpaceMonitor:
    """Background monitor for disk space during cache operations.

    This class implements a daemon thread that continuously monitors available
    disk space and signals when space falls below required thresholds. It follows
    the SpaceMonitor pattern from node-warmer for graceful operation interruption.
    """

    def __init__(
        self, required_space_mb: float, path: Path, check_interval: float = 2.0
    ):
        """Initialize the space monitor.

        Args:
            required_space_mb: Minimum required disk space in megabytes.
            path: Path to monitor for disk space (will check filesystem containing this path).
            check_interval: How often to check disk space in seconds. Defaults to 2.0.
        """
        self.required_space_mb = required_space_mb
        self.path = path
        self.check_interval = check_interval
        self.stop_operation = threading.Event()
        self.thread: threading.Thread = None

    def start(self) -> None:
        """Start monitoring disk space in background daemon thread."""
        if self.thread is not None:
            return  # Already started

        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
        logger.debug(
            f"Started space monitor for {self.path} (required: {self.required_space_mb:.1f}MB)"
        )

    def _monitor(self) -> None:
        """Continuously monitor disk space and signal when insufficient."""
        while not self.stop_operation.is_set():
            try:
                available_mb = get_available_disk_space_mb(self.path)
                logger.debug(
                    f"[SpaceMonitor] Available space: {available_mb:.1f}MB (required: {self.required_space_mb:.1f}MB)"
                )

                if available_mb < self.required_space_mb:
                    logger.error(
                        f"CRITICAL: Space ({available_mb:.1f}MB) below required {self.required_space_mb:.1f}MB. Signaling stop!"
                    )
                    self.stop_operation.set()
                    break

            except Exception as e:
                logger.warning(f"Space monitor error: {e}")

            time.sleep(self.check_interval)

    def should_stop(self) -> bool:
        """Check if operations should stop due to insufficient disk space.

        Returns:
            bool: True if insufficient disk space was detected, False otherwise.
        """
        return self.stop_operation.is_set()

    def stop(self) -> None:
        """Stop the background monitoring thread."""
        self.stop_operation.set()
        if self.thread is not None:
            logger.debug("Stopped space monitor")


def cleanup_process(
    process: Process, operation_name: str, timeout: float = 5.0
) -> None:
    """Clean up a process with graceful termination and force kill fallback.

    This helper function implements the standard pattern for cleaning up
    multiprocessing.Process instances with proper timeout handling.

    Args:
        process: The process to clean up.
        operation_name: Name of the operation for logging.
        timeout: How long to wait for graceful termination before force kill.
    """
    if process.is_alive():
        process.terminate()
        process.join(timeout=timeout)
        if process.is_alive():
            logger.warning(f"Force killing {operation_name} process")
            process.kill()
            process.join()


def run_monitored_process(
    worker_func,
    args,
    space_monitor: CacheSpaceMonitor,
    operation_name: str,
    cleanup_func=None,
) -> None:
    """Run a worker process with space monitoring and automatic termination.

    This function starts a worker process and monitors it alongside the space monitor.
    If insufficient disk space is detected, the worker process is terminated and
    cleanup is performed.

    Args:
        worker_func: The worker function to run in a separate process.
        args: Arguments to pass to the worker function.
        space_monitor: CacheSpaceMonitor instance to check for space issues.
        operation_name: Name of the operation for logging.
        cleanup_func: Optional function to call for cleanup if operation is interrupted.

    Raises:
        CacheOperationInterrupted: If the operation was interrupted due to insufficient disk space.
        Exception: If the worker process failed for other reasons.
    """
    result_queue = Queue()
    stop_event = multiprocessing.Event()

    # Add result_queue and stop_event to worker args
    worker_args = args + (result_queue, stop_event)

    # Start the worker process
    process = Process(target=worker_func, args=worker_args)
    process.start()

    try:
        # Monitor the process
        while process.is_alive():
            if space_monitor.should_stop():
                logger.warning(f"Low disk space detected, cancelling {operation_name}")
                stop_event.set()
                cleanup_process(process, operation_name)

                # Run cleanup if provided
                if cleanup_func:
                    cleanup_func()

                raise CacheOperationInterrupted(
                    f"{operation_name} was cancelled due to insufficient disk space"
                )

            time.sleep(SPACE_MONITOR_CHECK_INTERVAL_SECONDS)

        # Process finished, get the result
        process.join()

        if not result_queue.empty():
            status, error_msg = result_queue.get()
            if status == WorkerStatus.ERROR.value:
                logger.error(f"{operation_name} worker failed: {error_msg}")
                raise Exception(error_msg)
            elif status == WorkerStatus.CANCELLED.value:
                if cleanup_func:
                    cleanup_func()
                raise CacheOperationInterrupted(error_msg)
            # status == WorkerStatus.SUCCESS.value - continue normally

        logger.debug(f"{operation_name} completed successfully")

    except Exception as e:
        # Ensure process is cleaned up
        cleanup_process(process, operation_name)

        if not isinstance(e, CacheOperationInterrupted):
            logger.error(f"{operation_name} failed: {e}")
        raise
