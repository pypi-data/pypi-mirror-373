# Setup Notes

## Dependencies

The project is configured with core dependencies. Note that `sentence-transformers` will be added in task 6 when implementing the embedding system, as it has platform-specific PyTorch dependencies that may require special handling on different systems.

## Platform Compatibility

For macOS x86_64 systems, PyTorch dependencies may need to be installed from the CPU-only index:
```bash
uv add torch --index https://download.pytorch.org/whl/cpu
uv add sentence-transformers
```

## Project Structure

The project follows the recommended MCP server structure with:
- `src/strands_mcp/` - Main package
- `data/` - Cached documentation and indexes
- `tests/` - Test suite
- `main.py` - MCP server entry point