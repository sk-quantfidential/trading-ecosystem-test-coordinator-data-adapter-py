"""Test runs repository interface."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from test_coordinator_data_adapter.models import TestRun, RunStatus


class TestRunsRepository(ABC):
    """Abstract repository for test run operations."""

    @abstractmethod
    async def create(self, test_run: TestRun) -> TestRun:
        """Create a new test run."""
        pass

    @abstractmethod
    async def get_by_id(self, run_id: str) -> Optional[TestRun]:
        """Get test run by ID."""
        pass

    @abstractmethod
    async def update(self, test_run: TestRun) -> TestRun:
        """Update existing test run."""
        pass

    @abstractmethod
    async def delete(self, run_id: str) -> bool:
        """Delete test run by ID."""
        pass

    @abstractmethod
    async def get_by_scenario(self, scenario_id: str) -> List[TestRun]:
        """Get all runs for a scenario."""
        pass

    @abstractmethod
    async def get_by_status(self, status: RunStatus) -> List[TestRun]:
        """Get runs by status."""
        pass

    @abstractmethod
    async def update_status(self, run_id: str, status: RunStatus) -> TestRun:
        """Update run status."""
        pass

    @abstractmethod
    async def record_completion(self, run_id: str, exit_code: int, duration_ms: int) -> TestRun:
        """Record run completion with metrics."""
        pass

    @abstractmethod
    async def get_recent_runs(self, limit: int = 10) -> List[TestRun]:
        """Get most recent test runs."""
        pass

    @abstractmethod
    async def get_runs_by_date_range(self, start: datetime, end: datetime) -> List[TestRun]:
        """Get runs within date range."""
        pass

    @abstractmethod
    async def calculate_pass_rate(self, scenario_id: str) -> float:
        """Calculate pass rate for a scenario."""
        pass

    @abstractmethod
    async def get_average_duration(self, scenario_id: str) -> float:
        """Get average duration for a scenario."""
        pass
