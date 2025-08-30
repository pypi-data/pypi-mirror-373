import logging
from pathlib import Path

from .cleanup import cooperative_cleanup_b10fs
from .utils import (
    timed_fn,
    safe_execute,
    cache_operation,
)
from .space_monitor import (
    check_sufficient_disk_space,
    CacheSpaceMonitor,
    CacheOperationInterrupted,
    run_monitored_process,
)
from .constants import (
    B10FS_CACHE_DIR,
    LOCAL_WORK_DIR,
    REQUIRED_B10FS_SPACE_MB,
    MIN_LOCAL_SPACE_MB,
    TransferStatus,
)

logger = logging.getLogger(__name__)


@timed_fn(logger=logger, name="Generic transfer operation")
@safe_execute("Transfer failed", TransferStatus.ERROR)
def transfer(
    source: Path,
    dest: Path,
    callback: callable,
    *callback_args,
    monitor_local: bool = True,
    monitor_b10fs: bool = True,
    **callback_kwargs,
) -> TransferStatus:
    """Generic transfer function with space monitoring and atomic operations.

    The actual transfer logic is provided via callback.

    The function handles:
    - Cooperative cleanup of stale shared resources
    - Space monitoring during operations (optional for local and b10fs)
    - Atomic operations using temp files and rename
    - Automatic cleanup on interruption or failure
    - Lock management for b10fs operations

    Args:
        source: Source path for the transfer operation
        dest: Destination path for the transfer operation
        callback: Function to perform the actual transfer work
        *callback_args: Positional arguments to pass to callback
        monitor_local: Whether to monitor local disk space (default: True)
        monitor_b10fs: Whether to monitor b10fs disk space (default: True)
        **callback_kwargs: Keyword arguments to pass to callback

    Returns:
        TransferStatus:
              TransferStatus.SUCCESS if transfer completed successfully
              TransferStatus.ERROR if transfer failed
              TransferStatus.INTERRUPTED if transfer was interrupted due to insufficient disk space

    Raises:
        CacheValidationError: If b10fs is not enabled (caught and returns TransferStatus.ERROR).
        CacheOperationInterrupted: If operations interrupted due to insufficient
                                  disk space (caught and returns TransferStatus.INTERRUPTED).
        Exception: Any other errors during transfer (caught and returns TransferStatus.ERROR).
    """
    with cache_operation("Transfer"):
        # Cooperative cleanup of stale shared resources
        cooperative_cleanup_b10fs()

        b10fs_dir = Path(B10FS_CACHE_DIR)
        work_dir = Path(LOCAL_WORK_DIR)

        # Determine which paths to monitor based on source/dest
        local_path = None
        b10fs_path = None

        if str(source).startswith(str(b10fs_dir)) or str(dest).startswith(
            str(b10fs_dir)
        ):
            b10fs_path = b10fs_dir

        if (
            str(source).startswith(str(work_dir))
            or str(dest).startswith(str(work_dir))
            or not str(source).startswith(str(b10fs_dir))
            or not str(dest).startswith(str(b10fs_dir))
        ):
            local_path = work_dir

        # Initial disk space checks
        if monitor_local and local_path:
            check_sufficient_disk_space(
                local_path, MIN_LOCAL_SPACE_MB, "local transfer operations"
            )
            logger.debug(
                f"Initial local space check passed: {MIN_LOCAL_SPACE_MB:.1f}MB required"
            )

        if monitor_b10fs and b10fs_path:
            check_sufficient_disk_space(
                b10fs_path, REQUIRED_B10FS_SPACE_MB, "b10fs transfer operations"
            )
            logger.debug(
                f"Initial b10fs space check passed: {REQUIRED_B10FS_SPACE_MB:.1f}MB required"
            )

        # Determine primary space monitor (prioritize b10fs if both are monitored)
        primary_monitor = None
        if monitor_b10fs and b10fs_path:
            primary_monitor = CacheSpaceMonitor(REQUIRED_B10FS_SPACE_MB, b10fs_path)
        elif monitor_local and local_path:
            primary_monitor = CacheSpaceMonitor(MIN_LOCAL_SPACE_MB, local_path)

        if primary_monitor is None:
            # No monitoring requested, execute callback directly
            logger.info(f"Starting transfer (no monitoring): {source} -> {dest}")
            callback(source, dest, *callback_args, **callback_kwargs)
            logger.info("Transfer complete")
            return TransferStatus.SUCCESS

        # Start the primary space monitor
        primary_monitor.start()

        try:
            # Execute the callback using monitored process for continuous space monitoring
            logger.info(f"Starting monitored transfer: {source} -> {dest}")

            # Try direct callback with run_monitored_process first
            try:
                run_monitored_process(
                    callback,
                    (source, dest, *callback_args),
                    primary_monitor,
                    "transfer callback",
                )
                logger.info("Transfer complete (monitored)")
                return TransferStatus.SUCCESS

            except (TypeError, AttributeError, ImportError, OSError) as e:
                # Callback not pickleable or other serialization issue
                logger.warning(
                    f"Callback not suitable for process isolation, running without monitoring: {e}"
                )

                # Fallback to direct execution without process isolation
                callback(source, dest, *callback_args, **callback_kwargs)
                logger.info("Transfer complete (unmonitored)")
                return TransferStatus.SUCCESS

        except CacheOperationInterrupted as e:
            logger.warning(f"Transfer interrupted: {e}")
            return TransferStatus.INTERRUPTED

        finally:
            # Stop space monitor
            primary_monitor.stop()
