"""Stub scenarios repository implementation."""
import structlog
from typing import List, Optional
from test_coordinator_data_adapter.interfaces import ScenariosRepository
from test_coordinator_data_adapter.models import Scenario, ScenarioType, ScenarioStatus

logger = structlog.get_logger(__name__)


class StubScenariosRepository(ScenariosRepository):
    """In-memory stub implementation of scenarios repository."""

    def __init__(self):
        self._scenarios: dict[str, Scenario] = {}
        logger.info("stub_scenarios_repository_initialized", storage="in-memory")

    async def create(self, scenario: Scenario) -> Scenario:
        """Create a new scenario."""
        self._scenarios[scenario.scenario_id] = scenario
        logger.debug(
            "scenario_created",
            scenario_id=scenario.scenario_id,
            scenario_type=scenario.scenario_type.value,
        )
        return scenario

    async def get_by_id(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID."""
        scenario = self._scenarios.get(scenario_id)
        logger.debug("scenario_retrieved", scenario_id=scenario_id, found=scenario is not None)
        return scenario

    async def update(self, scenario: Scenario) -> Scenario:
        """Update existing scenario."""
        if scenario.scenario_id not in self._scenarios:
            logger.warning("scenario_not_found_for_update", scenario_id=scenario.scenario_id)
            raise ValueError(f"Scenario {scenario.scenario_id} not found")
        self._scenarios[scenario.scenario_id] = scenario
        logger.debug("scenario_updated", scenario_id=scenario.scenario_id)
        return scenario

    async def delete(self, scenario_id: str) -> bool:
        """Delete scenario by ID."""
        if scenario_id in self._scenarios:
            del self._scenarios[scenario_id]
            logger.debug("scenario_deleted", scenario_id=scenario_id)
            return True
        logger.warning("scenario_not_found_for_delete", scenario_id=scenario_id)
        return False

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Scenario]:
        """List all scenarios with pagination."""
        all_scenarios = list(self._scenarios.values())
        result = all_scenarios[offset : offset + limit]
        logger.debug("scenarios_listed", total=len(all_scenarios), returned=len(result))
        return result

    async def get_by_type(self, scenario_type: ScenarioType) -> List[Scenario]:
        """Get scenarios by type."""
        result = [s for s in self._scenarios.values() if s.scenario_type == scenario_type]
        logger.debug("scenarios_retrieved_by_type", scenario_type=scenario_type.value, count=len(result))
        return result

    async def get_by_status(self, status: ScenarioStatus) -> List[Scenario]:
        """Get scenarios by status."""
        result = [s for s in self._scenarios.values() if s.status == status]
        logger.debug("scenarios_retrieved_by_status", status=status.value, count=len(result))
        return result

    async def update_status(self, scenario_id: str, status: ScenarioStatus) -> Scenario:
        """Update scenario status."""
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            logger.warning("scenario_not_found_for_status_update", scenario_id=scenario_id)
            raise ValueError(f"Scenario {scenario_id} not found")
        scenario.status = status
        logger.debug("scenario_status_updated", scenario_id=scenario_id, status=status.value)
        return scenario

    async def search_by_tag(self, tag: str) -> List[Scenario]:
        """Search scenarios by tag."""
        result = [s for s in self._scenarios.values() if tag in s.tags]
        logger.debug("scenarios_searched_by_tag", tag=tag, count=len(result))
        return result

    async def get_active_scenarios(self) -> List[Scenario]:
        """Get all active scenarios."""
        result = [s for s in self._scenarios.values() if s.status == ScenarioStatus.ACTIVE]
        logger.debug("active_scenarios_retrieved", count=len(result))
        return result
