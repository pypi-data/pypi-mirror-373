"""PyTorch compilation cache management using the generic transfer system.

This module provides torch-specific cache operations (save/load) that use the
generic transfer infrastructure from core.py. It handles the torch-specific
logic like compression, extraction, and file naming while delegating the
robust transfer operations to the core transfer function.
"""

import os
import logging
import tempfile
import shutil
from pathlib import Path

from .core import transfer
from .environment import get_cache_filename
from .archive import create_archive, extract_archive
from .utils import (
    timed_fn,
    critical_section_b10fs_file_lock,
    safe_execute,
    temp_file_cleanup,
    safe_unlink,
)
from .space_monitor import worker_process
from .constants import (
    TORCH_CACHE_DIR,
    B10FS_CACHE_DIR,
    LOCAL_WORK_DIR,
    MAX_CACHE_SIZE_MB,
    CACHE_FILE_EXTENSION,
    CACHE_LATEST_SUFFIX,
    CACHE_INCOMPLETE_SUFFIX,
    LoadStatus,
    SaveStatus,
    TransferStatus,
)

logger = logging.getLogger(__name__)


def torch_cache_save_callback(
    source_dir: Path, dest_file: Path, max_size_mb: int = None, *args, **kwargs
) -> None:
    """Callback function for saving torch cache: compress then copy to b10fs.

    This function handles the torch-specific save logic:
    1. Compress the torch cache directory to a temporary archive
    2. Copy the archive to b10fs using atomic operations (temp file + rename)

    Args:
        source_dir: Path to the torch cache directory to compress
        dest_file: Path to the final cache file in b10fs
        max_size_mb: Maximum allowed archive size in megabytes (can be passed as kwarg)
        *args: Additional arguments passed by the transfer system (ignored)
        **kwargs: Additional keyword arguments passed by the transfer system (may contain max_size_mb)
    """
    # Handle max_size_mb from kwargs if not provided as positional argument
    if max_size_mb is None:
        max_size_mb = kwargs.get("max_size_mb", MAX_CACHE_SIZE_MB)

    work_dir = Path(LOCAL_WORK_DIR)

    # Create temporary archive in local work directory
    with tempfile.NamedTemporaryFile(
        suffix=CACHE_FILE_EXTENSION, dir=work_dir, delete=False
    ) as f:
        temp_archive = Path(f.name)

    logger.debug(f"Created temporary archive: {temp_archive}")

    try:
        with temp_file_cleanup(temp_archive):
            # Step 1: Compress torch cache to temporary archive
            logger.info(f"Compressing torch cache: {source_dir} -> {temp_archive}")
            create_archive(source_dir, temp_archive, max_size_mb)

            # Step 2: Atomic copy to b10fs (temp file + rename)
            b10fs_dir = dest_file.parent
            b10fs_dir.mkdir(parents=True, exist_ok=True)

            # Use incomplete suffix for atomic operation
            cache_filename = get_cache_filename()
            temp_dest = (
                b10fs_dir
                / f"{cache_filename}{CACHE_INCOMPLETE_SUFFIX}{CACHE_FILE_EXTENSION}"
            )

            logger.info(f"Copying to b10fs: {temp_archive} -> {temp_dest}")

            @critical_section_b10fs_file_lock("copy_in")
            def _atomic_copy_to_b10fs():
                shutil.copy2(temp_archive, temp_dest)
                # Atomic rename to final destination
                logger.info(f"Atomic rename: {temp_dest} -> {dest_file}")
                temp_dest.rename(dest_file)

            _atomic_copy_to_b10fs()

    except Exception as e:
        # Cleanup any partial b10fs files
        temp_dest_pattern = dest_file.parent / f"*{CACHE_INCOMPLETE_SUFFIX}*"
        for temp_file in dest_file.parent.glob(f"*{CACHE_INCOMPLETE_SUFFIX}*"):
            safe_unlink(temp_file, f"Failed to cleanup incomplete file {temp_file}")
        raise


