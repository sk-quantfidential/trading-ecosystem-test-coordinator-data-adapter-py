# Test Coordinator Data Adapter

Data adapter service for test coordination in the Trading Ecosystem.

## Status

🚧 **In Development** - Foundation phase

## Purpose

Provides data access and persistence layer for test coordination services, implementing the adapter pattern to separate business logic from data concerns.

## Architecture

- **Pattern**: Clean Architecture with Adapter pattern
- **Language**: Python 3.13+
- **Dependencies**: Protocol Buffers, gRPC, FastAPI

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Testing

```bash
pytest tests/ -v
```

## Related Services

- **test-coordinator-py**: Test orchestration and validation service

## Project Context

Part of Epic TSE-0001: Foundation Services & Infrastructure
