"""Test Coordinator Data Adapter - Data persistence layer for test coordinator service."""

__version__ = "0.1.0"

from test_coordinator_data_adapter.config import AdapterConfig
from test_coordinator_data_adapter.factory import AdapterFactory

__all__ = [
    "AdapterConfig",
    "AdapterFactory",
]
