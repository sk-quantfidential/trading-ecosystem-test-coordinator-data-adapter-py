"""Repository interfaces for test coordinator data adapter."""

from test_coordinator_data_adapter.interfaces.scenarios import ScenariosRepository
from test_coordinator_data_adapter.interfaces.test_runs import TestRunsRepository
from test_coordinator_data_adapter.interfaces.chaos_events import ChaosEventsRepository
from test_coordinator_data_adapter.interfaces.test_results import TestResultsRepository
from test_coordinator_data_adapter.interfaces.service_discovery import (
    ServiceDiscoveryRepository,
    ServiceInfo,
)
from test_coordinator_data_adapter.interfaces.cache import CacheRepository

__all__ = [
    "ScenariosRepository",
    "TestRunsRepository",
    "ChaosEventsRepository",
    "TestResultsRepository",
    "ServiceDiscoveryRepository",
    "ServiceInfo",
    "CacheRepository",
]
