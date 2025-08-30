"""Torch-specific async cache operations using the generic async transfer system."""

from pathlib import Path
from typing import Optional, Callable

from .async_transfers import start_transfer_async
from .torch_cache import torch_cache_load_callback, torch_cache_save_callback
from .environment import get_cache_filename
from .constants import (
    TORCH_CACHE_DIR,
    B10FS_CACHE_DIR,
    MAX_CACHE_SIZE_MB,
    CACHE_FILE_EXTENSION,
    CACHE_LATEST_SUFFIX,
)


def load_compile_cache_async(
    progress_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """Start async PyTorch compilation cache load operation."""
    b10fs_dir = Path(B10FS_CACHE_DIR)
    torch_dir = Path(TORCH_CACHE_DIR)

    cache_filename = get_cache_filename()
    cache_file = (
        b10fs_dir / f"{cache_filename}{CACHE_LATEST_SUFFIX}{CACHE_FILE_EXTENSION}"
    )

    return start_transfer_async(
        source=cache_file,
        dest=torch_dir,
        callback=torch_cache_load_callback,
        operation_name="torch_cache_load",
        progress_callback=progress_callback,
        monitor_local=True,
        monitor_b10fs=False,  # No need to monitor b10fs for read operations
    )


def save_compile_cache_async(
    progress_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """Start async PyTorch compilation cache save operation."""
    b10fs_dir = Path(B10FS_CACHE_DIR)
    torch_dir = Path(TORCH_CACHE_DIR)

    cache_filename = get_cache_filename()
    final_file = (
        b10fs_dir / f"{cache_filename}{CACHE_LATEST_SUFFIX}{CACHE_FILE_EXTENSION}"
    )

    return start_transfer_async(
        source=torch_dir,
        dest=final_file,
        callback=torch_cache_save_callback,
        operation_name="torch_cache_save",
        progress_callback=progress_callback,
        monitor_local=True,
        monitor_b10fs=True,
        max_size_mb=MAX_CACHE_SIZE_MB,
    )
