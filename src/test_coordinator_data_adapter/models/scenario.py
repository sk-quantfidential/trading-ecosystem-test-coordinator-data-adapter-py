"""Scenario domain model - test scenario definitions."""
from datetime import datetime, UTC
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    """Scenario type classifications."""
    SERVICE_RESTART = "service_restart"
    NETWORK_PARTITION = "network_partition"
    NETWORK_LATENCY = "network_latency"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_CORRUPTION = "data_corruption"
    COMBINED = "combined"


class ScenarioStatus(str, Enum):
    """Scenario lifecycle status."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class Scenario(BaseModel):
    """Test scenario definition with YAML configuration."""

    scenario_id: str = Field(..., description="Unique scenario identifier")
    name: str = Field(..., description="Human-readable scenario name")
    description: Optional[str] = Field(None, description="Detailed scenario description")

    # Scenario classification
    scenario_type: ScenarioType = Field(..., description="Type of chaos scenario")
    status: ScenarioStatus = Field(default=ScenarioStatus.DRAFT, description="Scenario status")

    # Configuration
    configuration: Dict[str, Any] = Field(..., description="YAML/JSON scenario configuration")
    services_under_test: List[str] = Field(default_factory=list, description="Services being tested")
    expected_outcomes: List[str] = Field(default_factory=list, description="Expected scenario outcomes")

    # Metadata
    created_by: Optional[str] = Field(None, description="User who created scenario")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tags: List[str] = Field(default_factory=list, description="Scenario tags for categorization")

    model_config = {"json_schema_extra": {"example": {
        "scenario_id": "scen_001",
        "name": "Trading Engine Restart Test",
        "description": "Validates system behavior during trading engine restart",
        "scenario_type": "service_restart",
        "status": "active",
        "configuration": {"target_service": "trading-engine", "graceful": True},
        "services_under_test": ["trading-engine", "risk-monitor"],
        "expected_outcomes": ["service_recovers", "no_data_loss"],
        "created_by": "test_engineer"
    }}}
