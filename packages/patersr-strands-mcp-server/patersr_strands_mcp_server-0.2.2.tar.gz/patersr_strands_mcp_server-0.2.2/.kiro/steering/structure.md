# Project Structure

## Current Organization
```
.
├── .kiro/              # Kiro AI assistant configuration
│   └── steering/       # AI guidance documents
├── .vscode/            # VSCode workspace settings
├── .venv/              # Python virtual environment
├── main.py             # MCP Server entry point
├── pyproject.toml      # Python project configuration
├── uv.lock             # Dependency lock file
└── README.md           # Project documentation
```

## Recommended MCP Server Structure
```
src/
├── strands_mcp/        # Main MCP server package
│   ├── __init__.py
│   ├── server.py       # MCP server implementation
│   ├── tools/          # MCP tools implementation
│   │   ├── __init__.py
│   │   ├── documentation.py    # Documentation search tools
│   │   ├── project_setup.py    # Project initialization tools
│   │   ├── observability.py   # Observability and evaluation tools
│   │   └── deployment.py      # Deployment guidance tools
│   ├── services/       # Core business logic
│   │   ├── __init__.py
│   │   ├── doc_indexer.py      # Document indexing service
│   │   ├── strands_client.py   # Strands SDK interaction
│   │   ├── aws_client.py       # AWS API interactions
│   │   └── project_manager.py  # Project setup management
│   ├── models/         # Data models and schemas
│   │   ├── __init__.py
│   │   ├── project_config.py   # Project configuration models
│   │   └── documentation.py    # Documentation models
│   └── utils/          # Utility functions
│       ├── __init__.py
│       ├── file_utils.py       # File system utilities
│       └── validation.py      # Input validation
├── data/               # Cached documentation and indexes
│   ├── docs/           # Downloaded Strands documentation
│   └── indexes/        # Search indexes
└── tests/              # Test suite
    ├── unit/           # Unit tests
    ├── integration/    # Integration tests
    └── fixtures/       # Test data
```

## Configuration Structure
```
config/
├── default.json        # Default MCP server configuration
├── logging.json        # Logging configuration
└── templates/          # Project templates
    ├── basic/          # Basic Strands project template
    ├── multi_agent/    # Multi-agent project templates
    └── samples/        # Sample implementations
```

## Naming Conventions
- Use snake_case for Python files and directories
- Use descriptive names that reflect MCP server functionality
- Prefix MCP tools with clear action verbs (search_, create_, setup_, etc.)
- Keep module names concise but meaningful
- Use consistent patterns for tool and resource naming

## Organization Principles
- Separate MCP server concerns from business logic
- Group related tools and services together
- Keep documentation indexing separate from project management
- Maintain clear boundaries between AWS interactions and Strands SDK operations
- Use dependency injection for testability