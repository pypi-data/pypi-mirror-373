# MCP Server Configuration

This document explains how to configure the Strands Documentation Search MCP server for use with Kiro IDE or other MCP clients.

## Configuration

### Basic Configuration

Add the following to your MCP configuration file (e.g., `.kiro/settings/mcp.json`):

```json
{
  "mcpServers": {
    "strands-doc-search": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "/path/to/strands-mcp-server",
      "env": {
        "GITHUB_TOKEN": "your_github_token_here",
        "FASTMCP_LOG_LEVEL": "ERROR",
        "PYTHONWARNINGS": "ignore::DeprecationWarning"
      },
      "disabled": false,
      "autoApprove": [
        "search_documentation",
        "list_documentation",
        "health_check"
      ]
    }
  }
}
```

### Using uvx (Recommended for Production)

If you plan to publish this as a package, users can install and run it with uvx:

```json
{
  "mcpServers": {
    "strands-doc-search": {
      "command": "uvx",
      "args": ["strands-mcp-server@latest"],
      "env": {
        "GITHUB_TOKEN": "your_github_token_here",
        "FASTMCP_LOG_LEVEL": "ERROR",
        "PYTHONWARNINGS": "ignore::DeprecationWarning"
      },
      "disabled": false,
      "autoApprove": [
        "search_documentation",
        "list_documentation",
        "health_check"
      ]
    }
  }
}
```

## Environment Variables

### Required

- **GITHUB_TOKEN**: GitHub personal access token for API authentication
  - Without this, you'll hit GitHub API rate limits (60 requests/hour)
  - With token, you get 5,000 requests/hour
  - Create at: https://github.com/settings/tokens

### Optional

- **FASTMCP_LOG_LEVEL**: Set to "ERROR" to reduce log noise (default: "INFO")
- **PYTHONWARNINGS**: Set to "ignore::DeprecationWarning" to suppress FAISS warnings
- **STRANDS_CACHE_DIR**: Custom cache directory (default: "data/docs")
- **STRANDS_INDEX_DIR**: Custom index directory (default: "data/indexes")

## GitHub Token Setup

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name like "Strands MCP Server"
4. Select scopes: **public_repo** (for accessing public repositories)
5. Click "Generate token"
6. Copy the token and add it to your MCP configuration

## Auto-Approve Tools

The following tools are safe to auto-approve:

- `search_documentation`: Search Strands SDK documentation
- `list_documentation`: Browse available documentation sections
- `health_check`: Check server health status

## Troubleshooting

### Rate Limit Errors

If you see "403 rate limit exceeded" errors:
- Ensure your GITHUB_TOKEN is set correctly
- Verify the token has `public_repo` scope
- Check that the token hasn't expired

### FAISS Warnings

If you see SWIG deprecation warnings:
- Add `"PYTHONWARNINGS": "ignore::DeprecationWarning"` to the env section
- These warnings don't affect functionality

### Service Initialization Failures

The server is designed to handle failures gracefully:
- If documentation fetching fails, it will use cached data
- If indexing fails, the server continues without search functionality
- Check logs for specific error details

## Testing Configuration

You can test your configuration by running:

```bash
# Test with your GitHub token
GITHUB_TOKEN=your_token python main.py
```

The server should start without rate limit errors and successfully build the search index.