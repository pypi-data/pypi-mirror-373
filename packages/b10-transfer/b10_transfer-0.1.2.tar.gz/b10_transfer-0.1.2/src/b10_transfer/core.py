import os
import logging
import tempfile
import shutil
from pathlib import Path

import time

from .environment import get_cache_filename
from .cleanup import cooperative_cleanup_b10fs
from .utils import (
    timed_fn,
    critical_section_b10fs_file_lock,
    safe_execute,
    temp_file_cleanup,
    cache_operation,
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
    TORCH_CACHE_DIR,
    B10FS_CACHE_DIR,
    LOCAL_WORK_DIR,
    MAX_CACHE_SIZE_MB,
    REQUIRED_B10FS_SPACE_MB,
    MIN_LOCAL_SPACE_MB,
    CACHE_FILE_EXTENSION,
    CACHE_LATEST_SUFFIX,
    CACHE_INCOMPLETE_SUFFIX,
    LoadStatus,
    SaveStatus,
)

logger = logging.getLogger(__name__)


@timed_fn(logger=logger, name="Loading compile cache")
@safe_execute("Load failed", False)
def load_compile_cache() -> LoadStatus:
    """Load PyTorch compilation cache from b10fs to local torch cache directory.

    This function implements a lock-free pattern to safely load cached PyTorch
    compilation artifacts from the b10fs shared filesystem to the local torch
    cache directory. It validates b10fs availability, checks for existing cache,
    and extracts the archive if needed.

    The function monitors local disk space during both the copy from b10fs and
    extraction phases, interrupting operations if space falls below MIN_LOCAL_SPACE_MB.

    Returns:
        LoadStatus:
              LoadStatus.SUCCESS if cache was successfully loaded
              LoadStatus.SKIPPED if already exists
              LoadStatus.ERROR if b10fs is unavailable, local disk space is insufficient, or loading failed.
              LoadStatus.DOES_NOT_EXIST if no cache file was found.

    Raises:
        CacheValidationError: If b10fs is not enabled (caught and returns LoadStatus.ERROR).
        CacheOperationInterrupted: If operations interrupted due to insufficient
                                  local disk space (caught and returns LoadStatus.ERROR).
        Exception: Any other errors during loading (caught and returns LoadStatus.ERROR).
    """
    with cache_operation("Load"):
        # Cooperative cleanup of stale shared resources
        cooperative_cleanup_b10fs()

        b10fs_dir = Path(B10FS_CACHE_DIR)
        torch_dir = Path(TORCH_CACHE_DIR)
        work_dir = Path(LOCAL_WORK_DIR)

        cache_filename = get_cache_filename()
        cache_file = (
            b10fs_dir / f"{cache_filename}{CACHE_LATEST_SUFFIX}{CACHE_FILE_EXTENSION}"
        )
        logger.debug(f"Looking for cache file: {cache_file}")

        if not cache_file.exists():
            logger.info("No cache file found in b10fs")
            return LoadStatus.DOES_NOT_EXIST

        # Skip if already loaded
        if torch_dir.exists() and any(torch_dir.iterdir()):
            logger.info("Torch cache already loaded, skipping extraction")
            return LoadStatus.SKIPPED

        # Initial disk space check for local operations
        check_sufficient_disk_space(
            work_dir, MIN_LOCAL_SPACE_MB, "cache load operations"
        )
        logger.debug(
            f"Initial space check passed: {MIN_LOCAL_SPACE_MB:.1f}MB required on local machine"
        )

        # Start background space monitoring for local disk
        space_monitor = CacheSpaceMonitor(MIN_LOCAL_SPACE_MB, work_dir)
        space_monitor.start()

        # Create temp local copy
        with tempfile.NamedTemporaryFile(
            suffix=CACHE_FILE_EXTENSION, dir=work_dir, delete=False
        ) as f:
            temp_path = Path(f.name)
        logger.debug(f"Created temporary file for cache: {temp_path}")

        try:
            with temp_file_cleanup(temp_path):
                # Phase 1: Copy from b10fs to local temp file in separate process
                @critical_section_b10fs_file_lock("copy_out")
                def _monitored_copy_from_b10fs():
                    logger.info(
                        f"Starting copy from b10fs: {cache_file} -> {temp_path}"
                    )
                    run_monitored_process(
                        _cache_copy_from_b10fs_worker,
                        (str(cache_file), str(temp_path)),
                        space_monitor,
                        "b10fs to local copy",
                    )

                _monitored_copy_from_b10fs()

                # Phase 2: Extract archive in separate process
                logger.info(f"Starting extraction: {temp_path} -> {torch_dir}")
                run_monitored_process(
                    _cache_extract_worker,
                    (str(temp_path), str(torch_dir)),
                    space_monitor,
                    "archive extraction",
                    cleanup_func=lambda: _cleanup_torch_dir(torch_dir),
                )

            logger.info("Cache load complete")
            return LoadStatus.SUCCESS

        except CacheOperationInterrupted as e:
            logger.warning(f"Cache load interrupted: {e}")
            return LoadStatus.ERROR

        finally:
            space_monitor.stop()


