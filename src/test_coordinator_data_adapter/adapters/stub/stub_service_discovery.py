"""Stub service discovery repository implementation."""
import structlog
from datetime import datetime, UTC, timedelta
from typing import List, Optional
from test_coordinator_data_adapter.interfaces import ServiceDiscoveryRepository, ServiceInfo

logger = structlog.get_logger(__name__)


class StubServiceDiscoveryRepository(ServiceDiscoveryRepository):
    """In-memory stub implementation of service discovery repository."""

    def __init__(self):
        self._services: dict[str, ServiceInfo] = {}
        logger.info("stub_service_discovery_repository_initialized", storage="in-memory")

    async def register(self, service: ServiceInfo) -> ServiceInfo:
        """Register a service."""
        self._services[service.service_id] = service
        logger.debug(
            "service_registered",
            service_id=service.service_id,
            service_name=service.service_name,
            host=service.host,
            grpc_port=service.grpc_port,
        )
        return service

    async def deregister(self, service_id: str) -> bool:
        """Deregister a service."""
        if service_id in self._services:
            del self._services[service_id]
            logger.debug("service_deregistered", service_id=service_id)
            return True
        logger.warning("service_not_found_for_deregister", service_id=service_id)
        return False

    async def get_service_by_id(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service by ID."""
        service = self._services.get(service_id)
        logger.debug("service_retrieved_by_id", service_id=service_id, found=service is not None)
        return service

    async def get_service_by_name(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service by name (returns first matching)."""
        for service in self._services.values():
            if service.service_name == service_name:
                logger.debug("service_retrieved_by_name", service_name=service_name, service_id=service.service_id)
                return service
        logger.debug("service_not_found_by_name", service_name=service_name)
        return None

    async def list_services_by_name(self, service_name: str) -> List[ServiceInfo]:
        """List all instances of a service."""
        services = [s for s in self._services.values() if s.service_name == service_name]
        logger.debug("services_listed_by_name", service_name=service_name, count=len(services))
        return services

    async def list_all_services(self) -> List[ServiceInfo]:
        """List all registered services."""
        services = list(self._services.values())
        logger.debug("all_services_listed", count=len(services))
        return services

    async def update_heartbeat(self, service_id: str) -> ServiceInfo:
        """Update service heartbeat timestamp."""
        service = self._services.get(service_id)
        if not service:
            logger.warning("service_not_found_for_heartbeat", service_id=service_id)
            raise ValueError(f"Service {service_id} not found")
        service.last_seen = datetime.now(UTC)
        logger.debug("service_heartbeat_updated", service_id=service_id, last_seen=service.last_seen)
        return service

    async def remove_stale_services(self, threshold_seconds: int) -> int:
        """Remove services not seen within threshold."""
        now = datetime.now(UTC)
        threshold_time = now - timedelta(seconds=threshold_seconds)

        stale_services = [
            service_id
            for service_id, service in self._services.items()
            if service.last_seen < threshold_time
        ]

        for service_id in stale_services:
            del self._services[service_id]

        logger.debug("stale_services_removed", count=len(stale_services), threshold_seconds=threshold_seconds)
        return len(stale_services)

    async def is_service_healthy(self, service_id: str, threshold_seconds: int) -> bool:
        """Check if service is healthy based on last heartbeat."""
        service = self._services.get(service_id)
        if not service:
            logger.debug("service_not_found_for_health_check", service_id=service_id)
            return False

        now = datetime.now(UTC)
        threshold_time = now - timedelta(seconds=threshold_seconds)
        is_healthy = service.last_seen >= threshold_time

        logger.debug(
            "service_health_checked",
            service_id=service_id,
            is_healthy=is_healthy,
            last_seen=service.last_seen,
        )
        return is_healthy

    async def get_service_count(self) -> int:
        """Get total count of registered services."""
        count = len(self._services)
        logger.debug("service_count_retrieved", count=count)
        return count
