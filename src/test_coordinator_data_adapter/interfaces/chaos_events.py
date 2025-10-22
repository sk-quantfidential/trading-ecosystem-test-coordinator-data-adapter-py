"""Chaos events repository interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from test_coordinator_data_adapter.models import ChaosEvent, EventType, EventStatus


class ChaosEventsRepository(ABC):
    """Abstract repository for chaos event operations."""

    @abstractmethod
    async def create(self, event: ChaosEvent) -> ChaosEvent:
        """Create a new chaos event."""
        pass

    @abstractmethod
    async def get_by_id(self, event_id: str) -> Optional[ChaosEvent]:
        """Get chaos event by ID."""
        pass

    @abstractmethod
    async def update(self, event: ChaosEvent) -> ChaosEvent:
        """Update existing chaos event."""
        pass

    @abstractmethod
    async def get_by_run(self, run_id: str) -> List[ChaosEvent]:
        """Get all events for a test run."""
        pass

    @abstractmethod
    async def get_by_type(self, event_type: EventType) -> List[ChaosEvent]:
        """Get events by type."""
        pass

    @abstractmethod
    async def get_by_service(self, service_name: str) -> List[ChaosEvent]:
        """Get events by target service."""
        pass

    @abstractmethod
    async def update_status(self, event_id: str, status: EventStatus) -> ChaosEvent:
        """Update event status."""
        pass

    @abstractmethod
    async def record_recovery(self, event_id: str, recovery_time_ms: int) -> ChaosEvent:
        """Record event recovery time."""
        pass

    @abstractmethod
    async def get_active_events(self) -> List[ChaosEvent]:
        """Get all active/in-progress chaos events."""
        pass

    @abstractmethod
    async def calculate_average_recovery_time(self, event_type: EventType) -> float:
        """Calculate average recovery time for event type."""
        pass
