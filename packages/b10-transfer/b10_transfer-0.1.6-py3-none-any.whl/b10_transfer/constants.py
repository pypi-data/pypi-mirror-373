"""Configuration constants for b10-transfer.

This module defines configuration constants for the PyTorch compilation cache system.
Some values can be overridden by environment variables, but security caps are enforced
to prevent malicious or accidental misuse in production environments.
"""

import os
from enum import Enum, auto

# Import helper functions from utils to avoid duplication
from .utils import (
    get_current_username,
    validate_path_security,
    validate_boolean_env,
    apply_cap,
)

# Cache directories with security validation

# Validate TORCH_CACHE_DIR - allow /tmp and /cache paths
# TORCHINDUCTOR_CACHE_DIR is what torch uses by default. If it is not set, we use a different value.
_torch_cache_dir = os.getenv(
    "TORCHINDUCTOR_CACHE_DIR", f"/tmp/torchinductor_{get_current_username()}"
)
TORCH_CACHE_DIR = validate_path_security(
    _torch_cache_dir, ["/tmp/", "/cache/"], "TORCHINDUCTOR_CACHE_DIR"
)

# B10FS cache directory validation
_REQUIRED_TORCH_CACHE_DIR_PREFIX = "/cache/model"
_b10fs_cache_dir = os.getenv(
    "B10FS_CACHE_DIR", f"{_REQUIRED_TORCH_CACHE_DIR_PREFIX}/compile_cache"
)
B10FS_CACHE_DIR = validate_path_security(
    _b10fs_cache_dir, [_REQUIRED_TORCH_CACHE_DIR_PREFIX], "B10FS_CACHE_DIR"
)

# Validate LOCAL_WORK_DIR - allow /app, /tmp, and /cache paths
_local_work_dir = os.getenv("LOCAL_WORK_DIR", "/app")
LOCAL_WORK_DIR = validate_path_security(
    _local_work_dir, ["/app/", "/tmp/", "/cache/"], "LOCAL_WORK_DIR"
)

# Security caps to prevent resource exhaustion
_MAX_CACHE_SIZE_CAP_MB = 1 * 1024  # 1GB hard limit per cache archive
_MAX_CONCURRENT_SAVES_CAP = 100  # Maximum concurrent save operations (only used as estimate for b10fs space requirements/thresholding)


# Cache limits (capped for security)
_user_max_cache_size = int(os.getenv("MAX_CACHE_SIZE_MB", "1024"))
MAX_CACHE_SIZE_MB = apply_cap(
    _user_max_cache_size, _MAX_CACHE_SIZE_CAP_MB, "MAX_CACHE_SIZE_MB"
)

_user_max_concurrent_saves = int(os.getenv("MAX_CONCURRENT_SAVES", "50"))
MAX_CONCURRENT_SAVES = apply_cap(
    _user_max_concurrent_saves, _MAX_CONCURRENT_SAVES_CAP, "MAX_CONCURRENT_SAVES"
)

# Space requirements
MIN_LOCAL_SPACE_MB = 50 * 1024  # 50GB minimum space on local machine
REQUIRED_B10FS_SPACE_MB = max(MAX_CONCURRENT_SAVES * MAX_CACHE_SIZE_MB, 100_000)

# B10FS configuration
# The default is "0" (disabled) to prevent accidental enabling.
# But this does limit the ability to enable b10fs for debugging purposes.
# Probably should use B10FS_ENABLED instead for that.
_baseten_fs_enabled = os.getenv("BASETEN_FS_ENABLED", "0")
BASETEN_FS_ENABLED = validate_boolean_env(_baseten_fs_enabled, "BASETEN_FS_ENABLED")

# File naming patterns
CACHE_FILE_EXTENSION = ".tar.gz"
CACHE_LATEST_SUFFIX = ".latest"
CACHE_INCOMPLETE_SUFFIX = ".incomplete"
CACHE_PREFIX = "cache_"


# Space monitoring settings
SPACE_MONITOR_CHECK_INTERVAL_SECONDS = (
    0.5  # How often to check disk space during operations
)

# Cooperative cleanup settings
# Cache operations (load/save) should complete within ~15 seconds under normal conditions
_LOCK_TIMEOUT_CAP_SECONDS = 3600  # 1 hour hard limit
_INCOMPLETE_TIMEOUT_CAP_SECONDS = 7200  # 2 hours hard limit

# Lock file cleanup timeout (default: 2x expected operation time)
_user_lock_timeout = int(
    os.getenv("CLEANUP_LOCK_TIMEOUT_SECONDS", "30")
)  # 30 seconds default
CLEANUP_LOCK_TIMEOUT_SECONDS = apply_cap(
    _user_lock_timeout, _LOCK_TIMEOUT_CAP_SECONDS, "CLEANUP_LOCK_TIMEOUT_SECONDS"
)

# Incomplete file cleanup timeout (default: 3x expected operation time)
_user_incomplete_timeout = int(
    os.getenv("CLEANUP_INCOMPLETE_TIMEOUT_SECONDS", "60")
)  # 1 minute default
CLEANUP_INCOMPLETE_TIMEOUT_SECONDS = apply_cap(
    _user_incomplete_timeout,
    _INCOMPLETE_TIMEOUT_CAP_SECONDS,
    "CLEANUP_INCOMPLETE_TIMEOUT_SECONDS",
)


# Worker process result status enum
class WorkerStatus(Enum):
    """Status values for worker process results."""

    SUCCESS = auto()
    ERROR = auto()
    CANCELLED = auto()


class OperationStatus(Enum):
    """Status values for all b10-transfer operations (load, save, transfer)."""

    SUCCESS = auto()
    ERROR = auto()
    DOES_NOT_EXIST = auto()  # Used by load operations when cache file not found
    SKIPPED = auto()  # Used by load/save operations when operation not needed