"""
FIXME(SRAY):
What about the case in @b10-transfer/ where a single pod finishes an inference request,
and then the client calls save_compile_cache. And while we are creating the local archive,
another inference call on the same pod is kicked off, which then modifies the torch cache.
How would this be handled? Maybe just accept that the cache will be recompiled/overwritten?
Otherwise you'd need application level coordination to ensure that the cache is not modified
while we are creating the archive, but this doesn't really seem like a good idea in terms of adoption.

FIXME(SR):
More things to consider:
- [possible] What if b10fs dies *during* an op? right now we check for b10fs availability in the beginning of the op... Add some constants instead of just False for load().
- [possible, and really bad if it happens] potential memory exhaustion during compression if the cache is super super large. very very edge case. higher compression levels also have high memory usage.
"""


@timed_fn(logger=logger, name="Saving compile cache")
@safe_execute("Save failed", False)
def save_compile_cache() -> SaveStatus:
    """Save local PyTorch compilation cache to b10fs using atomic journal pattern.

    This function creates an archive of the local torch cache directory and
    atomically saves it to b10fs using a journal pattern (write to temp file,
    then rename). This ensures concurrent saves don't corrupt each other.

    The function validates b10fs availability, checks if cache already exists
    (early exit), performs initial space checks using pre-calculated requirements
    for concurrent saves, starts background space monitoring, then runs compression
    and copy operations in separate worker processes that can be terminated if disk
    space becomes insufficient, finally performing an atomic rename to the final cache file.

    Returns:
        SaveStatus:
              SaveStatus.SUCCESS if cache was successfully saved or already exists
              SaveStatus.ERROR if b10fs is unavailable, insufficient disk space caused interruption,
                no cache exists to save, or saving failed.
              SaveStatus.SKIPPED if no cache exists to save or cache already exists in b10fs

    Raises:
        CacheValidationError: If b10fs is not enabled (caught and returns SaveStatus.ERROR).
        CacheOperationInterrupted: If operations interrupted due to insufficient
                                  disk space (caught and returns SaveStatus.ERROR).
        ArchiveError: If archive creation fails (caught and returns SaveStatus.ERROR).
        Exception: Any other errors during saving (caught and returns SaveStatus.ERROR).
    """
    with cache_operation("Save"):
        # Cooperative cleanup of stale shared resources
        cooperative_cleanup_b10fs()

        b10fs_dir = Path(B10FS_CACHE_DIR)
        torch_dir = Path(TORCH_CACHE_DIR)
        work_dir = Path(LOCAL_WORK_DIR)

        # Check if anything to save
        if not torch_dir.exists() or not any(torch_dir.iterdir()):
            logger.info("No torch cache to save")
            return SaveStatus.SKIPPED

        cache_filename = get_cache_filename()
        final_file = (
            b10fs_dir / f"{cache_filename}{CACHE_LATEST_SUFFIX}{CACHE_FILE_EXTENSION}"
        )

        # Check for existing cache first (early exit)
        if final_file.exists():
            logger.info("Cache already exists in b10fs, skipping save")
            return SaveStatus.SKIPPED

        # Initial disk space checks using calculated space requirements
        check_sufficient_disk_space(
            work_dir, MAX_CACHE_SIZE_MB, "local temp file creation"
        )
        check_sufficient_disk_space(
            b10fs_dir, REQUIRED_B10FS_SPACE_MB, "cache save to b10fs"
        )
        logger.debug(
            f"Initial space checks passed: {MAX_CACHE_SIZE_MB:.1f}MB local, {REQUIRED_B10FS_SPACE_MB:.1f}MB b10fs"
        )

        temp_file = (
            b10fs_dir
            / f"{cache_filename}{CACHE_INCOMPLETE_SUFFIX}{CACHE_FILE_EXTENSION}"
        )

        # Start background space monitoring
        space_monitor = CacheSpaceMonitor(REQUIRED_B10FS_SPACE_MB, b10fs_dir)
        space_monitor.start()

        with tempfile.NamedTemporaryFile(
            suffix=CACHE_FILE_EXTENSION, dir=work_dir, delete=False
        ) as f:
            local_temp = Path(f.name)
        logger.debug(f"Created local temp file for archive: {local_temp}")

        try:
            with temp_file_cleanup(local_temp):
                # Phase 1: Compression in separate process
                logger.info(f"Starting compression: {torch_dir} -> {local_temp}")
                run_monitored_process(
                    _cache_compression_worker,
                    (str(torch_dir), str(local_temp), MAX_CACHE_SIZE_MB),
                    space_monitor,
                    "compression",
                )

                b10fs_dir.mkdir(parents=True, exist_ok=True)

                # Phase 2: Copy to b10fs in separate process
                @critical_section_b10fs_file_lock("copy_in")
                def _monitored_copy_to_b10fs():
                    logger.info(f"Starting copy to b10fs: {local_temp} -> {temp_file}")
                    run_monitored_process(
                        _cache_copy_worker,
                        (str(local_temp), str(temp_file)),
                        space_monitor,
                        "b10fs copy",
                        cleanup_func=lambda: safe_unlink(
                            temp_file, f"Failed to cleanup interrupted copy {temp_file}"
                        ),
                    )

                _monitored_copy_to_b10fs()

                # Phase 3: Atomic rename (fast, don't interrupt)
                logger.info(
                    f"Renaming temp file to final cache file: {temp_file} -> {final_file}"
                )
                temp_file.rename(final_file)

            logger.info("Cache save complete")
            return SaveStatus.SUCCESS

        except CacheOperationInterrupted as e:
            logger.warning(f"Cache save interrupted: {e}")
            return SaveStatus.ERROR

        finally:
            space_monitor.stop()


