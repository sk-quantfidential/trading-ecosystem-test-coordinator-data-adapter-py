"""Stub test runs repository implementation."""
import structlog
from datetime import datetime, UTC
from typing import List, Optional
from test_coordinator_data_adapter.interfaces import TestRunsRepository
from test_coordinator_data_adapter.models import TestRun, RunStatus

logger = structlog.get_logger(__name__)


class StubTestRunsRepository(TestRunsRepository):
    """In-memory stub implementation of test runs repository."""

    def __init__(self):
        self._runs: dict[str, TestRun] = {}
        logger.info("stub_test_runs_repository_initialized", storage="in-memory")

    async def create(self, run: TestRun) -> TestRun:
        """Create a new test run."""
        self._runs[run.run_id] = run
        logger.debug("test_run_created", run_id=run.run_id, scenario_id=run.scenario_id)
        return run

    async def get_by_id(self, run_id: str) -> Optional[TestRun]:
        """Get test run by ID."""
        run = self._runs.get(run_id)
        logger.debug("test_run_retrieved", run_id=run_id, found=run is not None)
        return run

    async def update(self, run: TestRun) -> TestRun:
        """Update existing test run."""
        if run.run_id not in self._runs:
            logger.warning("test_run_not_found_for_update", run_id=run.run_id)
            raise ValueError(f"TestRun {run.run_id} not found")
        self._runs[run.run_id] = run
        logger.debug("test_run_updated", run_id=run.run_id, status=run.status.value)
        return run

    async def get_by_scenario(self, scenario_id: str) -> List[TestRun]:
        """Get all runs for a scenario."""
        result = [r for r in self._runs.values() if r.scenario_id == scenario_id]
        logger.debug("test_runs_retrieved_by_scenario", scenario_id=scenario_id, count=len(result))
        return result

    async def get_by_status(self, status: RunStatus) -> List[TestRun]:
        """Get runs by status."""
        result = [r for r in self._runs.values() if r.status == status]
        logger.debug("test_runs_retrieved_by_status", status=status.value, count=len(result))
        return result

    async def update_status(self, run_id: str, status: RunStatus) -> TestRun:
        """Update run status."""
        run = self._runs.get(run_id)
        if not run:
            logger.warning("test_run_not_found_for_status_update", run_id=run_id)
            raise ValueError(f"TestRun {run_id} not found")
        run.status = status
        logger.debug("test_run_status_updated", run_id=run_id, status=status.value)
        return run

    async def start_run(self, run_id: str) -> TestRun:
        """Start a test run."""
        run = self._runs.get(run_id)
        if not run:
            logger.warning("test_run_not_found_for_start", run_id=run_id)
            raise ValueError(f"TestRun {run_id} not found")
        run.status = RunStatus.RUNNING
        run.started_at = datetime.now(UTC)
        logger.debug("test_run_started", run_id=run_id)
        return run

    async def complete_run(self, run_id: str, status: RunStatus, exit_code: Optional[int] = None) -> TestRun:
        """Complete a test run."""
        run = self._runs.get(run_id)
        if not run:
            logger.warning("test_run_not_found_for_completion", run_id=run_id)
            raise ValueError(f"TestRun {run_id} not found")
        run.status = status
        run.completed_at = datetime.now(UTC)
        run.exit_code = exit_code
        if run.started_at:
            run.duration_ms = int((run.completed_at - run.started_at).total_seconds() * 1000)
        logger.debug("test_run_completed", run_id=run_id, status=status.value, duration_ms=run.duration_ms)
        return run

    async def get_recent_runs(self, limit: int = 10) -> List[TestRun]:
        """Get most recent test runs."""
        sorted_runs = sorted(
            self._runs.values(),
            key=lambda r: r.started_at or datetime.min.replace(tzinfo=UTC),
            reverse=True,
        )
        result = sorted_runs[:limit]
        logger.debug("recent_test_runs_retrieved", count=len(result))
        return result

    async def get_failed_runs(self, limit: int = 10) -> List[TestRun]:
        """Get recent failed runs."""
        failed_runs = [r for r in self._runs.values() if r.status == RunStatus.FAILED]
        sorted_runs = sorted(
            failed_runs,
            key=lambda r: r.completed_at or datetime.min.replace(tzinfo=UTC),
            reverse=True,
        )
        result = sorted_runs[:limit]
        logger.debug("failed_test_runs_retrieved", count=len(result))
        return result

    async def delete(self, run_id: str) -> bool:
        """Delete test run by ID."""
        if run_id in self._runs:
            del self._runs[run_id]
            logger.debug("test_run_deleted", run_id=run_id)
            return True
        logger.warning("test_run_not_found_for_delete", run_id=run_id)
        return False

    async def record_completion(self, run_id: str, exit_code: int, duration_ms: int) -> TestRun:
        """Record run completion with metrics."""
        run = self._runs.get(run_id)
        if not run:
            logger.warning("test_run_not_found_for_completion", run_id=run_id)
            raise ValueError(f"TestRun {run_id} not found")
        run.completed_at = datetime.now(UTC)
        run.exit_code = exit_code
        run.duration_ms = duration_ms
        # Determine status from exit code
        run.status = RunStatus.PASSED if exit_code == 0 else RunStatus.FAILED
        logger.debug("test_run_completion_recorded", run_id=run_id, status=run.status.value, duration_ms=duration_ms)
        return run

    async def get_runs_by_date_range(self, start: datetime, end: datetime) -> List[TestRun]:
        """Get runs within date range."""
        result = [
            r for r in self._runs.values()
            if r.started_at and start <= r.started_at <= end
        ]
        logger.debug("test_runs_retrieved_by_date_range", count=len(result))
        return result

    async def calculate_pass_rate(self, scenario_id: str) -> float:
        """Calculate pass rate for a scenario."""
        runs = [r for r in self._runs.values() if r.scenario_id == scenario_id]
        if not runs:
            return 0.0
        passed = sum(1 for r in runs if r.status == RunStatus.PASSED)
        pass_rate = passed / len(runs)
        logger.debug("pass_rate_calculated", scenario_id=scenario_id, rate=pass_rate)
        return pass_rate

    async def get_average_duration(self, scenario_id: str) -> float:
        """Get average duration for scenario runs."""
        runs = [r for r in self._runs.values() if r.scenario_id == scenario_id and r.duration_ms is not None]
        if not runs:
            return 0.0
        avg_duration = sum(r.duration_ms for r in runs) / len(runs)
        logger.debug("average_duration_calculated", scenario_id=scenario_id, avg_ms=avg_duration)
        return avg_duration
