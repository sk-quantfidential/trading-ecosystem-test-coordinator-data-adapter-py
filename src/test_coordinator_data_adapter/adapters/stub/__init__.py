"""Stub repository implementations for graceful degradation."""

from test_coordinator_data_adapter.adapters.stub.stub_scenarios import StubScenariosRepository
from test_coordinator_data_adapter.adapters.stub.stub_test_runs import StubTestRunsRepository
from test_coordinator_data_adapter.adapters.stub.stub_chaos_events import StubChaosEventsRepository
from test_coordinator_data_adapter.adapters.stub.stub_test_results import StubTestResultsRepository
from test_coordinator_data_adapter.adapters.stub.stub_service_discovery import StubServiceDiscoveryRepository
from test_coordinator_data_adapter.adapters.stub.stub_cache import StubCacheRepository

__all__ = [
    "StubScenariosRepository",
    "StubTestRunsRepository",
    "StubChaosEventsRepository",
    "StubTestResultsRepository",
    "StubServiceDiscoveryRepository",
    "StubCacheRepository",
]
