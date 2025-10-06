"""Stub test results repository implementation."""
import structlog
from typing import List, Optional
from test_coordinator_data_adapter.models import TestResult, ResultStatus, AssertionType
from test_coordinator_data_adapter.interfaces import TestResultsRepository

logger = structlog.get_logger(__name__)


class StubTestResultsRepository(TestResultsRepository):
    """In-memory stub implementation of test results repository."""

    def __init__(self):
        self._results: dict[str, TestResult] = {}
        logger.info("stub_test_results_repository_initialized", storage="in-memory")

    async def create(self, result: TestResult) -> TestResult:
        """Create a new test result."""
        self._results[result.result_id] = result
        logger.debug(
            "test_result_created",
            result_id=result.result_id,
            run_id=result.run_id,
            assertion_type=result.assertion_type.value,
            status=result.status.value,
        )
        return result

    async def get_by_id(self, result_id: str) -> Optional[TestResult]:
        """Get test result by ID."""
        result = self._results.get(result_id)
        logger.debug("test_result_retrieved", result_id=result_id, found=result is not None)
        return result

    async def get_by_run(self, run_id: str) -> List[TestResult]:
        """Get all results for a test run."""
        results = [r for r in self._results.values() if r.run_id == run_id]
        logger.debug("test_results_retrieved_by_run", run_id=run_id, count=len(results))
        return results

    async def get_by_assertion_type(self, assertion_type: AssertionType) -> List[TestResult]:
        """Get results by assertion type."""
        results = [r for r in self._results.values() if r.assertion_type == assertion_type]
        logger.debug(
            "test_results_retrieved_by_assertion_type",
            assertion_type=assertion_type.value,
            count=len(results),
        )
        return results

    async def get_by_status(self, status: ResultStatus) -> List[TestResult]:
        """Get results by status."""
        results = [r for r in self._results.values() if r.status == status]
        logger.debug("test_results_retrieved_by_status", status=status.value, count=len(results))
        return results

    async def get_failed_results(self, run_id: str) -> List[TestResult]:
        """Get all failed results for a run."""
        results = [
            r for r in self._results.values() if r.run_id == run_id and r.status == ResultStatus.FAILED
        ]
        logger.debug("failed_test_results_retrieved", run_id=run_id, count=len(results))
        return results

    async def get_by_correlation_id(self, correlation_id: str) -> List[TestResult]:
        """Get results by audit correlation ID."""
        results = [r for r in self._results.values() if r.correlation_id == correlation_id]
        logger.debug("test_results_retrieved_by_correlation", correlation_id=correlation_id, count=len(results))
        return results

    async def calculate_pass_rate(self, run_id: str) -> float:
        """Calculate pass rate for a test run."""
        run_results = [r for r in self._results.values() if r.run_id == run_id]
        if not run_results:
            return 0.0
        passed = sum(1 for r in run_results if r.status == ResultStatus.PASSED)
        pass_rate = passed / len(run_results)
        logger.debug("pass_rate_calculated", run_id=run_id, rate=pass_rate)
        return pass_rate

    async def count_by_status(self, run_id: str, status: ResultStatus) -> int:
        """Count results by status for a run."""
        count = sum(
            1 for r in self._results.values() if r.run_id == run_id and r.status == status
        )
        logger.debug("results_counted_by_status", run_id=run_id, status=status.value, count=count)
        return count

    async def get_assertion_statistics(self, assertion_type: AssertionType) -> dict:
        """Get statistics for an assertion type."""
        results = [r for r in self._results.values() if r.assertion_type == assertion_type]
        if not results:
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "pass_rate": 0.0,
            }

        passed = sum(1 for r in results if r.status == ResultStatus.PASSED)
        failed = sum(1 for r in results if r.status == ResultStatus.FAILED)
        skipped = sum(1 for r in results if r.status == ResultStatus.SKIPPED)

        stats = {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": passed / len(results) if results else 0.0,
        }

        logger.debug(
            "assertion_statistics_calculated",
            assertion_type=assertion_type.value,
            **stats,
        )
        return stats

    async def bulk_create(self, results: List[TestResult]) -> List[TestResult]:
        """Bulk create test results."""
        for result in results:
            self._results[result.result_id] = result
        logger.debug("test_results_bulk_created", count=len(results))
        return results
