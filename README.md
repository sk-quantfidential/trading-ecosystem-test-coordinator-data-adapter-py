# Test Coordinator Data Adapter

Data persistence adapter for the Test Coordinator service, providing comprehensive database and caching operations for test scenarios, runs, chaos events, and results.

## Features

- **Domain Models**: Scenario, TestRun, ChaosEvent, TestResult
- **Repository Pattern**: Clean interface-based architecture
- **PostgreSQL Integration**: Async operations with connection pooling
- **Redis Integration**: Caching and service discovery
- **Stub Repositories**: Graceful degradation when infrastructure unavailable
- **Type Safety**: Full Pydantic validation
- **Test Coverage**: Comprehensive unit and integration tests

## Installation

```bash
pip install -e .
```

## Development Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov
```

## Configuration

Environment variables with `TEST_COORDINATOR_ADAPTER_` prefix:

```bash
TEST_COORDINATOR_ADAPTER_POSTGRES_URL=postgres://user:pass@localhost/db
TEST_COORDINATOR_ADAPTER_REDIS_URL=redis://localhost:6379/0
```

## Architecture

Follows Clean Architecture principles with separation of:
- Domain Models (entities and value objects)
- Repository Interfaces (abstract contracts)
- Adapter Implementations (PostgreSQL, Redis, Stub)
- Factory Pattern (adapter creation and lifecycle)
