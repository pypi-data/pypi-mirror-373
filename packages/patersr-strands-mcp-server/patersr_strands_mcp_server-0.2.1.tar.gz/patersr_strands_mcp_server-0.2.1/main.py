#!/usr/bin/env python3
"""Development entry point for Strands MCP Server."""

import sys
from pathlib import Path

# Add src to Python path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from strands_mcp.main import main

if __name__ == "__main__":
    main()
