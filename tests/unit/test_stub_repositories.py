"""Unit tests for stub repository implementations."""
import pytest
from datetime import datetime, UTC
from test_coordinator_data_adapter.adapters.stub import (
    StubScenariosRepository,
    StubTestRunsRepository,
    StubChaosEventsRepository,
    StubTestResultsRepository,
    StubServiceDiscoveryRepository,
    StubCacheRepository,
)
from test_coordinator_data_adapter.models import (
    Scenario,
    ScenarioType,
    ScenarioStatus,
    TestRun,
    RunStatus,
    ChaosEvent,
    EventType,
    EventStatus,
    TestResult,
    AssertionType,
    ResultStatus,
)
from test_coordinator_data_adapter.interfaces import ServiceInfo


@pytest.mark.asyncio
class TestStubScenariosRepository:
    """Test stub scenarios repository."""

    async def test_create_and_retrieve_scenario(self):
        """GIVEN a stub scenarios repository
        WHEN creating and retrieving a scenario
        THEN the scenario is stored and retrieved correctly."""
        # Given
        repo = StubScenariosRepository()
        scenario = Scenario(
            scenario_id="test-001",
            name="Service Restart Test",
            scenario_type=ScenarioType.SERVICE_RESTART,
            status=ScenarioStatus.ACTIVE,
            configuration={"timeout": 30},
            services_under_test=["trading-engine"],
        )

        # When
        created = await repo.create(scenario)
        retrieved = await repo.get_by_id("test-001")

        # Then
        assert created == scenario
        assert retrieved == scenario
        assert retrieved.name == "Service Restart Test"

    async def test_get_by_type(self):
        """GIVEN scenarios of different types
        WHEN filtering by type
        THEN only matching scenarios are returned."""
        # Given
        repo = StubScenariosRepository()
        await repo.create(
            Scenario(
                scenario_id="s1",
                name="Restart",
                scenario_type=ScenarioType.SERVICE_RESTART,
                configuration={},
            )
        )
        await repo.create(
            Scenario(
                scenario_id="s2",
                name="Latency",
                scenario_type=ScenarioType.NETWORK_LATENCY,
                configuration={},
            )
        )

        # When
        results = await repo.get_by_type(ScenarioType.SERVICE_RESTART)

        # Then
        assert len(results) == 1
        assert results[0].scenario_id == "s1"


@pytest.mark.asyncio
class TestStubTestRunsRepository:
    """Test stub test runs repository."""

    async def test_create_and_start_run(self):
        """GIVEN a test run
        WHEN starting the run
        THEN status and timestamp are updated."""
        # Given
        repo = StubTestRunsRepository()
        run = TestRun(
            run_id="run-001",
            scenario_id="test-001",
            status=RunStatus.PENDING,
            configuration_snapshot={"version": "1.0"},
        )
        await repo.create(run)

        # When
        started = await repo.start_run("run-001")

        # Then
        assert started.status == RunStatus.RUNNING
        assert started.started_at is not None

    async def test_complete_run_with_duration(self):
        """GIVEN a running test
        WHEN completing the run
        THEN duration is calculated."""
        # Given
        repo = StubTestRunsRepository()
        run = TestRun(
            run_id="run-001",
            scenario_id="test-001",
            status=RunStatus.PENDING,
            configuration_snapshot={"version": "1.0"},
        )
        await repo.create(run)
        await repo.start_run("run-001")

        # When
        completed = await repo.complete_run("run-001", RunStatus.PASSED, exit_code=0)

        # Then
        assert completed.status == RunStatus.PASSED
        assert completed.completed_at is not None
        assert completed.duration_ms is not None
        assert completed.duration_ms >= 0


