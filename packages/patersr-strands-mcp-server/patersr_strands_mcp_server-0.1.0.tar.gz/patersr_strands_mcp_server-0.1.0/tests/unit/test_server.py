"""Unit tests for the MCP server."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from strands_mcp.server import StrandsMCPServer, ServerHealth


class TestStrandsMCPServer:
    """Test cases for StrandsMCPServer."""
    
    def test_server_initialization(self):
        """Test server initializes correctly."""
        server = StrandsMCPServer()
        
        assert server._mcp_server is not None
        assert server._running is False
        assert server._start_time is None
        assert server.uptime == 0.0
        assert not server.is_running
    
    def test_server_properties(self):
        """Test server properties."""
        server = StrandsMCPServer()
        
        # Test initial state
        assert not server.is_running
        assert server.uptime == 0.0
        
        # Simulate server start
        server._running = True
        server._start_time = datetime.now()
        
        assert server.is_running
        assert server.uptime >= 0.0
    
    def test_server_health_model(self):
        """Test ServerHealth model validation."""
        health = ServerHealth(
            status="healthy",
            timestamp=datetime.now(),
            uptime_seconds=10.5
        )
        
        assert health.status == "healthy"
        assert health.version == "0.1.0"
        assert health.uptime_seconds == 10.5
        assert isinstance(health.timestamp, datetime)
    
    @patch('strands_mcp.server.FastMCP')
    def test_server_start_error_handling(self, mock_fastmcp):
        """Test server handles start errors gracefully."""
        # Mock FastMCP to raise an exception
        mock_server = Mock()
        mock_server.run.side_effect = Exception("Test error")
        mock_fastmcp.return_value = mock_server
        
        server = StrandsMCPServer()
        
        with pytest.raises(Exception, match="Test error"):
            server.start()
        
        assert not server.is_running
    
    def test_server_stop(self):
        """Test server stop functionality."""
        server = StrandsMCPServer()
        server._running = True
        
        server.stop()
        
        assert not server.is_running