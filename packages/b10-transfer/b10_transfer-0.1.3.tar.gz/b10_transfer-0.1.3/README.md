https://www.notion.so/ml-infra/mega-base-cache-24291d247273805b8e20fe26677b7b0f

# B10 Transfer

PyTorch file transfer for Baseten deployments.

## Usage

```python
import b10_transfer

# Inside model.load() function
def load()
    # Load cache before torch.compile()
    cache_loaded = b10_transfer.load_compile_cache()

    # ...

    # Your model compilation
    model = torch.compile(model)
    # Warm up the model with dummy prompts, and arguments that would be typically used in your requests (e.g resolutions)
    dummy_input = "What is the capital of France?"
    model(dummy_input)

    # ...

    # Save cache after compilation
    if not cache_loaded:
        b10_transfer.save_compile_cache()
```

## Configuration

Configure via environment variables:

```bash
# Cache directories
export TORCH_CACHE_DIR="/tmp/torchinductor_root"      # Default
export B10FS_CACHE_DIR="/cache/model/compile_cache"   # Default  
export LOCAL_WORK_DIR="/app"                          # Default

# Cache limits
export MAX_CACHE_SIZE_MB="1024"                       # 1GB default
```

## How It Works

### Environment-Specific Caching

The library automatically creates unique cache keys based on your environment:

```
torch-2.1.0_cuda-12.1_cc-8.6_triton-2.1.0 → cache_a1b2c3d4e5f6.latest.tar.gz
torch-2.0.1_cuda-11.8_cc-7.5_triton-2.0.1 → cache_x9y8z7w6v5u4.latest.tar.gz
torch-2.1.0_cpu_triton-none                → cache_m1n2o3p4q5r6.latest.tar.gz
```

**Components used:**
- **PyTorch version** (e.g., `torch-2.1.0`)
- **CUDA version** (e.g., `cuda-12.1` or `cpu`)
- **GPU compute capability** (e.g., `cc-8.6` for A100)
- **Triton version** (e.g., `triton-2.1.0` or `triton-none`)

### Cache Workflow

1. **Load Phase** (startup): Generate environment key, check for matching cache in B10FS, extract to local directory
2. **Save Phase** (after compilation): Create archive, atomic copy to B10FS with environment-specific filename

### Lock-Free Race Prevention  

Uses journal pattern with atomic filesystem operations for parallel-safe cache saves.

## API Reference

### Functions

- `load_compile_cache() -> bool`: Load cache from B10FS for current environment
- `save_compile_cache() -> bool`: Save cache to B10FS with environment-specific filename
- `clear_local_cache() -> bool`: Clear local cache directory
- `get_cache_info() -> Dict[str, Any]`: Get cache status information for current environment
- `list_available_caches() -> Dict[str, Any]`: List all cache files with environment details

### Exceptions

- `CacheError`: Base exception for cache operations
- `CacheValidationError`: Path validation or compatibility check failed

## Performance Impact

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger('b10_transfer').setLevel(logging.DEBUG)
```