@safe_execute("Clear failed", False)
def clear_local_cache() -> bool:
    """Clear the local PyTorch compilation cache directory.

    This function removes the entire local torch cache directory and all its
    contents. This is useful for cleaning up disk space or forcing recompilation.

    Returns:
        bool: True if cache was successfully cleared or didn't exist, False if
              clearing failed due to permissions or other filesystem errors.

    Raises:
        Exception: Any errors during directory removal (caught and returns False).
    """
    torch_dir = Path(TORCH_CACHE_DIR)
    if not torch_dir.exists():
        return True
    shutil.rmtree(torch_dir)
    return True


@worker_process("Compression was cancelled before starting")
def _cache_compression_worker(
    torch_dir_str: str, local_temp_str: str, max_size_mb: int
) -> None:
    """Worker process that handles cache compression.

    This function runs in a separate process to compress the torch cache directory
    into an archive. It can be terminated externally if disk space becomes insufficient.

    Args:
        torch_dir_str: String path to the torch cache directory to compress.
        local_temp_str: String path where the compressed archive will be created.
        max_size_mb: Maximum allowed archive size in megabytes.
    """
    torch_dir = Path(torch_dir_str)
    local_temp = Path(local_temp_str)

    # Import here to avoid issues with multiprocessing
    from .archive import create_archive

    create_archive(torch_dir, local_temp, max_size_mb)


@worker_process("Copy was cancelled before starting")
def _cache_copy_worker(source_path_str: str, dest_path_str: str) -> None:
    """Worker process that handles file copy to b10fs.

    This function runs in a separate process to copy the compressed cache file
    to the b10fs filesystem. It can be terminated externally if disk space becomes insufficient.

    Args:
        source_path_str: String path to the source file to copy.
        dest_path_str: String path where the file will be copied.
    """
    source_path = Path(source_path_str)
    dest_path = Path(dest_path_str)

    shutil.copy2(source_path, dest_path)


@worker_process("Copy from b10fs was cancelled before starting")
def _cache_copy_from_b10fs_worker(source_path_str: str, dest_path_str: str) -> None:
    """Worker process that handles file copy from b10fs to local machine.

    This function runs in a separate process to copy the cache file from b10fs
    to the local filesystem. It can be terminated externally if local disk space becomes insufficient.

    Args:
        source_path_str: String path to the source file in b10fs to copy.
        dest_path_str: String path where the file will be copied locally.
    """
    source_path = Path(source_path_str)
    dest_path = Path(dest_path_str)

    shutil.copy2(source_path, dest_path)


def _cleanup_torch_dir(torch_dir: Path) -> None:
    """Helper function to safely cleanup torch directory during interrupted extraction."""
    try:
        if torch_dir.exists():
            shutil.rmtree(torch_dir)
            logger.debug(f"Cleaned up torch directory: {torch_dir}")
    except Exception as e:
        logger.error(f"Failed to cleanup torch directory {torch_dir}: {e}")


@worker_process("Extraction was cancelled before starting")
def _cache_extract_worker(archive_path_str: str, dest_dir_str: str) -> None:
    """Worker process that handles archive extraction.

    This function runs in a separate process to extract the cache archive to
    the torch cache directory. It can be terminated externally if local disk space becomes insufficient.

    Args:
        archive_path_str: String path to the archive file to extract.
        dest_dir_str: String path to the directory where archive will be extracted.
    """
    archive_path = Path(archive_path_str)
    dest_dir = Path(dest_dir_str)

    # Import here to avoid issues with multiprocessing
    from .archive import extract_archive

    extract_archive(archive_path, dest_dir)
