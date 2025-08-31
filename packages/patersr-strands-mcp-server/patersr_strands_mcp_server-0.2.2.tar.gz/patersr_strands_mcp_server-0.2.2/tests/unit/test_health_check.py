"""Tests for health check utilities."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from src.strands_mcp.utils.health_check import (
    HealthStatus,
    ComponentHealth,
    SystemHealth,
    HealthChecker
)
from src.strands_mcp.services.documentation_service import DocumentationService
from src.strands_mcp.services.search_service import SearchService
from src.strands_mcp.services.indexing_service import DocumentIndexingService


class TestHealthStatus:
    """Test health status constants."""
    
    def test_health_status_constants(self):
        """Test that health status constants are defined correctly."""
        assert HealthStatus.HEALTHY == "healthy"
        assert HealthStatus.DEGRADED == "degraded"
        assert HealthStatus.UNHEALTHY == "unhealthy"
        assert HealthStatus.STARTING == "starting"
        assert HealthStatus.STOPPED == "stopped"


class TestComponentHealth:
    """Test ComponentHealth class."""
    
    def test_component_health_creation(self):
        """Test creating ComponentHealth instance."""
        health = ComponentHealth(
            name="test_component",
            status=HealthStatus.HEALTHY,
            message="All good",
            details={"key": "value"}
        )
        
        assert health.name == "test_component"
        assert health.status == HealthStatus.HEALTHY
        assert health.message == "All good"
        assert health.details == {"key": "value"}
        assert isinstance(health.last_check, datetime)
    
    def test_component_health_to_dict(self):
        """Test ComponentHealth to_dict conversion."""
        health = ComponentHealth(
            name="test_component",
            status=HealthStatus.HEALTHY,
            message="All good"
        )
        
        result = health.to_dict()
        
        assert result["name"] == "test_component"
        assert result["status"] == HealthStatus.HEALTHY
        assert result["message"] == "All good"
        assert "last_check" in result
        assert isinstance(result["last_check"], str)  # ISO format


class TestSystemHealth:
    """Test SystemHealth class."""
    
    def test_system_health_creation(self):
        """Test creating SystemHealth instance."""
        component = ComponentHealth("test", HealthStatus.HEALTHY)
        health = SystemHealth(
            overall_status=HealthStatus.HEALTHY,
            components=[component],
            uptime_seconds=100.0
        )
        
        assert health.overall_status == HealthStatus.HEALTHY
        assert len(health.components) == 1
        assert health.uptime_seconds == 100.0
        assert isinstance(health.start_time, datetime)
    
    def test_system_health_to_dict(self):
        """Test SystemHealth to_dict conversion."""
        component = ComponentHealth("test", HealthStatus.HEALTHY)
        health = SystemHealth(
            overall_status=HealthStatus.HEALTHY,
            components=[component]
        )
        
        result = health.to_dict()
        
        assert result["overall_status"] == HealthStatus.HEALTHY
        assert len(result["components"]) == 1
        assert "start_time" in result
        assert "last_check" in result


class TestHealthChecker:
    """Test HealthChecker functionality."""
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        doc_service = MagicMock(spec=DocumentationService)
        search_service = MagicMock(spec=SearchService)
        indexing_service = MagicMock(spec=DocumentIndexingService)
        
        return doc_service, search_service, indexing_service
    
    @pytest.fixture
    def health_checker(self, mock_services):
        """Create HealthChecker with mock services."""
        doc_service, search_service, indexing_service = mock_services
        return HealthChecker(
            documentation_service=doc_service,
            search_service=search_service,
            indexing_service=indexing_service
        )
    
    @pytest.mark.asyncio
    async def test_check_documentation_service_healthy(self, health_checker, mock_services):
        """Test documentation service health check - healthy state."""
        doc_service, _, _ = mock_services
        
        # Mock healthy cache info
        doc_service.get_cache_info = AsyncMock(return_value={
            "cache_valid": True,
            "user_cache": {"index_exists": True},
            "bundled_cache": {"index_exists": True}
        })
        
        result = await health_checker.check_documentation_service()
        
        assert result.name == "documentation_service"
        assert result.status == HealthStatus.HEALTHY
        assert "operational" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_documentation_service_degraded(self, health_checker, mock_services):
        """Test documentation service health check - degraded state."""
        doc_service, _, _ = mock_services
        
        # Mock degraded cache info (no cache available)
        doc_service.get_cache_info = AsyncMock(return_value={
            "cache_valid": False,
            "user_cache": {"index_exists": False},
            "bundled_cache": {"index_exists": False}
        })
        
        result = await health_checker.check_documentation_service()
        
        assert result.name == "documentation_service"
        assert result.status == HealthStatus.DEGRADED
        assert "no documentation cache" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_documentation_service_unhealthy(self, health_checker, mock_services):
        """Test documentation service health check - unhealthy state."""
        doc_service, _, _ = mock_services
        
        # Mock service failure
        doc_service.get_cache_info = AsyncMock(side_effect=Exception("Service error"))
        
        result = await health_checker.check_documentation_service()
        
        assert result.name == "documentation_service"
        assert result.status == HealthStatus.UNHEALTHY
        assert "health check failed" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_search_service_healthy(self, health_checker, mock_services):
        """Test search service health check - healthy state."""
        _, search_service, _ = mock_services
        
        # Mock healthy index stats
        search_service.get_index_stats.return_value = {
            "status": "loaded",
            "total_chunks": 100,
            "unique_documents": 50
        }
        
        result = await health_checker.check_search_service()
        
        assert result.name == "search_service"
        assert result.status == HealthStatus.HEALTHY
        assert "operational" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_search_service_degraded(self, health_checker, mock_services):
        """Test search service health check - degraded state."""
        _, search_service, _ = mock_services
        
        # Mock no index loaded
        search_service.get_index_stats.return_value = {
            "status": "no_index_loaded"
        }
        
        result = await health_checker.check_search_service()
        
        assert result.name == "search_service"
        assert result.status == HealthStatus.DEGRADED
        assert "index not loaded" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_indexing_service_healthy(self, health_checker, mock_services):
        """Test indexing service health check - healthy state."""
        _, _, indexing_service = mock_services
        
        # Mock successful index loading
        mock_document_index = MagicMock()
        mock_document_index.version = "1.0"
        mock_document_index.chunks = ["chunk1", "chunk2"]
        mock_document_index.last_updated = datetime.now(timezone.utc)
        mock_document_index.embedding_model = "test-model"
        
        mock_faiss_index = MagicMock()
        
        indexing_service.load_latest_index.return_value = (mock_document_index, mock_faiss_index)
        
        result = await health_checker.check_indexing_service()
        
        assert result.name == "indexing_service"
        assert result.status == HealthStatus.HEALTHY
        assert "operational" in result.message.lower()
        assert result.details["chunk_count"] == 2
    
    @pytest.mark.asyncio
    async def test_check_network_connectivity_healthy(self, health_checker):
        """Test network connectivity check - healthy state."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "rate": {"remaining": 5000, "reset": 1234567890}
            }
            mock_client.get.return_value = mock_response
            
            result = await health_checker.check_network_connectivity()
            
            assert result.name == "network_connectivity"
            assert result.status == HealthStatus.HEALTHY
            assert "operational" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_check_network_connectivity_degraded(self, health_checker):
        """Test network connectivity check - degraded state."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_client.get.return_value = mock_response
            
            result = await health_checker.check_network_connectivity()
            
            assert result.name == "network_connectivity"
            assert result.status == HealthStatus.DEGRADED
            assert "403" in result.message
    
    @pytest.mark.asyncio
    async def test_perform_full_health_check(self, health_checker, mock_services):
        """Test full health check with mixed component states."""
        doc_service, search_service, indexing_service = mock_services
        
        # Mock healthy documentation service
        doc_service.get_cache_info = AsyncMock(return_value={
            "cache_valid": True,
            "user_cache": {"index_exists": True},
            "bundled_cache": {"index_exists": True}
        })
        
        # Mock degraded search service
        search_service.get_index_stats.return_value = {
            "status": "no_index_loaded"
        }
        
        # Mock healthy indexing service
        mock_document_index = MagicMock()
        mock_document_index.version = "1.0"
        mock_document_index.chunks = ["chunk1"]
        mock_document_index.last_updated = datetime.now(timezone.utc)
        mock_document_index.embedding_model = "test-model"
        indexing_service.load_latest_index.return_value = (mock_document_index, MagicMock())
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"rate": {"remaining": 5000}}
            mock_client.get.return_value = mock_response
            
            result = await health_checker.perform_full_health_check()
            
            # Should be degraded due to search service
            assert result.overall_status == HealthStatus.DEGRADED
            assert len(result.components) == 4  # All components checked
            assert result.uptime_seconds >= 0
    
    def test_determine_overall_status_healthy(self, health_checker):
        """Test overall status determination - all healthy."""
        components = [
            ComponentHealth("comp1", HealthStatus.HEALTHY),
            ComponentHealth("comp2", HealthStatus.HEALTHY)
        ]
        
        status = health_checker._determine_overall_status(components)
        assert status == HealthStatus.HEALTHY
    
    def test_determine_overall_status_degraded(self, health_checker):
        """Test overall status determination - some degraded."""
        components = [
            ComponentHealth("comp1", HealthStatus.HEALTHY),
            ComponentHealth("comp2", HealthStatus.DEGRADED)
        ]
        
        status = health_checker._determine_overall_status(components)
        assert status == HealthStatus.DEGRADED
    
    def test_determine_overall_status_unhealthy(self, health_checker):
        """Test overall status determination - some unhealthy."""
        components = [
            ComponentHealth("comp1", HealthStatus.HEALTHY),
            ComponentHealth("comp2", HealthStatus.UNHEALTHY)
        ]
        
        status = health_checker._determine_overall_status(components)
        assert status == HealthStatus.UNHEALTHY
    
    @pytest.mark.asyncio
    async def test_check_readiness_ready(self, health_checker, mock_services):
        """Test readiness check - ready state."""
        _, search_service, _ = mock_services
        
        search_service.get_index_stats.return_value = {
            "status": "loaded"
        }
        
        result = await health_checker.check_readiness()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_readiness_not_ready(self, health_checker, mock_services):
        """Test readiness check - not ready state."""
        _, search_service, _ = mock_services
        
        search_service.get_index_stats.return_value = {
            "status": "no_index_loaded"
        }
        
        result = await health_checker.check_readiness()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_liveness_alive(self, health_checker, mock_services):
        """Test liveness check - alive state."""
        doc_service, _, _ = mock_services
        
        doc_service.get_cache_info = AsyncMock(return_value={})
        
        result = await health_checker.check_liveness()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_liveness_not_alive(self, health_checker, mock_services):
        """Test liveness check - not alive state."""
        doc_service, _, _ = mock_services
        
        doc_service.get_cache_info = AsyncMock(side_effect=Exception("Service error"))
        
        result = await health_checker.check_liveness()
        assert result is False