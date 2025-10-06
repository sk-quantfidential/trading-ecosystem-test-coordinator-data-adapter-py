"""Scenarios repository interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from test_coordinator_data_adapter.models import Scenario, ScenarioType, ScenarioStatus


class ScenariosRepository(ABC):
    """Abstract repository for scenario operations."""

    @abstractmethod
    async def create(self, scenario: Scenario) -> Scenario:
        """Create a new scenario."""
        pass

    @abstractmethod
    async def get_by_id(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID."""
        pass

    @abstractmethod
    async def update(self, scenario: Scenario) -> Scenario:
        """Update existing scenario."""
        pass

    @abstractmethod
    async def delete(self, scenario_id: str) -> bool:
        """Delete scenario by ID."""
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Scenario]:
        """List all scenarios with pagination."""
        pass

    @abstractmethod
    async def get_by_type(self, scenario_type: ScenarioType) -> List[Scenario]:
        """Get scenarios by type."""
        pass

    @abstractmethod
    async def get_by_status(self, status: ScenarioStatus) -> List[Scenario]:
        """Get scenarios by status."""
        pass

    @abstractmethod
    async def update_status(self, scenario_id: str, status: ScenarioStatus) -> Scenario:
        """Update scenario status."""
        pass

    @abstractmethod
    async def search_by_tag(self, tag: str) -> List[Scenario]:
        """Search scenarios by tag."""
        pass

    @abstractmethod
    async def get_active_scenarios(self) -> List[Scenario]:
        """Get all active scenarios."""
        pass