@pytest.mark.asyncio
class TestStubChaosEventsRepository:
    """Test stub chaos events repository."""

    async def test_create_and_record_recovery(self):
        """GIVEN a chaos event
        WHEN recording recovery
        THEN recovery time and status are updated."""
        # Given
        repo = StubChaosEventsRepository()
        event = ChaosEvent(
            event_id="evt-001",
            run_id="run-001",
            event_type=EventType.SERVICE_RESTART,
            target_service="trading-engine",
            parameters={"graceful": True},
            injected_at=datetime.now(UTC),
            status=EventStatus.INJECTED,
        )
        await repo.create(event)

        # When
        recovered = await repo.record_recovery("evt-001", recovery_time_ms=1500)

        # Then
        assert recovered.status == EventStatus.RECOVERED
        assert recovered.recovery_time_ms == 1500

    async def test_get_active_events(self):
        """GIVEN events with different statuses
        WHEN getting active events
        THEN only active events are returned."""
        # Given
        repo = StubChaosEventsRepository()
        now = datetime.now(UTC)
        await repo.create(
            ChaosEvent(
                event_id="e1",
                run_id="run-001",
                event_type=EventType.SERVICE_RESTART,
                target_service="svc1",
                parameters={},
                injected_at=now,
                status=EventStatus.INJECTED,
            )
        )
        await repo.create(
            ChaosEvent(
                event_id="e2",
                run_id="run-001",
                event_type=EventType.SERVICE_RESTART,
                target_service="svc2",
                parameters={},
                injected_at=now,
                status=EventStatus.RECOVERED,
            )
        )

        # When
        active = await repo.get_active_events()

        # Then
        assert len(active) == 1
        assert active[0].event_id == "e1"


@pytest.mark.asyncio
class TestStubTestResultsRepository:
    """Test stub test results repository."""

    async def test_calculate_pass_rate(self):
        """GIVEN test results with mixed outcomes
        WHEN calculating pass rate
        THEN correct percentage is returned."""
        # Given
        repo = StubTestResultsRepository()
        now = datetime.now(UTC)
        for i in range(3):
            await repo.create(
                TestResult(
                    result_id=f"res-{i}",
                    run_id="run-001",
                    assertion_type=AssertionType.SERVICE_HEALTH,
                    status=ResultStatus.PASSED,
                    expected_value="healthy",
                    actual_value="healthy",
                    verification_time=now,
                )
            )
        await repo.create(
            TestResult(
                result_id="res-failed",
                run_id="run-001",
                assertion_type=AssertionType.SERVICE_HEALTH,
                status=ResultStatus.FAILED,
                expected_value="healthy",
                actual_value="unhealthy",
                verification_time=now,
            )
        )

        # When
        pass_rate = await repo.calculate_pass_rate("run-001")

        # Then
        assert pass_rate == 0.75  # 3 passed out of 4 total

    async def test_get_assertion_statistics(self):
        """GIVEN test results of specific assertion type
        WHEN getting statistics
        THEN correct counts are returned."""
        # Given
        repo = StubTestResultsRepository()
        now = datetime.now(UTC)
        await repo.create(
            TestResult(
                result_id="r1",
                run_id="run-001",
                assertion_type=AssertionType.RESPONSE_TIME,
                status=ResultStatus.PASSED,
                expected_value="< 100ms",
                actual_value="75ms",
                verification_time=now,
            )
        )
        await repo.create(
            TestResult(
                result_id="r2",
                run_id="run-001",
                assertion_type=AssertionType.RESPONSE_TIME,
                status=ResultStatus.FAILED,
                expected_value="< 100ms",
                actual_value="150ms",
                verification_time=now,
            )
        )

        # When
        stats = await repo.get_assertion_statistics(AssertionType.RESPONSE_TIME)

        # Then
        assert stats["total"] == 2
        assert stats["passed"] == 1
        assert stats["failed"] == 1
        assert stats["pass_rate"] == 0.5