def torch_cache_load_callback(
    source_file: Path, dest_dir: Path, *args, **kwargs
) -> None:
    """Callback function for loading torch cache: copy from b10fs then extract.

    This function handles the torch-specific load logic:
    1. Copy the cache file from b10fs to a temporary local file
    2. Extract the archive to the torch cache directory

    Args:
        source_file: Path to the cache file in b10fs
        dest_dir: Path to the torch cache directory where files will be extracted
        *args: Additional arguments passed by the transfer system (ignored)
        **kwargs: Additional keyword arguments passed by the transfer system (ignored)
    """
    work_dir = Path(LOCAL_WORK_DIR)

    # Create temporary file for local copy
    with tempfile.NamedTemporaryFile(
        suffix=CACHE_FILE_EXTENSION, dir=work_dir, delete=False
    ) as f:
        temp_archive = Path(f.name)

    logger.debug(f"Created temporary file for cache copy: {temp_archive}")

    try:
        with temp_file_cleanup(temp_archive):
            # Step 1: Copy from b10fs to local temp file
            @critical_section_b10fs_file_lock("copy_out")
            def _copy_from_b10fs():
                logger.info(f"Copying from b10fs: {source_file} -> {temp_archive}")
                if not source_file.exists():
                    raise FileNotFoundError(f"Cache file not found: {source_file}")
                shutil.copy2(source_file, temp_archive)

            _copy_from_b10fs()

            # Step 2: Extract archive to torch cache directory
            logger.info(f"Extracting archive: {temp_archive} -> {dest_dir}")
            extract_archive(temp_archive, dest_dir)

    except Exception as e:
        # Cleanup partial torch directory on failure
        if dest_dir.exists():
            try:
                shutil.rmtree(dest_dir)
                logger.debug(f"Cleaned up partial torch directory: {dest_dir}")
            except Exception as cleanup_error:
                logger.error(
                    f"Failed to cleanup torch directory {dest_dir}: {cleanup_error}"
                )
        raise


@timed_fn(logger=logger, name="Loading compile cache")
@safe_execute("Load failed", LoadStatus.ERROR)
def load_compile_cache() -> LoadStatus:
    """Load PyTorch compilation cache from b10fs to local torch cache directory.

    This function loads cached PyTorch compilation artifacts from the b10fs shared
    filesystem to the local torch cache directory using the generic transfer system.
    It validates cache availability, checks for existing cache, and extracts the
    archive if needed.

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
    b10fs_dir = Path(B10FS_CACHE_DIR)
    torch_dir = Path(TORCH_CACHE_DIR)

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

    # Use generic transfer system with torch-specific callback
    result = transfer(
        source=cache_file,
        dest=torch_dir,
        callback=torch_cache_load_callback,
        monitor_local=True,
        monitor_b10fs=False,  # No need to monitor b10fs for read operations
    )

    # Convert TransferStatus to LoadStatus
    if result == TransferStatus.SUCCESS:
        logger.info("Cache load complete")
        return LoadStatus.SUCCESS
    else:
        logger.error(f"Cache load failed with status: {result}")
        return LoadStatus.ERROR


@timed_fn(logger=logger, name="Saving compile cache")
@safe_execute("Save failed", SaveStatus.ERROR)
def save_compile_cache() -> SaveStatus:
    """Save local PyTorch compilation cache to b10fs using atomic journal pattern.

    This function creates an archive of the local torch cache directory and
    atomically saves it to b10fs using the generic transfer system. It validates
    cache availability, checks if cache already exists (early exit), and performs
    compression and copy operations with proper space monitoring.

    Returns:
        SaveStatus:
              SaveStatus.SUCCESS if cache was successfully saved
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
    b10fs_dir = Path(B10FS_CACHE_DIR)
    torch_dir = Path(TORCH_CACHE_DIR)

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

    # Use generic transfer system with torch-specific callback
    result = transfer(
        source=torch_dir,
        dest=final_file,
        callback=torch_cache_save_callback,
        max_size_mb=MAX_CACHE_SIZE_MB,
        monitor_local=True,
        monitor_b10fs=True,
    )

    # Convert TransferStatus to SaveStatus
    if result == TransferStatus.SUCCESS:
        logger.info("Cache save complete")
        return SaveStatus.SUCCESS
    elif result == TransferStatus.INTERRUPTED:
        logger.warning("Cache save interrupted due to insufficient disk space")
        return SaveStatus.ERROR
    else:
        logger.error(f"Cache save failed with status: {result}")
        return SaveStatus.ERROR


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


# Worker functions for backward compatibility with existing monitored process system
# These are used if someone wants to use the old worker-based approach


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

    extract_archive(archive_path, dest_dir)


def _cleanup_torch_dir(torch_dir: Path) -> None:
    """Helper function to safely cleanup torch directory during interrupted extraction."""
    try:
        if torch_dir.exists():
            shutil.rmtree(torch_dir)
            logger.debug(f"Cleaned up torch directory: {torch_dir}")
    except Exception as e:
        logger.error(f"Failed to cleanup torch directory {torch_dir}: {e}")
