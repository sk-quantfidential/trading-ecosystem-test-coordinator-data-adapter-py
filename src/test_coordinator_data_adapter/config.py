"""Configuration for test coordinator data adapter."""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdapterConfig(BaseSettings):
    """Configuration for test coordinator data adapter.

    Environment variables with TEST_COORDINATOR_ADAPTER_ prefix override defaults.
    """

    model_config = SettingsConfigDict(
        env_prefix="TEST_COORDINATOR_ADAPTER_",
        case_sensitive=False,
        extra="ignore",
    )

    # PostgreSQL connection
    postgres_url: str = "postgresql+asyncpg://test_coordinator_adapter:test-pass@localhost:5432/trading_ecosystem"
    postgres_pool_size: int = 10
    postgres_max_overflow: int = 20
    postgres_pool_timeout: int = 30
    postgres_pool_recycle: int = 3600

    # Redis connection
    redis_url: str = "redis://localhost:6379/0"
    redis_pool_size: int = 10
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5

    # Cache TTL settings
    cache_ttl_default: int = 300
    cache_ttl_scenarios: int = 600
    cache_ttl_test_runs: int = 300
    cache_ttl_results: int = 180

    # Service identity
    service_name: str = "test-coordinator"
    service_version: str = "0.1.0"

    # Service discovery
    heartbeat_interval: int = 30
    stale_service_threshold: int = 300

    # Query settings
    batch_size: int = 100
    query_timeout: int = 30

    # Data retention (days)
    test_runs_retention_days: int = 90
    scenarios_retention_days: int = 365
    chaos_events_retention_days: int = 90
    test_results_retention_days: int = 90

    # Logging
    log_level: str = "INFO"
    log_sql_queries: bool = False

    # Health check timeout
    health_check_timeout: int = 5
