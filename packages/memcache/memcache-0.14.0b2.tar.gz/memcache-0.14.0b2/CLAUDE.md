# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

This is a Python memcached client library using uv for dependency management.

### Core Dependencies
- Python ^3.7
- hashring ^1.5.1 (for consistent hashing across servers)
- anyio ^3.0.0 (for async support)

### Development Dependencies
- pytest ^8.0.0 (testing framework)
- pytest-asyncio ^0.23.0 (async test support)
- pytest-trio (Trio support)
- mypy ^1.10.0 (type checking)
- black ^24.0.0 (code formatting)
- flake8 ^7.0.0 (linting)

### Common Commands

```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest
uv run pytest tests/test_client.py  # Run specific test file
uv run pytest tests/test_async_client.py  # Run async tests
uv run pytest tests/test_trio_client.py  # Run Trio tests

# Type checking
uv run mypy . --exclude .venv

# Code formatting
uv run black memcache/ tests/

# Linting
uv run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=.venv
uv run flake8 . --count --exit-zero --max-complexity=10 --statistics --exclude=.venv

# Build package
uv build
```

## Architecture Overview

### Core Components

1. **memcache/**: Main package directory
   - `__init__.py`: Exports public API (AsyncMemcache, Memcache, MemcacheError, MetaResult, MetaCommand)
   - `memcache.py`: Synchronous client implementation
   - `async_memcache.py`: Asynchronous client implementation
   - `meta_command.py`: Meta command protocol implementation (memcached's new meta commands)
   - `errors.py`: Custom exception classes
   - `serialize.py`: Serialization utilities for data storage/retrieval

2. **Protocol Design**
   - Uses memcached's new meta commands instead of the older ASCII protocol
   - Meta commands provide more efficient operations with better error handling
   - Supports authentication via username/password

3. **Client Architecture**
   - **AsyncConnection**: Low-level async connection to single memcached server
   - **Connection**: Sync wrapper around AsyncConnection using event loops
   - **AsyncMemcache**: High-level async client with consistent hashing across multiple servers
   - **Memcache**: High-level sync client (wrapper around AsyncMemcache)

4. **Data Flow**
   - Client operations → MetaCommand objects → TCP connection → memcached server
   - Responses parsed into MetaResult objects
   - Automatic serialization/deserialization of Python objects

### Key Classes

- `MetaCommand`: Represents a memcached meta command with cm (command), key, flags, and optional value
- `MetaResult`: Represents server response with return code, data length, flags, and value
- `AsyncConnection`: Manages single TCP connection with auth support
- `AsyncMemcache`: Manages multiple server connections with consistent hashing
- `Memcache`: Synchronous interface wrapping AsyncMemcache

### Testing Notes

- Tests require a running memcached server on localhost:11211
- Uses pytest fixtures for client setup
- Tests cover both sync and async client operations
- Tests validate basic CRUD operations and meta command execution
- CI runs on Python 3.8-3.13 with memcached automatically set up
- GitHub Actions workflow: `.github/workflows/ci.yaml`