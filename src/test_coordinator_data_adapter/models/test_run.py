"""TestRun domain model - test execution tracking."""
from datetime import datetime, UTC
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    """Test run execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TestRun(BaseModel):
    """Test execution run with results and metrics."""

    run_id: str = Field(..., description="Unique test run identifier")
    scenario_id: str = Field(..., description="Scenario being executed")

    # Execution status
    status: RunStatus = Field(..., description="Current run status")

    # Timing
    started_at: Optional[datetime] = Field(None, description="When test run started")
    completed_at: Optional[datetime] = Field(None, description="When test run completed")
    duration_ms: Optional[int] = Field(None, description="Total execution duration in milliseconds")

    # Configuration
    configuration_snapshot: Dict[str, Any] = Field(..., description="Snapshot of scenario config at runtime")
    test_environment: Optional[str] = Field(None, description="Environment where test ran (dev/staging/prod)")

    # Results
    exit_code: Optional[int] = Field(None, description="Test run exit code (0=success)")
    error_message: Optional[str] = Field(None, description="Error message if run failed")

    # Audit
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"json_schema_extra": {"example": {
        "run_id": "run_001",
        "scenario_id": "scen_001",
        "status": "passed",
        "started_at": "2025-10-06T10:00:00Z",
        "completed_at": "2025-10-06T10:05:00Z",
        "duration_ms": 300000,
        "configuration_snapshot": {"version": "1.0"},
        "exit_code": 0
    }}}
