"""Test results repository interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from test_coordinator_data_adapter.models import TestResult, ResultStatus, AssertionType


class TestResultsRepository(ABC):
    """Abstract repository for test result operations."""

    @abstractmethod
    async def create(self, result: TestResult) -> TestResult:
        """Create a new test result."""
        pass

    @abstractmethod
    async def get_by_id(self, result_id: str) -> Optional[TestResult]:
        """Get test result by ID."""
        pass

    @abstractmethod
    async def get_by_run(self, run_id: str) -> List[TestResult]:
        """Get all results for a test run."""
        pass

    @abstractmethod
    async def get_by_assertion_type(self, assertion_type: AssertionType) -> List[TestResult]:
        """Get results by assertion type."""
        pass

    @abstractmethod
    async def get_by_status(self, status: ResultStatus) -> List[TestResult]:
        """Get results by status."""
        pass

    @abstractmethod
    async def get_failed_results(self, run_id: str) -> List[TestResult]:
        """Get all failed results for a run."""
        pass

    @abstractmethod
    async def get_by_correlation_id(self, correlation_id: str) -> List[TestResult]:
        """Get results by audit correlation ID."""
        pass

    @abstractmethod
    async def calculate_pass_rate(self, run_id: str) -> float:
        """Calculate pass rate for a test run."""
        pass

    @abstractmethod
    async def count_by_status(self, run_id: str, status: ResultStatus) -> int:
        """Count results by status for a run."""
        pass

    @abstractmethod
    async def get_assertion_statistics(self, assertion_type: AssertionType) -> dict:
        """Get statistics for an assertion type."""
        pass

    @abstractmethod
    async def bulk_create(self, results: List[TestResult]) -> List[TestResult]:
        """Bulk create test results."""
        pass
