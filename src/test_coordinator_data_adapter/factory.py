"""Factory for creating repository instances with connection management."""
import structlog
from typing import Optional
from redis.asyncio import Redis, ConnectionPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from test_coordinator_data_adapter.config import AdapterConfig
from test_coordinator_data_adapter.interfaces import (
    ScenariosRepository,
    TestRunsRepository,
    ChaosEventsRepository,
    TestResultsRepository,
    ServiceDiscoveryRepository,
    CacheRepository,
)
from test_coordinator_data_adapter.adapters.stub import (
    StubScenariosRepository,
    StubTestRunsRepository,
    StubChaosEventsRepository,
    StubTestResultsRepository,
    StubServiceDiscoveryRepository,
    StubCacheRepository,
)

logger = structlog.get_logger(__name__)


class AdapterFactory:
    """Factory for creating test coordinator data adapter repository instances."""

    def __init__(self, config: Optional[AdapterConfig] = None):
        """Initialize factory with configuration.

        Args:
            config: Adapter configuration. If None, uses default configuration.
        """
        self.config = config or AdapterConfig()
        self._postgres_engine: Optional[AsyncEngine] = None
        self._session_maker: Optional[async_sessionmaker[AsyncSession]] = None
        self._redis_pool: Optional[ConnectionPool] = None
        self._redis_client: Optional[Redis] = None
        self._is_initialized = False
        logger.info(
            "adapter_factory_created",
            postgres_url=self._mask_password(self.config.postgres_url),
            redis_url=self._mask_password(self.config.redis_url),
        )

    @staticmethod
    def _mask_password(url: str) -> str:
        """Mask password in URL for logging."""
        try:
            from urllib.parse import urlparse, urlunparse

            parsed = urlparse(url)
            if parsed.password:
                netloc = f"{parsed.username}:***@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                masked = parsed._replace(netloc=netloc)
                return urlunparse(masked)
            return url
        except Exception:
            return url

    async def initialize(self) -> None:
        """Initialize database and cache connections."""
        if self._is_initialized:
            logger.warning("factory_already_initialized")
            return

        try:
            # Initialize PostgreSQL engine
            self._postgres_engine = create_async_engine(
                self.config.postgres_url,
                pool_size=self.config.postgres_pool_size,
                max_overflow=self.config.postgres_max_overflow,
                pool_timeout=self.config.postgres_pool_timeout,
                pool_recycle=self.config.postgres_pool_recycle,
                echo=self.config.log_sql_queries,
            )

            # Create session maker
            self._session_maker = async_sessionmaker(
                self._postgres_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            # Initialize Redis connection pool
            self._redis_pool = ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=self.config.redis_pool_size,
                socket_timeout=self.config.redis_socket_timeout,
                socket_connect_timeout=self.config.redis_socket_connect_timeout,
                decode_responses=True,
            )

            self._redis_client = Redis(connection_pool=self._redis_pool)

            self._is_initialized = True
            logger.info(
                "factory_initialized",
                postgres_pool_size=self.config.postgres_pool_size,
                redis_pool_size=self.config.redis_pool_size,
            )

        except Exception as e:
            logger.error("factory_initialization_failed", error=str(e), error_type=type(e).__name__)
            raise

    async def cleanup(self) -> None:
        """Cleanup database and cache connections."""
        if not self._is_initialized:
            return

        try:
            # Close Redis connection
            if self._redis_client:
                await self._redis_client.aclose()
                self._redis_client = None
                logger.debug("redis_client_closed")

            # Close Redis pool
            if self._redis_pool:
                await self._redis_pool.aclose()
                self._redis_pool = None
                logger.debug("redis_pool_closed")

            # Dispose PostgreSQL engine
            if self._postgres_engine:
                await self._postgres_engine.dispose()
                self._postgres_engine = None
                logger.debug("postgres_engine_disposed")

            self._session_maker = None
            self._is_initialized = False
            logger.info("factory_cleanup_complete")

        except Exception as e:
            logger.error("factory_cleanup_failed", error=str(e), error_type=type(e).__name__)
            raise

    async def health_check(self) -> dict:
        """Check health of database and cache connections.

        Returns:
            Dictionary with health status of each component.
        """
        health = {
            "factory_initialized": self._is_initialized,
            "postgres": {"connected": False, "error": None},
            "redis": {"connected": False, "error": None},
        }

        # Check PostgreSQL connection
        if self._postgres_engine:
            try:
                async with self._postgres_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                health["postgres"]["connected"] = True
            except Exception as e:
                health["postgres"]["error"] = str(e)
                logger.warning("postgres_health_check_failed", error=str(e))

        # Check Redis connection
        if self._redis_client:
            try:
                await self._redis_client.ping()
                health["redis"]["connected"] = True
            except Exception as e:
                health["redis"]["error"] = str(e)
                logger.warning("redis_health_check_failed", error=str(e))

        logger.debug("health_check_completed", **health)
        return health

    def get_session_maker(self) -> Optional[async_sessionmaker[AsyncSession]]:
        """Get SQLAlchemy session maker.

        Returns:
            Session maker if initialized, None otherwise.
        """
        return self._session_maker

    def get_redis_client(self) -> Optional[Redis]:
        """Get Redis client.

        Returns:
            Redis client if initialized, None otherwise.
        """
        return self._redis_client

    # Repository factory methods

    def get_scenarios_repository(self, use_stub: bool = False) -> ScenariosRepository:
        """Get scenarios repository.

        Args:
            use_stub: If True, return stub implementation. If False and not initialized,
                     falls back to stub with warning.

        Returns:
            ScenariosRepository instance.
        """
        if use_stub or not self._is_initialized:
            if not use_stub and not self._is_initialized:
                logger.warning("scenarios_repository_fallback_to_stub", reason="factory_not_initialized")
            return StubScenariosRepository()

        # TODO: Implement PostgreSQL repository when ready
        logger.warning("scenarios_repository_postgresql_not_implemented", fallback="stub")
        return StubScenariosRepository()

    def get_test_runs_repository(self, use_stub: bool = False) -> TestRunsRepository:
        """Get test runs repository.

        Args:
            use_stub: If True, return stub implementation. If False and not initialized,
                     falls back to stub with warning.

        Returns:
            TestRunsRepository instance.
        """
        if use_stub or not self._is_initialized:
            if not use_stub and not self._is_initialized:
                logger.warning("test_runs_repository_fallback_to_stub", reason="factory_not_initialized")
            return StubTestRunsRepository()

        # TODO: Implement PostgreSQL repository when ready
        logger.warning("test_runs_repository_postgresql_not_implemented", fallback="stub")
        return StubTestRunsRepository()

    def get_chaos_events_repository(self, use_stub: bool = False) -> ChaosEventsRepository:
        """Get chaos events repository.

        Args:
            use_stub: If True, return stub implementation. If False and not initialized,
                     falls back to stub with warning.

        Returns:
            ChaosEventsRepository instance.
        """
        if use_stub or not self._is_initialized:
            if not use_stub and not self._is_initialized:
                logger.warning("chaos_events_repository_fallback_to_stub", reason="factory_not_initialized")
            return StubChaosEventsRepository()

        # TODO: Implement PostgreSQL repository when ready
        logger.warning("chaos_events_repository_postgresql_not_implemented", fallback="stub")
        return StubChaosEventsRepository()

    def get_test_results_repository(self, use_stub: bool = False) -> TestResultsRepository:
        """Get test results repository.

        Args:
            use_stub: If True, return stub implementation. If False and not initialized,
                     falls back to stub with warning.

        Returns:
            TestResultsRepository instance.
        """
        if use_stub or not self._is_initialized:
            if not use_stub and not self._is_initialized:
                logger.warning("test_results_repository_fallback_to_stub", reason="factory_not_initialized")
            return StubTestResultsRepository()

        # TODO: Implement PostgreSQL repository when ready
        logger.warning("test_results_repository_postgresql_not_implemented", fallback="stub")
        return StubTestResultsRepository()

    def get_service_discovery_repository(self, use_stub: bool = False) -> ServiceDiscoveryRepository:
        """Get service discovery repository.

        Args:
            use_stub: If True, return stub implementation. If False and not initialized,
                     falls back to stub with warning.

        Returns:
            ServiceDiscoveryRepository instance.
        """
        if use_stub or not self._is_initialized:
            if not use_stub and not self._is_initialized:
                logger.warning("service_discovery_repository_fallback_to_stub", reason="factory_not_initialized")
            return StubServiceDiscoveryRepository()

        # TODO: Implement Redis repository when ready
        logger.warning("service_discovery_repository_redis_not_implemented", fallback="stub")
        return StubServiceDiscoveryRepository()

    def get_cache_repository(self, use_stub: bool = False) -> CacheRepository:
        """Get cache repository.

        Args:
            use_stub: If True, return stub implementation. If False and not initialized,
                     falls back to stub with warning.

        Returns:
            CacheRepository instance.
        """
        if use_stub or not self._is_initialized:
            if not use_stub and not self._is_initialized:
                logger.warning("cache_repository_fallback_to_stub", reason="factory_not_initialized")
            return StubCacheRepository()

        # TODO: Implement Redis repository when ready
        logger.warning("cache_repository_redis_not_implemented", fallback="stub")
        return StubCacheRepository()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        return False