@pytest.mark.asyncio
class TestStubServiceDiscoveryRepository:
    """Test stub service discovery repository."""

    async def test_register_and_retrieve_service(self):
        """GIVEN a service registration
        WHEN registering and retrieving
        THEN service info is stored correctly."""
        # Given
        repo = StubServiceDiscoveryRepository()
        service = ServiceInfo(
            service_id="svc-001",
            service_name="trading-engine",
            version="1.0.0",
            host="localhost",
            grpc_port=50051,
            http_port=8080,
            last_seen=datetime.now(UTC),
            registered_at=datetime.now(UTC),
        )

        # When
        registered = await repo.register(service)
        retrieved = await repo.get_service_by_id("svc-001")

        # Then
        assert registered == service
        assert retrieved == service

    async def test_update_heartbeat(self):
        """GIVEN a registered service
        WHEN updating heartbeat
        THEN last_seen timestamp is updated."""
        # Given
        repo = StubServiceDiscoveryRepository()
        now = datetime.now(UTC)
        service = ServiceInfo(
            service_id="svc-001",
            service_name="test-svc",
            version="1.0.0",
            host="localhost",
            grpc_port=50051,
            http_port=8080,
            last_seen=now,
            registered_at=now,
        )
        await repo.register(service)

        # When
        updated = await repo.update_heartbeat("svc-001")

        # Then
        assert updated.last_seen >= service.last_seen

    async def test_remove_stale_services(self):
        """GIVEN services with old heartbeats
        WHEN removing stale services
        THEN old services are removed."""
        # Given
        repo = StubServiceDiscoveryRepository()
        from datetime import timedelta

        old_time = datetime.now(UTC) - timedelta(seconds=120)
        recent_time = datetime.now(UTC)

        await repo.register(
            ServiceInfo(
                service_id="old-svc",
                service_name="old",
                version="1.0.0",
                host="localhost",
                grpc_port=50051,
                http_port=8080,
                last_seen=old_time,
                registered_at=old_time,
            )
        )
        await repo.register(
            ServiceInfo(
                service_id="new-svc",
                service_name="new",
                version="1.0.0",
                host="localhost",
                grpc_port=50052,
                http_port=8081,
                last_seen=recent_time,
                registered_at=recent_time,
            )
        )

        # When
        removed = await repo.remove_stale_services(threshold_seconds=60)

        # Then
        assert removed == 1
        assert await repo.get_service_by_id("old-svc") is None
        assert await repo.get_service_by_id("new-svc") is not None


@pytest.mark.asyncio
class TestStubCacheRepository:
    """Test stub cache repository."""

    async def test_set_and_get(self):
        """GIVEN a cache repository
        WHEN setting and getting values
        THEN values are stored correctly."""
        # Given
        repo = StubCacheRepository()

        # When
        await repo.set("key1", "value1")
        value = await repo.get("key1")

        # Then
        assert value == "value1"

    async def test_ttl_expiration(self):
        """GIVEN a value with TTL
        WHEN TTL expires
        THEN value is no longer available."""
        # Given
        repo = StubCacheRepository()
        await repo.set("temp-key", "temp-value", ttl=1)

        # When - immediately check (should exist)
        value_before = await repo.get("temp-key")

        # Wait for expiration
        import asyncio

        await asyncio.sleep(1.1)

        value_after = await repo.get("temp-key")

        # Then
        assert value_before == "temp-value"
        assert value_after is None

    async def test_increment_decrement(self):
        """GIVEN numeric cache values
        WHEN incrementing and decrementing
        THEN values change correctly."""
        # Given
        repo = StubCacheRepository()

        # When
        val1 = await repo.increment("counter")
        val2 = await repo.increment("counter", amount=5)
        val3 = await repo.decrement("counter", amount=2)

        # Then
        assert val1 == 1
        assert val2 == 6
        assert val3 == 4

    async def test_pattern_operations(self):
        """GIVEN keys with patterns
        WHEN searching by pattern
        THEN matching keys are found."""
        # Given
        repo = StubCacheRepository()
        await repo.set("test:user:1", "user1")
        await repo.set("test:user:2", "user2")
        await repo.set("test:session:1", "session1")

        # When
        user_keys = await repo.keys("test:user:*")
        deleted = await repo.delete_pattern("test:user:*")

        # Then
        assert len(user_keys) == 2
        assert deleted == 2
        assert await repo.exists("test:session:1")
        assert not await repo.exists("test:user:1")

    async def test_json_operations(self):
        """GIVEN JSON data
        WHEN storing and retrieving
        THEN JSON is preserved."""
        # Given
        repo = StubCacheRepository()
        data = {"name": "test", "count": 42, "active": True}

        # When
        await repo.set_json("config", data)
        retrieved = await repo.get_json("config")

        # Then
        assert retrieved == data
        assert retrieved["count"] == 42
