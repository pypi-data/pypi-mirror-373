"""Integration tests for MCP protocol compliance."""

import asyncio
import json
import pytest
import sys
from pathlib import Path


class TestMCPProtocol:
    """Test MCP protocol compliance."""
    
    @pytest.mark.asyncio
    async def test_mcp_server_protocol(self):
        """Test complete MCP server protocol interaction."""
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        
        # Create subprocess to run the server
        process = await asyncio.create_subprocess_exec(
            sys.executable, "main.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=project_root
        )
        
        try:
            # Test initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            process.stdin.write((json.dumps(init_request) + "\n").encode())
            await process.stdin.drain()
            
            # Read initialize response
            line = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
            init_response = json.loads(line.decode().strip())
            
            # Verify initialize response
            assert init_response["jsonrpc"] == "2.0"
            assert init_response["id"] == 1
            assert "result" in init_response
            assert init_response["result"]["protocolVersion"] == "2024-11-05"
            assert "serverInfo" in init_response["result"]
            assert init_response["result"]["serverInfo"]["name"] == "Strands Documentation Search"
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            process.stdin.write((json.dumps(initialized_notification) + "\n").encode())
            await process.stdin.drain()
            
            # Test tools/list request
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            process.stdin.write((json.dumps(tools_request) + "\n").encode())
            await process.stdin.drain()
            
            # Read tools/list response
            line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            tools_response = json.loads(line.decode().strip())
            
            # Verify tools/list response
            assert tools_response["jsonrpc"] == "2.0"
            assert tools_response["id"] == 2
            assert "result" in tools_response
            assert "tools" in tools_response["result"]
            
            # Verify health_check tool is present
            tools = tools_response["result"]["tools"]
            health_tool = next((tool for tool in tools if tool["name"] == "health_check"), None)
            assert health_tool is not None
            assert health_tool["description"] == "Check server health status."
            
            # Test health_check tool call
            health_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "health_check",
                    "arguments": {}
                }
            }
            
            process.stdin.write((json.dumps(health_request) + "\n").encode())
            await process.stdin.drain()
            
            # Read health_check response
            line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
            health_response = json.loads(line.decode().strip())
            
            # Verify health_check response
            assert health_response["jsonrpc"] == "2.0"
            assert health_response["id"] == 3
            assert "result" in health_response
            assert health_response["result"]["isError"] is False
            assert "structuredContent" in health_response["result"]
            
            # Verify health data
            health_data = health_response["result"]["structuredContent"]
            assert health_data["status"] == "healthy"
            assert health_data["version"] == "0.1.0"
            assert "timestamp" in health_data
            assert "uptime_seconds" in health_data
            assert health_data["uptime_seconds"] >= 0
            
        finally:
            # Clean up
            process.stdin.close()
            try:
                await asyncio.wait_for(process.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()