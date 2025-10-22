"""Unit tests for adapter factory."""
import pytest
from test_coordinator_data_adapter.factory import AdapterFactory
from test_coordinator_data_adapter.config import AdapterConfig
from test_coordinator_data_adapter.adapters.stub import (
    StubScenariosRepository,
    StubTestRunsRepository,
    StubChaosEventsRepository,
    StubTestResultsRepository,
    StubServiceDiscoveryRepository,
    StubCacheRepository,
)


@pytest.mark.asyncio
class TestAdapterFactory:
    """Test adapter factory functionality."""

    async def test_factory_creation_with_default_config(self):
        """GIVEN no configuration
        WHEN creating a factory
        THEN factory is created with default configuration."""
        # When
        factory = AdapterFactory()

        # Then
        assert factory.config is not None
        assert isinstance(factory.config, AdapterConfig)
        assert not factory._is_initialized

    async def test_factory_creation_with_custom_config(self):
        """GIVEN custom configuration
        WHEN creating a factory
        THEN factory uses custom configuration."""
        # Given
        config = AdapterConfig(
            postgres_url="postgresql+asyncpg://custom:pass@host:5432/db",
            redis_url="redis://custom-host:6380/1",
        )

        # When
        factory = AdapterFactory(config)

        # Then
        assert factory.config == config
        assert factory.config.postgres_url == "postgresql+asyncpg://custom:pass@host:5432/db"
        assert factory.config.redis_url == "redis://custom-host:6380/1"

    async def test_get_repositories_without_initialization(self):
        """GIVEN an uninitialized factory
        WHEN getting repositories
        THEN stub repositories are returned."""
        # Given
        factory = AdapterFactory()

        # When
        scenarios = factory.get_scenarios_repository()
        test_runs = factory.get_test_runs_repository()
        chaos_events = factory.get_chaos_events_repository()
        test_results = factory.get_test_results_repository()
        service_discovery = factory.get_service_discovery_repository()
        cache = factory.get_cache_repository()

        # Then
        assert isinstance(scenarios, StubScenariosRepository)
        assert isinstance(test_runs, StubTestRunsRepository)
        assert isinstance(chaos_events, StubChaosEventsRepository)
        assert isinstance(test_results, StubTestResultsRepository)
        assert isinstance(service_discovery, StubServiceDiscoveryRepository)
        assert isinstance(cache, StubCacheRepository)

    async def test_get_repositories_with_use_stub_flag(self):
        """GIVEN a factory with use_stub=True
        WHEN getting repositories
        THEN stub repositories are returned."""
        # Given
        factory = AdapterFactory()

        # When
        scenarios = factory.get_scenarios_repository(use_stub=True)
        test_runs = factory.get_test_runs_repository(use_stub=True)

        # Then
        assert isinstance(scenarios, StubScenariosRepository)
        assert isinstance(test_runs, StubTestRunsRepository)

    async def test_context_manager_initialize_and_cleanup(self):
        """GIVEN a factory as context manager
        WHEN entering and exiting context
        THEN factory initializes and cleans up."""
        # Given
        factory = AdapterFactory()

        # When/Then
        async with factory as f:
            # Should be initialized in context
            assert f._is_initialized
            assert f == factory

        # Should be cleaned up after context
        assert not factory._is_initialized

    async def test_password_masking_in_urls(self):
        """GIVEN URLs with passwords
        WHEN masking passwords
        THEN passwords are hidden."""
        # When
        masked1 = AdapterFactory._mask_password("postgresql://user:secret@localhost:5432/db")
        masked2 = AdapterFactory._mask_password("redis://user:password123@host:6379/0")
        masked3 = AdapterFactory._mask_password("postgresql://user@localhost:5432/db")

        # Then
        assert "***" in masked1
        assert "secret" not in masked1
        assert "***" in masked2
        assert "password123" not in masked2
        # No password to mask
        assert "***" not in masked3
        assert "user@localhost" in masked3

    async def test_health_check_when_not_initialized(self):
        """GIVEN an uninitialized factory
        WHEN performing health check
        THEN returns not initialized status."""
        # Given
        factory = AdapterFactory()

        # When
        health = await factory.health_check()

        # Then
        assert health["factory_initialized"] is False
        assert health["postgres"]["connected"] is False
        assert health["redis"]["connected"] is False

    async def test_get_session_maker_when_not_initialized(self):
        """GIVEN an uninitialized factory
        WHEN getting session maker
        THEN returns None."""
        # Given
        factory = AdapterFactory()

        # When
        session_maker = factory.get_session_maker()

        # Then
        assert session_maker is None

    async def test_get_redis_client_when_not_initialized(self):
        """GIVEN an uninitialized factory
        WHEN getting Redis client
        THEN returns None."""
        # Given
        factory = AdapterFactory()

        # When
        redis_client = factory.get_redis_client()

        # Then
        assert redis_client is None

    async def test_cleanup_when_not_initialized(self):
        """GIVEN an uninitialized factory
        WHEN calling cleanup
        THEN cleanup completes without error."""
        # Given
        factory = AdapterFactory()

        # When/Then - should not raise
        await factory.cleanup()

        # Then
        assert not factory._is_initialized
