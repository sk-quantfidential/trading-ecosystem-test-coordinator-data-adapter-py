"""Service discovery repository interface."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ServiceInfo(BaseModel):
    """Service registration information."""
    service_id: str = Field(..., description="Unique service identifier")
    service_name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    host: str = Field(..., description="Service host")
    grpc_port: int = Field(..., description="gRPC port")
    http_port: int = Field(..., description="HTTP port")
    last_seen: datetime = Field(..., description="Last heartbeat timestamp")
    registered_at: datetime = Field(..., description="Registration timestamp")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class ServiceDiscoveryRepository(ABC):
    """Abstract repository for service discovery operations."""

    @abstractmethod
    async def register(self, service: ServiceInfo) -> ServiceInfo:
        """Register a service."""
        pass

    @abstractmethod
    async def deregister(self, service_id: str) -> bool:
        """Deregister a service."""
        pass

    @abstractmethod
    async def get_service_by_id(self, service_id: str) -> Optional[ServiceInfo]:
        """Get service by ID."""
        pass

    @abstractmethod
    async def get_service_by_name(self, service_name: str) -> Optional[ServiceInfo]:
        """Get service by name (returns first matching)."""
        pass

    @abstractmethod
    async def list_services_by_name(self, service_name: str) -> List[ServiceInfo]:
        """List all instances of a service."""
        pass

    @abstractmethod
    async def list_all_services(self) -> List[ServiceInfo]:
        """List all registered services."""
        pass

    @abstractmethod
    async def update_heartbeat(self, service_id: str) -> ServiceInfo:
        """Update service heartbeat timestamp."""
        pass

    @abstractmethod
    async def remove_stale_services(self, threshold_seconds: int) -> int:
        """Remove services not seen within threshold."""
        pass

    @abstractmethod
    async def is_service_healthy(self, service_id: str, threshold_seconds: int) -> bool:
        """Check if service is healthy based on last heartbeat."""
        pass

    @abstractmethod
    async def get_service_count(self) -> int:
        """Get total count of registered services."""
        pass
