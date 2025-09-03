import os
import time
import logging
import getpass
from pathlib import Path
from contextlib import contextmanager
from typing import Generator, Any

logger = logging.getLogger(__name__)

# Lock file settings
LOCK_WAIT_SLEEP_SECONDS = 1.0  # How long to wait between lock file checks


class CacheError(Exception):
    """Base cache operation error."""

    pass


class CacheValidationError(CacheError):
    """Path validation or compatibility check failed."""

    pass


def get_current_username() -> str:
    """
    Get the current username using getpass.getuser().

    This uses the same method as PyTorch for consistency.

    Returns:
        str: Current username.

    Raises:
        RuntimeError: If unable to determine the current username.
    """
    try:
        return getpass.getuser()
    except Exception as e:
        raise RuntimeError(f"Unable to determine current username: {e}") from e


def validate_path_security(
    path: str,
    allowed_prefixes: list[str],
    name: str,
    exception_class: type = EnvironmentError,
) -> str:
    """
    Validate that a path is secure and within allowed directory prefixes.

    This function prevents directory traversal attacks and ensures paths
    are within expected locations for security. It handles symlinks like
    macOS /tmp -> /private/tmp by resolving both path and prefixes.

        Args:
        path: The path string to validate.
        allowed_prefixes: List of allowed directory prefix strings.
        name: Name of the configuration for error messages.
        exception_class: Exception class to raise on validation failure.
                        Defaults to EnvironmentError.

    Returns:
        str: The validated resolved path.

    Raises:
        exception_class: If path is outside allowed prefixes or contains
                        unsafe components.
    """
    if not path:
        raise exception_class(f"{name} cannot be empty")

    # Convert to Path and resolve to handle symlinks and relative paths
    try:
        resolved_path = str(Path(path).resolve())
    except (OSError, ValueError) as e:
        raise exception_class(f"{name} path resolution failed: {e}")

    # Check for directory traversal attempts
    if ".." in path or path != path.strip():
        raise exception_class(f"{name} contains unsafe path components: {path}")

    # Validate against allowed prefixes
    # Handle symlinks like macOS /tmp -> /private/tmp by checking both resolved and canonical forms
    path_matches = False
    for prefix in allowed_prefixes:
        # Check resolved path against resolved prefix
        try:
            resolved_prefix = str(Path(prefix).resolve())
            if resolved_path.startswith(resolved_prefix):
                path_matches = True
                break
        except (OSError, ValueError):
            # If prefix resolution fails, fall back to string comparison
            if resolved_path.startswith(prefix):
                path_matches = True
                break

    if not path_matches:
        raise exception_class(
            f"{name} path '{resolved_path}' must start with one of: {allowed_prefixes}"
        )

    return resolved_path


def validate_boolean_env(env_var: str, name: str) -> str:
    """
    Validate that an environment variable contains a safe boolean-like value.

    Args:
        env_var: The environment variable value to validate.
        name: Name of the configuration for error messages.

    Returns:
        str: The validated environment variable value.

    Raises:
        CacheValidationError: If the value is not a recognized boolean string.
    """
    valid_values = {"0", "1", "true", "false", "True", "False", ""}
    if env_var not in valid_values:
        raise CacheValidationError(
            f"{name} must be one of {valid_values}, got: {env_var}"
        )
    return env_var


def apply_cap(value: int, cap: int, name: str) -> int:
    """
    Apply security cap to user-provided values.
    Not amazing (doesn't prevent the user from modifying the pip package
    source code), but at least it prevents accidental environment variable
    setting that could cause resource exhaustion.
    """
    if value > cap:
        logger.warning(
            f"{name} capped at {cap} (requested {value}) for security/stability"
        )
        return cap
    return value


def timed_fn(logger=logger, name=None):
    """Decorator to log function execution time.

    This decorator logs when a function starts and finishes, including the
    total execution time in seconds.

    Args:
        logger: Logger instance to use for logging. Defaults to module logger.
        name: Custom name to use in log messages. If None, uses function name.

    Returns:
        Decorator function that wraps the target function with timing logic.
    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            logger.info(f"{name or fn.__name__} started")
            start = time.perf_counter()
            result = fn(*args, **kwargs)
            logger.info(
                f"{name or fn.__name__} finished in {time.perf_counter() - start:.2f}s"
            )
            return result

        return wrapper

    return decorator


def safe_execute(error_message: str, default_return: Any = None):
    """Decorator to safely execute a function with error handling.

    This decorator catches all exceptions from the wrapped function and logs
    them with a custom error message, then returns a default value instead
    of propagating the exception.

    Args:
        error_message: Message to log when an exception occurs.
        default_return: Value to return if the function raises an exception.
                       Defaults to None.

    Returns:
        Decorator function that wraps the target function with error handling.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{error_message}: {e}")
                return default_return

        return wrapper

    return decorator


