"""Environment detection utilities for GPU cache management.

This module provides functions to generate unique environment keys based on
GPU hardware and driver information for cache compatibility.
"""

import hashlib
import json
import logging
import os

# Optional imports - may not be available in all environments
try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)

KEY_LENGTH = 16
UNKNOWN_HOSTNAME = "unknown-host"


def get_cache_filename() -> str:
    """Get the cache filename prefix for the current environment.

    This function generates a cache filename prefix that includes the
    environment key and hostname to ensure cache files are environment-specific
    and unique per machine.

    Returns:
        str: Cache filename prefix in format "cache_{environment_key}.{hostname}".
    """
    env_key = get_environment_key()
    hostname = os.uname().nodename or os.getenv("HOSTNAME", UNKNOWN_HOSTNAME)
    return f"cache_{env_key}.{hostname}"


def get_environment_key() -> str:
    """Generate unique environment key based on PyTorch/CUDA/GPU configuration.

    This function creates a deterministic hash key based only on node-specific
    hardware and driver information to ensure cache compatibility across
    different environments with identical GPU configurations.

    Returns:
        str: A 16-character hex hash uniquely identifying the environment.

    Raises:
        RuntimeError: If PyTorch/CUDA are unavailable or environment key
                     generation fails for any reason.

    Note:
        Includes all GPU properties that affect Triton kernel generation.
        References from PyTorch repository:
        - Device name: GPU model identification (codecache.py:199)
        - CUDA version: Driver compatibility (codecache.py:200)

        These next four are bit more embedded in the codebase and not obviously used in the torchinductor_root cache check.
        They are commented out because:
        1) They are not explicitly used in the torchinductor_root cache check.
        2) It's not clear but likely that any violation of these properties will cause local re-compilation when the torch guards activate, not full recompilation.
        3) We don't want to over-estimate the number of unique environments since that'll cause more cache misses overall.
        We can add them back if we need to.

        - Compute capability: Available GPU instructions/features (scheduler.py:4286, triton_heuristics.py:480)
        - Multi-processor count: Affects occupancy and grid sizing (choices.py:210, triton_heuristics.py:539)
        - Warp size: Thread grouping (triton_heuristics.py:487, triton.py:2763)
        - Register limits: Affects kernel optimization strategies (triton_heuristics.py:518,536)

        We're also not including the torch and triton versions in the hash, despite the torch compilation cache dependent on these two things.
        This is because we are saving the cache to the `/cache/model` directory, which is already deployment-specific where the torch/triton versions are constant.
    """
    try:
        _validate_cuda_environment()

        device_properties = torch.cuda.get_device_properties(
            torch.cuda.current_device()
        )
        node_data = _extract_gpu_properties(device_properties, torch.version.cuda)

        node_json = json.dumps(node_data, sort_keys=True)
        return hashlib.sha256(node_json.encode("utf-8")).hexdigest()[:KEY_LENGTH]

    except (ImportError, RuntimeError, AssertionError) as e:
        logger.error(f"GPU environment unavailable: {e}")
        raise RuntimeError(f"Cannot generate environment key: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error during environment key generation: {e}")
        raise RuntimeError(f"Environment key generation failed: {e}") from e


def _validate_cuda_environment() -> None:
    """Validate that PyTorch and CUDA are available and properly configured.

    Raises:
        ImportError: If PyTorch is not available
        RuntimeError: If CUDA is not available or version is missing
    """
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch not available")

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA must be available - AMD/HIP not supported")

    if torch.version.cuda is None:
        raise RuntimeError("CUDA version must be available")


def _extract_gpu_properties(
    device_properties: any, cuda_version: str
) -> dict[str, any]:
    """Extract relevant GPU properties for environment key generation.

    Args:
        device_properties: CUDA device properties object
        cuda_version: CUDA version string
        SEE docstring of get_environment_key() for more details and why certain properties are excluded.

    Returns:
        Dict containing GPU properties that affect kernel generation
    """
    return {
        "device_name": device_properties.name,  # GPU model
        "cuda_version": cuda_version,  # Driver version
        # "compute_capability": (device_properties.major, device_properties.minor),  # GPU features
        # "multi_processor_count": device_properties.multi_processor_count,  # SM count for occupancy
        # "warp_size": device_properties.warp_size,  # Thread grouping size
        # "regs_per_multiprocessor": getattr(device_properties, "regs_per_multiprocessor", None),  # Register limits
        # "max_threads_per_multi_processor": getattr(device_properties, "max_threads_per_multi_processor", None),  # Thread limits
    }
