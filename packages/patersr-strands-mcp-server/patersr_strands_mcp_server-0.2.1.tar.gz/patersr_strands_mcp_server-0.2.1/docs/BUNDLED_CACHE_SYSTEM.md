# Bundled Cache System

The Strands MCP Server implements a hierarchical cache system to provide immediate functionality even on first installation or in offline environments.

## Cache Hierarchy

The system uses a three-tier cache hierarchy:

1. **User Cache** (`~/.cache/strands-mcp/` or `data/docs/`) - Updated by background processes
2. **Bundled Cache** (`strands_mcp/data/cache/`) - Read-only, ships with package
3. **No Cache** - Falls back to limited functionality

### Cache Priority

When the server needs documentation, it follows this priority order:

```
User Cache → Bundled Cache → None
```

- **User Cache**: If available and valid, always used first
- **Bundled Cache**: Used when user cache is unavailable or corrupted
- **No Cache**: Server starts with limited functionality and updates in background

## Bundled Cache Features

### Immediate Availability
- Ships with the package installation
- Provides instant functionality without network access
- Enables offline operation

### Read-Only Design
- Never modified by the running server
- Only updated during package builds (CI/CD)
- Ensures consistent baseline functionality

### Fallback Safety
- Automatically used when user cache fails
- Provides graceful degradation
- Maintains service availability

## Building Bundled Cache

### Development
```bash
# Build bundled cache from latest documentation
python scripts/build_bundled_cache.py

# Force rebuild even if cache is recent
python scripts/build_bundled_cache.py --force
```

### CI/CD Integration
The bundled cache should be built during the package build process:

```yaml
# Example GitHub Actions step
- name: Build bundled cache
  run: python scripts/build_bundled_cache.py --force
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Package Configuration

The bundled cache is included in the package via `pyproject.toml`:

```toml
[tool.hatch.build.targets.wheel.shared-data]
"src/strands_mcp/data" = "strands_mcp/data"
```

This ensures the cache directory is installed with the package.

## Usage Examples

### First-Time Installation
```python
# User installs package
pip install strands-mcp-server

# Server starts immediately using bundled cache
# No network access required for basic functionality
```

### Cache Corruption Recovery
```python
# If user cache becomes corrupted
doc_service = DocumentationService()
chunks = await doc_service.get_cached_docs()
# Automatically falls back to bundled cache
```

### Offline Operation
```python
# Server works offline using bundled cache
# Background updates fail gracefully
# Service remains available with cached content
```

## Implementation Details

### DocumentationService Changes
- Added `bundled_cache_dir` property pointing to package data
- Modified `get_cached_docs()` to implement cache hierarchy
- Updated `get_cache_info()` to report both cache states
- Ensured `save_docs_to_cache()` only updates user cache

### Directory Structure
```
src/strands_mcp/data/
├── cache/
│   └── index.json          # Bundled cache index
└── docs/
    └── README.md           # Documentation about data directory
```

### Cache Information
The `get_cache_info()` method now returns information about both caches:

```json
{
  "user_cache": {
    "index_exists": true,
    "chunk_count": 25,
    "last_updated": "2024-01-15T10:30:00Z"
  },
  "bundled_cache": {
    "index_exists": true,
    "chunk_count": 20,
    "last_updated": "2024-01-01T00:00:00Z"
  }
}
```

## Testing

The system includes comprehensive tests:

- **Unit Tests**: Cache hierarchy logic and fallback behavior
- **Integration Tests**: End-to-end cache workflows
- **Build Tests**: Cache building and packaging verification

Run tests with:
```bash
pytest tests/unit/test_bundled_cache.py
pytest tests/integration/test_cache_hierarchy.py
pytest tests/integration/test_bundled_cache_build.py
```

## Benefits

1. **Immediate Functionality**: Works out of the box without network access
2. **Offline Support**: Continues working in offline environments
3. **Graceful Degradation**: Falls back to bundled cache if user cache fails
4. **Fast Startup**: No need to download documentation on first run
5. **Reliable Baseline**: Always have a known-good cache available