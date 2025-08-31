"""Health check and monitoring utilities for the Strands MCP server."""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..models.documentation import DocumentIndex
from ..services.documentation_service import DocumentationService
from ..services.search_service import SearchService
from ..services.indexing_service import DocumentIndexingService

logger = logging.getLogger(__name__)


class HealthStatus:
    """Health status constants."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPED = "stopped"


class ComponentHealth:
    """Health information for a system component."""
    
    def __init__(
        self,
        name: str,
        status: str = HealthStatus.STARTING,
        message: str = "",
        details: Optional[Dict[str, Any]] = None,
        last_check: Optional[datetime] = None
    ):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.last_check = last_check or datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "last_check": self.last_check.isoformat()
        }


class SystemHealth:
    """Overall system health information."""
    
    def __init__(
        self,
        overall_status: str = HealthStatus.STARTING,
        components: Optional[List[ComponentHealth]] = None,
        uptime_seconds: float = 0.0,
        version: str = "0.1.0",
        start_time: Optional[datetime] = None
    ):
        self.overall_status = overall_status
        self.components = components or []
        self.uptime_seconds = uptime_seconds
        self.version = version
        self.start_time = start_time or datetime.now(timezone.utc)
        self.last_check = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "overall_status": self.overall_status,
            "uptime_seconds": self.uptime_seconds,
            "version": self.version,
            "start_time": self.start_time.isoformat(),
            "last_check": self.last_check.isoformat(),
            "components": [comp.to_dict() for comp in self.components]
        }


class HealthChecker:
    """Health checker for monitoring system components."""
    
    def __init__(
        self,
        documentation_service: Optional[DocumentationService] = None,
        search_service: Optional[SearchService] = None,
        indexing_service: Optional[DocumentIndexingService] = None
    ):
        """Initialize health checker.
        
        Args:
            documentation_service: Documentation service to monitor
            search_service: Search service to monitor
            indexing_service: Indexing service to monitor
        """
        self.documentation_service = documentation_service
        self.search_service = search_service
        self.indexing_service = indexing_service
        self.start_time = datetime.now(timezone.utc)
    
    async def check_documentation_service(self) -> ComponentHealth:
        """Check health of documentation service."""
        try:
            if not self.documentation_service:
                return ComponentHealth(
                    name="documentation_service",
                    status=HealthStatus.UNHEALTHY,
                    message="Documentation service not initialized"
                )
            
            # Check cache info
            cache_info = await self.documentation_service.get_cache_info()
            
            # Determine status based on cache availability
            status = HealthStatus.HEALTHY
            message = "Documentation service operational"
            
            if not cache_info.get("user_cache", {}).get("index_exists") and \
               not cache_info.get("bundled_cache", {}).get("index_exists"):
                status = HealthStatus.DEGRADED
                message = "No documentation cache available"
            elif not cache_info.get("cache_valid"):
                status = HealthStatus.DEGRADED
                message = "Documentation cache may be stale"
            
            return ComponentHealth(
                name="documentation_service",
                status=status,
                message=message,
                details=cache_info
            )
            
        except Exception as e:
            logger.error(f"Health check failed for documentation service: {e}")
            return ComponentHealth(
                name="documentation_service",
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}"
            )
    
    async def check_search_service(self) -> ComponentHealth:
        """Check health of search service."""
        try:
            if not self.search_service:
                return ComponentHealth(
                    name="search_service",
                    status=HealthStatus.UNHEALTHY,
                    message="Search service not initialized"
                )
            
            # Get index stats
            index_stats = self.search_service.get_index_stats()
            
            # Determine status based on index availability
            status = HealthStatus.HEALTHY
            message = "Search service operational"
            
            if index_stats.get("status") == "no_index_loaded":
                status = HealthStatus.DEGRADED
                message = "Search index not loaded"
            elif index_stats.get("total_chunks", 0) == 0:
                status = HealthStatus.DEGRADED
                message = "Search index is empty"
            
            return ComponentHealth(
                name="search_service",
                status=status,
                message=message,
                details=index_stats
            )
            
        except Exception as e:
            logger.error(f"Health check failed for search service: {e}")
            return ComponentHealth(
                name="search_service",
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}"
            )
    
    async def check_indexing_service(self) -> ComponentHealth:
        """Check health of indexing service."""
        try:
            if not self.indexing_service:
                return ComponentHealth(
                    name="indexing_service",
                    status=HealthStatus.UNHEALTHY,
                    message="Indexing service not initialized"
                )
            
            # Try to load latest index to verify functionality
            document_index, faiss_index = self.indexing_service.load_latest_index()
            
            status = HealthStatus.HEALTHY
            message = "Indexing service operational"
            details = {}
            
            if document_index is None or faiss_index is None:
                status = HealthStatus.DEGRADED
                message = "No index available"
            else:
                details = {
                    "index_version": document_index.version,
                    "chunk_count": len(document_index.chunks),
                    "last_updated": document_index.last_updated.isoformat(),
                    "embedding_model": document_index.embedding_model
                }
            
            return ComponentHealth(
                name="indexing_service",
                status=status,
                message=message,
                details=details
            )
            
        except Exception as e:
            logger.error(f"Health check failed for indexing service: {e}")
            return ComponentHealth(
                name="indexing_service",
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}"
            )
    
    async def check_network_connectivity(self) -> ComponentHealth:
        """Check network connectivity to GitHub."""
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.github.com/rate_limit")
                
                if response.status_code == 200:
                    rate_limit_info = response.json()
                    return ComponentHealth(
                        name="network_connectivity",
                        status=HealthStatus.HEALTHY,
                        message="Network connectivity operational",
                        details={
                            "github_api_accessible": True,
                            "rate_limit_remaining": rate_limit_info.get("rate", {}).get("remaining"),
                            "rate_limit_reset": rate_limit_info.get("rate", {}).get("reset")
                        }
                    )
                else:
                    return ComponentHealth(
                        name="network_connectivity",
                        status=HealthStatus.DEGRADED,
                        message=f"GitHub API returned status {response.status_code}",
                        details={"github_api_accessible": False, "status_code": response.status_code}
                    )
                    
        except Exception as e:
            logger.warning(f"Network connectivity check failed: {e}")
            return ComponentHealth(
                name="network_connectivity",
                status=HealthStatus.DEGRADED,
                message="Network connectivity check failed",
                details={"error": str(e)}
            )
    
    async def perform_full_health_check(self) -> SystemHealth:
        """Perform comprehensive health check of all components."""
        start_time = time.time()
        
        logger.info("Starting comprehensive health check")
        
        # Check all components concurrently
        health_checks = await asyncio.gather(
            self.check_documentation_service(),
            self.check_search_service(),
            self.check_indexing_service(),
            self.check_network_connectivity(),
            return_exceptions=True
        )
        
        components = []
        for check_result in health_checks:
            if isinstance(check_result, ComponentHealth):
                components.append(check_result)
            else:
                # Handle exceptions from health checks
                logger.error(f"Health check exception: {check_result}")
                components.append(ComponentHealth(
                    name="unknown_component",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {str(check_result)}"
                ))
        
        # Determine overall status
        overall_status = self._determine_overall_status(components)
        
        # Calculate uptime
        uptime_seconds = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        
        health_check_duration = (time.time() - start_time) * 1000
        
        logger.info(
            f"Health check completed in {health_check_duration:.2f}ms",
            extra={
                "extra_fields": {
                    "operation": "health_check",
                    "component": "health_checker",
                    "duration_ms": health_check_duration,
                    "overall_status": overall_status,
                    "component_count": len(components)
                }
            }
        )
        
        return SystemHealth(
            overall_status=overall_status,
            components=components,
            uptime_seconds=uptime_seconds,
            start_time=self.start_time
        )
    
    def _determine_overall_status(self, components: List[ComponentHealth]) -> str:
        """Determine overall system status based on component health."""
        if not components:
            return HealthStatus.STARTING
        
        statuses = [comp.status for comp in components]
        
        # If any component is unhealthy, system is unhealthy
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        
        # If any component is degraded, system is degraded
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        
        # If all components are healthy, system is healthy
        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        
        # Default to starting if mixed states
        return HealthStatus.STARTING
    
    async def check_readiness(self) -> bool:
        """Check if the system is ready to serve requests."""
        try:
            # Quick readiness check - just verify core services are available
            if not self.search_service:
                return False
            
            index_stats = self.search_service.get_index_stats()
            return index_stats.get("status") != "no_index_loaded"
            
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return False
    
    async def check_liveness(self) -> bool:
        """Check if the system is alive and responsive."""
        try:
            # Simple liveness check - verify we can perform basic operations
            start_time = time.time()
            
            # Just check that we can access services without errors
            if self.documentation_service:
                await self.documentation_service.get_cache_info()
            
            duration = time.time() - start_time
            
            # If it takes too long, consider it unhealthy
            return duration < 5.0
            
        except Exception as e:
            logger.error(f"Liveness check failed: {e}")
            return False