# TODO(SR): Make the 1-second sleep a configurable parameter + document what it does.
# FIXME(SR): There's a race condition here. If a single process creates a lock file
#            (say because they are copy-ing in or copy-ing out, and the pod/replica crashes for whatever reason),
#            then the lock file will never be released. This is bad because then a bunch of other replicas will
#            be blocked from doing anything (loading in the cache or saving out the cache).
#            We either need to find a way to ENSURE that the lock file will be released if the pod/replica crashes OR in a certain amount of time.
#            OR enforce some retry-timeout logic to ensure that other replicas proceed with reading from the cache/writing to the cache if they are "held up" by the lock file N number of times or seconds perhaps
#            Just a thought...need to think more + test this out.
def critical_section_b10fs_file_lock(name):
    """Decorator to ensure critical section for b10fs file operations.

    This decorator ensures that the decorated function runs in a critical section
    where no other b10fs file operations can interfere. It uses a lock file to
    synchronize access.

    Args:
        name: The name of the operation, used for the lock file name.

    Returns:
        The decorated function with critical section handling.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Import here to avoid circular dependency
            from .constants import B10FS_CACHE_DIR

            lock_dir = Path(B10FS_CACHE_DIR)
            lock_dir.mkdir(parents=True, exist_ok=True)

            lock_file = lock_dir / f"{name}.lock"
            while lock_file.exists():
                logger.debug("Waiting for lock file to be released...")
                time.sleep(LOCK_WAIT_SLEEP_SECONDS)

            try:
                lock_file.touch()
                return func(*args, **kwargs)
            finally:
                lock_file.unlink(missing_ok=True)

        return wrapper

    return decorator


def safe_unlink(
    file_path: Path, error_message: str, success_message: str = None
) -> None:
    """Safely unlink a file with dead mount filesystem protection.

    This function attempts to delete a file while gracefully handling cases
    where the filesystem (like b10fs) becomes unavailable or dead during
    the operation. It uses missing_ok=True to handle missing files.

    Args:
        file_path: Path to the file to delete.
        error_message: Message to log if deletion fails.
        success_message: Optional message to log if deletion succeeds.

    Raises:
        No exceptions are raised; all errors are caught and logged.
    """
    try:
        file_path.unlink(missing_ok=True)
        if success_message:
            logger.debug(success_message)
    except Exception as e:
        logger.error(f"{error_message}: {e}")


@contextmanager
def temp_file_cleanup(temp_path: Path) -> Generator[Path, None, None]:
    """Context manager for temporary file with automatic safe cleanup.

    This context manager ensures that temporary files are cleaned up even
    if the filesystem becomes unavailable during the operation. It uses
    safe_unlink to handle dead mount scenarios gracefully.

    Args:
        temp_path: Path to the temporary file to manage.

    Yields:
        Path: The temporary file path for use within the context.

    Raises:
        Cleanup errors are handled gracefully and logged but not raised.
    """
    try:
        yield temp_path
    finally:
        safe_unlink(temp_path, f"Failed to delete temporary file {temp_path}")


def _is_b10fs_enabled() -> bool:
    """Check if b10fs filesystem is enabled via environment variable.

    This function checks the BASETEN_FS_ENABLED environment variable to
    determine if the b10fs shared filesystem is available for cache operations.

    Returns:
        bool: True if BASETEN_FS_ENABLED is set to "1" or "True", False otherwise.
    """
    # Import here to avoid circular dependency
    from .constants import BASETEN_FS_ENABLED

    return BASETEN_FS_ENABLED in ("1", "True", "true")


def _validate_b10fs_available() -> None:
    """Validate that b10fs filesystem is available for cache operations.

    This function checks if b10fs is enabled and raises an exception if not.
    It should be called before any operations that require b10fs access.

    Raises:
        CacheValidationError: If b10fs is not enabled (BASETEN_FS_ENABLED
                            is not set to "1" or "True").
    """
    if not _is_b10fs_enabled():
        raise CacheValidationError(
            "b10fs is not enabled. Set BASETEN_FS_ENABLED=1 or BASETEN_FS_ENABLED=True to enable cache operations."
        )


@contextmanager
def cache_operation(operation_name: str) -> Generator[None, None, None]:
    """Context manager for cache operations with b10fs validation and error handling.

    This context manager validates that b10fs is available before executing
    cache operations and provides consistent error logging. It should wrap
    any operations that require b10fs access.

    Args:
        operation_name: Name of the operation for error logging (e.g., "Load", "Save").

    Yields:
        None: Context for the operation to execute.

    Raises:
        CacheValidationError: If b10fs is not available (re-raised after logging).
        Exception: Any other errors during the operation (re-raised after logging).
    """
    try:
        _validate_b10fs_available()
        yield
    except CacheValidationError as e:
        logger.debug(f"{operation_name} failed: {e}")
        raise
    except Exception as e:
        logger.debug(f"{operation_name} failed: {e}")
        raise
