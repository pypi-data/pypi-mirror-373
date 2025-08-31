# Technology Stack

## Core Technologies
- **Language**: Python 3.11+
- **Package Manager**: uv (for fast dependency management)
- **MCP Framework**: Model Context Protocol Python SDK
- **Documentation Indexing**: FAISS or similar vector search
- **AWS Integration**: boto3, awscli
- **HTTP Client**: httpx (for async operations)
- **Configuration**: Pydantic for data validation

## Development Environment
- **Platform**: macOS (darwin)
- **Shell**: zsh
- **IDE Configuration**: VSCode with Kiro AI assistant
- **MCP Configuration**: Will be configured for this server

## Key Dependencies
```toml
[dependencies]
mcp = "^1.0.0"                    # MCP Python SDK
boto3 = "^1.34.0"                 # AWS SDK
httpx = "^0.27.0"                 # Async HTTP client
pydantic = "^2.5.0"               # Data validation
faiss-cpu = "^1.7.4"              # Vector search (CPU version)
sentence-transformers = "^2.2.2"  # Text embeddings
click = "^8.1.0"                  # CLI interface
aiofiles = "^23.2.0"              # Async file operations
```

## Development Dependencies
```toml
[dev-dependencies]
pytest = "^7.4.0"                 # Testing framework
pytest-asyncio = "^0.21.0"        # Async testing
black = "^23.12.0"                # Code formatting
ruff = "^0.1.8"                   # Linting
mypy = "^1.8.0"                   # Type checking
```

## Common Commands

### Setup
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

### Development
```bash
# Run the MCP server
python main.py

# Run tests
pytest

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

### MCP Server Testing
```bash
# Test MCP server with stdio transport
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python main.py

# Test with MCP client tools
mcp-client stdio python main.py
```

## AWS Integration Requirements
- **AWS CLI**: Required for model availability checks
- **Credentials**: AWS credentials configured via standard methods
- **Permissions**: Bedrock model access, quota checking permissions

## Documentation Indexing Strategy
- **Update Frequency**: Daily check on first server start
- **Storage**: Local file system with version tracking
- **Search**: Vector embeddings with semantic search
- **Fallback**: Direct GitHub API for latest content

## Guidelines
- Use async/await patterns for I/O operations
- Implement proper error handling for AWS API calls
- Cache documentation locally with TTL
- Follow MCP protocol specifications strictly
- Maintain backward compatibility with Strands SDK versions
- Use structured logging for debugging MCP interactions