import os
import logging
import subprocess
from pathlib import Path

from .utils import timed_fn, safe_unlink, CacheValidationError, validate_path_security
from .constants import MAX_CACHE_SIZE_MB

logger = logging.getLogger(__name__)


class ArchiveError(Exception):
    """Archive operation failed."""

    pass


def get_file_size_mb(file_path: Path) -> float:
    """Get the size of a file in megabytes.

    Args:
        file_path: Path to the file to measure.

    Returns:
        float: File size in megabytes, or 0.0 if file doesn't exist or
               can't be accessed.

    Raises:
        No exceptions are raised; OSError is caught and returns 0.0.
    """
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except OSError:
        return 0.0


def _compress_directory_to_tar(source_dir: Path, target_file: Path) -> None:
    """Compress directory contents to a gzipped tar archive using system tar.

    This function recursively compresses all files in the source directory
    into a gzipped tar archive using the system tar command for better performance.

    Args:
        source_dir: Path to the directory to compress.
        target_file: Path where the compressed archive will be created.

    Raises:
        subprocess.CalledProcessError: If tar command fails.
        OSError: If source directory can't be read or target file can't be written.
    """
    # Use system tar command for better performance
    # -czf: create, gzip, file
    # -C: change to directory before archiving
    cmd = ["tar", "-czf", str(target_file), "-C", str(source_dir), "."]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise OSError(f"tar compression failed: {e.stderr}") from e


@timed_fn(logger=logger, name="Creating archive")
def create_archive(
    source_dir: Path, target_file: Path, max_size_mb: int = MAX_CACHE_SIZE_MB
) -> None:
    """Create a compressed archive with path validation and size limits.

    This function safely creates a gzipped tar archive from a source directory
    with security validation and size constraints. It validates paths to prevent
    directory traversal attacks and enforces maximum archive size limits.

    Args:
        source_dir: Path to the directory to archive. Must exist and be within
                   allowed directories (/tmp/ or its parent).
        target_file: Path where the archive will be created. Must be within
                    allowed directories (/app or /cache).
        max_size_mb: Maximum allowed archive size in megabytes. Defaults to MAX_CACHE_SIZE_MB.

    Raises:
        CacheValidationError: If paths are outside allowed directories.
        ArchiveError: If source directory doesn't exist, archive creation fails,
                     or archive exceeds size limit.
    """
    # Validate paths
    validate_path_security(
        str(source_dir),
        ["/tmp/", str(source_dir.parent)],
        f"Source directory {source_dir}",
        CacheValidationError,
    )
    validate_path_security(
        str(target_file),
        ["/app", "/cache"],
        f"Target file {target_file}",
        CacheValidationError,
    )

    if not source_dir.exists():
        raise ArchiveError(f"Source directory missing: {source_dir}")

    target_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        _compress_directory_to_tar(source_dir, target_file)
        size_mb = get_file_size_mb(target_file)

        if size_mb > max_size_mb:
            safe_unlink(
                target_file, f"Failed to delete oversized archive {target_file}"
            )
            raise ArchiveError(f"Archive too large: {size_mb:.1f}MB > {max_size_mb}MB")

    except Exception as e:
        safe_unlink(target_file, f"Failed to cleanup failed archive {target_file}")
        raise ArchiveError(f"Archive creation failed: {e}") from e


@timed_fn(logger=logger, name="Extracting archive")
def extract_archive(archive_file: Path, target_dir: Path) -> None:
    """Extract a compressed archive with security validation.

    This function safely extracts a gzipped tar archive to a target directory
    with security checks to prevent directory traversal attacks. It validates
    both the archive and target paths, and inspects archive contents for
    malicious paths before extraction.

    Args:
        archive_file: Path to the archive file to extract. Must exist and be
                     within allowed directories (/app or /cache).
        target_dir: Path to the directory where files will be extracted. Must
                   be within allowed directories (/tmp/ or its parent).

    Raises:
        CacheValidationError: If paths are outside allowed directories or if
                            archive contains unsafe paths (absolute paths or
                            paths with '..' components).
        ArchiveError: If archive file doesn't exist or extraction fails.
    """
    # Validate paths
    validate_path_security(
        str(archive_file),
        ["/app", "/cache"],
        f"Archive file {archive_file}",
        CacheValidationError,
    )
    validate_path_security(
        str(target_dir),
        ["/tmp/", str(target_dir.parent)],
        f"Target directory {target_dir}",
        CacheValidationError,
    )

    if not archive_file.exists():
        raise ArchiveError(f"Archive missing: {archive_file}")

    try:
        target_dir.mkdir(parents=True, exist_ok=True)

        # First, perform security check by listing archive contents
        list_cmd = ["tar", "-tzf", str(archive_file)]
        result = subprocess.run(list_cmd, check=True, capture_output=True, text=True)

        # Security check on all paths in the archive
        for path in result.stdout.strip().split("\n"):
            if path and (os.path.isabs(path) or ".." in path):
                raise CacheValidationError(f"Unsafe path in archive: {path}")

        # Extract using system tar command for better performance
        extract_cmd = ["tar", "-xzf", str(archive_file), "-C", str(target_dir)]
        subprocess.run(extract_cmd, check=True, capture_output=True, text=True)

    except subprocess.CalledProcessError as e:
        raise ArchiveError(f"tar extraction failed: {e.stderr}") from e
    except Exception as e:
        raise ArchiveError(f"Extraction failed: {e}") from e
