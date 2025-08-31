#!/usr/bin/env python3
"""Main entry point for Strands MCP Server."""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

from .server import StrandsMCPServer


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging output."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


def setup_logging() -> None:
    """Configure structured logging for the MCP server."""
    # Suppress FAISS/SWIG deprecation warnings
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module=".*swig.*")
    warnings.filterwarnings("ignore", message=".*SwigPy.*")
    
    # Create structured formatter
    formatter = StructuredFormatter()
    
    # Configure stderr handler with structured output
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)


def main() -> None:
    """Main entry point for the MCP server."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Initializing Strands MCP Server")
        server = StrandsMCPServer()
        
        # Start the server (this will block until the server stops)
        # FastMCP handles the event loop internally
        server.start()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal (SIGINT)")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    main()