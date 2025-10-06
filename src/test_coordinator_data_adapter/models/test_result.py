"""TestResult domain model - test assertion results."""
from datetime import datetime, UTC
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AssertionType(str, Enum):
    """Types of test assertions."""
    SERVICE_HEALTH = "service_health"
    RESPONSE_TIME = "response_time"
    DATA_CONSISTENCY = "data_consistency"
    AUDIT_TRAIL = "audit_trail"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    AVAILABILITY = "availability"
    RECOVERY_TIME = "recovery_time"


class ResultStatus(str, Enum):
    """Assertion result status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestResult(BaseModel):
    """Test assertion result with verification details."""

    result_id: str = Field(..., description="Unique result identifier")
    run_id: str = Field(..., description="Test run this result belongs to")

    # Assertion details
    assertion_type: AssertionType = Field(..., description="Type of assertion")
    expected_value: str = Field(..., description="Expected outcome")
    actual_value: str = Field(..., description="Actual outcome")

    # Result
    status: ResultStatus = Field(..., description="Assertion result status")
    verification_time: datetime = Field(..., description="When assertion was verified")

    # Error details
    error_details: Optional[str] = Field(None, description="Detailed error information if failed")

    # Correlation
    correlation_id: Optional[str] = Field(None, description="Correlation ID linking to audit trail")

    # Audit
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"json_schema_extra": {"example": {
        "result_id": "result_001",
        "run_id": "run_001",
        "assertion_type": "service_health",
        "expected_value": "healthy",
        "actual_value": "healthy",
        "status": "passed",
        "verification_time": "2025-10-06T10:05:00Z",
        "correlation_id": "audit_trace_123"
    }}}
