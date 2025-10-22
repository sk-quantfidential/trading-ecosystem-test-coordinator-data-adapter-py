"""Stub chaos events repository implementation."""
import structlog
from typing import List, Optional
from test_coordinator_data_adapter.interfaces import ChaosEventsRepository
from test_coordinator_data_adapter.models import ChaosEvent, EventType, EventStatus

logger = structlog.get_logger(__name__)


class StubChaosEventsRepository(ChaosEventsRepository):
    """In-memory stub implementation of chaos events repository."""

    def __init__(self):
        self._events: dict[str, ChaosEvent] = {}
        logger.info("stub_chaos_events_repository_initialized", storage="in-memory")

    async def create(self, event: ChaosEvent) -> ChaosEvent:
        """Create a new chaos event."""
        self._events[event.event_id] = event
        logger.debug(
            "chaos_event_created",
            event_id=event.event_id,
            event_type=event.event_type.value,
            target_service=event.target_service,
        )
        return event

    async def get_by_id(self, event_id: str) -> Optional[ChaosEvent]:
        """Get chaos event by ID."""
        event = self._events.get(event_id)
        logger.debug("chaos_event_retrieved", event_id=event_id, found=event is not None)
        return event

    async def update(self, event: ChaosEvent) -> ChaosEvent:
        """Update existing chaos event."""
        if event.event_id not in self._events:
            logger.warning("chaos_event_not_found_for_update", event_id=event.event_id)
            raise ValueError(f"ChaosEvent {event.event_id} not found")
        self._events[event.event_id] = event
        logger.debug("chaos_event_updated", event_id=event.event_id, status=event.status.value)
        return event

    async def get_by_run(self, run_id: str) -> List[ChaosEvent]:
        """Get all events for a test run."""
        result = [e for e in self._events.values() if e.run_id == run_id]
        logger.debug("chaos_events_retrieved_by_run", run_id=run_id, count=len(result))
        return result

    async def get_by_type(self, event_type: EventType) -> List[ChaosEvent]:
        """Get events by type."""
        result = [e for e in self._events.values() if e.event_type == event_type]
        logger.debug("chaos_events_retrieved_by_type", event_type=event_type.value, count=len(result))
        return result

    async def get_by_service(self, service_name: str) -> List[ChaosEvent]:
        """Get events by target service."""
        result = [e for e in self._events.values() if e.target_service == service_name]
        logger.debug("chaos_events_retrieved_by_service", service_name=service_name, count=len(result))
        return result

    async def update_status(self, event_id: str, status: EventStatus) -> ChaosEvent:
        """Update event status."""
        event = self._events.get(event_id)
        if not event:
            logger.warning("chaos_event_not_found_for_status_update", event_id=event_id)
            raise ValueError(f"ChaosEvent {event_id} not found")
        event.status = status
        logger.debug("chaos_event_status_updated", event_id=event_id, status=status.value)
        return event

    async def record_recovery(self, event_id: str, recovery_time_ms: int) -> ChaosEvent:
        """Record event recovery time."""
        event = self._events.get(event_id)
        if not event:
            logger.warning("chaos_event_not_found_for_recovery", event_id=event_id)
            raise ValueError(f"ChaosEvent {event_id} not found")
        event.recovery_time_ms = recovery_time_ms
        event.status = EventStatus.RECOVERED
        logger.debug("chaos_event_recovery_recorded", event_id=event_id, recovery_ms=recovery_time_ms)
        return event

    async def get_active_events(self) -> List[ChaosEvent]:
        """Get all active/in-progress chaos events."""
        result = [
            e
            for e in self._events.values()
            if e.status in [EventStatus.INJECTED, EventStatus.IN_PROGRESS]
        ]
        logger.debug("active_chaos_events_retrieved", count=len(result))
        return result

    async def calculate_average_recovery_time(self, event_type: EventType) -> float:
        """Calculate average recovery time for event type."""
        events = [
            e
            for e in self._events.values()
            if e.event_type == event_type and e.recovery_time_ms is not None
        ]
        if not events:
            return 0.0
        avg_recovery = sum(e.recovery_time_ms for e in events) / len(events)
        logger.debug(
            "average_recovery_time_calculated",
            event_type=event_type.value,
            avg_ms=avg_recovery,
        )
        return avg_recovery
