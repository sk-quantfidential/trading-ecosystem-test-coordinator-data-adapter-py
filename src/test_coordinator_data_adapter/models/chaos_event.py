"""ChaosEvent domain model - chaos injection tracking."""
from datetime import datetime, UTC
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of chaos events that can be injected."""
    SERVICE_RESTART = "service_restart"
    SERVICE_KILL = "service_kill"
    NETWORK_PARTITION = "network_partition"
    NETWORK_LATENCY = "network_latency"
    NETWORK_PACKET_LOSS = "network_packet_loss"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_IO_STRESS = "disk_io_stress"
    CLOCK_SKEW = "clock_skew"


class EventStatus(str, Enum):
    """Chaos event lifecycle status."""
    PENDING = "pending"
    INJECTED = "injected"
    IN_PROGRESS = "in_progress"
    RECOVERED = "recovered"
    FAILED = "failed"


class ChaosEvent(BaseModel):
    """Chaos injection event with recovery metrics."""

    event_id: str = Field(..., description="Unique chaos event identifier")
    run_id: str = Field(..., description="Test run this event belongs to")

    # Event details
    event_type: EventType = Field(..., description="Type of chaos being injected")
    target_service: str = Field(..., description="Service being targeted by chaos")
    parameters: Dict[str, Any] = Field(..., description="Chaos event parameters")

    # Timing
    injected_at: datetime = Field(..., description="When chaos was injected")
    duration_ms: Optional[int] = Field(None, description="How long chaos lasted")

    # Recovery
    status: EventStatus = Field(..., description="Current event status")
    recovery_time_ms: Optional[int] = Field(None, description="Time to recover from chaos")

    # Audit
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"json_schema_extra": {"example": {
        "event_id": "chaos_001",
        "run_id": "run_001",
        "event_type": "service_restart",
        "target_service": "trading-engine",
        "parameters": {"graceful": True, "delay_seconds": 5},
        "injected_at": "2025-10-06T10:01:00Z",
        "status": "recovered",
        "recovery_time_ms": 2500
    }}}
