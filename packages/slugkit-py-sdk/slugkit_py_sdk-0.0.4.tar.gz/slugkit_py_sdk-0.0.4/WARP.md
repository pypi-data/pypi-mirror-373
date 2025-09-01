# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

SlugKit Python SDK is a Python library for generating human-readable IDs using the SlugKit.dev service. The SDK provides both synchronous and asynchronous clients, along with a comprehensive CLI tool.

## Architecture

### Core Components

**Client Architecture**: The SDK follows a dual-client pattern:
- `SyncClient` - Synchronous HTTP client using httpx
- `AsyncClient` - Asynchronous HTTP client using httpx async
- Both clients share common base classes in `base.py` for generator functionality

**Generator Pattern**: Three main generator types implemented via composition:
- `SyncSlugGenerator`/`AsyncSlugGenerator` - Main ID generation with streaming support
- `RandomGenerator`/`AsyncRandomGenerator` - Pattern-based ID generation
- All generators support method chaining for configuration (`.with_limit()`, `.with_batch_size()`, etc.)

**API Endpoints**: The SDK abstracts several SlugKit API endpoints:
- `/gen/mint` - Generate new IDs (increments counter)
- `/gen/slice` - Generate IDs from specific sequence (dry-run, no counter increment)
- `/gen/forge` - Generate IDs from patterns
- `/gen/reset` - Reset project generator
- `/gen/stats/latest` - Get generator statistics

### Key Design Patterns

**Streaming Support**: Both clients support streaming large batches of IDs to handle high-volume generation efficiently without memory issues.

**Configuration Chaining**: Generators support fluent configuration:
```python
generator.with_limit(1000).with_batch_size(100).starting_from(500)
```

**Series/Project Support**: Generators can target specific series within a project using bracket notation:
```python
client["series-slug"]  # Returns generator for specific series
```

## Development Commands

### Building and Publishing

```bash
# Build the package
make build

# Publish to PyPI
make publish
```

### Package Management

This project uses `uv` as the package manager. Dependencies are managed in `pyproject.toml`:

```bash
# Install development dependencies
uv sync

# Run with uv
uv run python -m slugkit.cli --help
```

### Testing

This project uses pytest for comprehensive testing of both sync and async clients:

```bash
# Install test dependencies
make install-test-deps

# Run all tests
make test

# Run tests with verbose output
make test-verbose

# Run tests with coverage (requires pytest-cov)
make test-coverage

# Run specific test files
uv run --group test pytest tests/test_sync_client.py
uv run --group test pytest tests/test_async_client.py
uv run --group test pytest tests/test_cli.py
```

**Test Structure**:
- `tests/test_sync_client.py` - Comprehensive sync client tests including streaming, error handling, and edge cases
- `tests/test_async_client.py` - Async client tests with mocked functionality
- `tests/test_cli.py` - CLI command tests using Typer's test runner
- `tests/conftest.py` - Shared fixtures and test configuration

**Test Environment**: Tests use dedicated API keys and project (`whole-blond-rower-a597`) for safe testing without affecting production data.

### Testing the CLI

The CLI tool `slugkit` supports multiple commands:

```bash
# Generate IDs
slugkit mint 5
slugkit mint 10 --batch-size 2

# Test patterns
slugkit forge "your-pattern" --seed "test-seed" --count 5

# Slice IDs (dry-run from sequence)
slugkit slice 100 5

# Get stats and manage generator
slugkit stats
slugkit reset
```

### Environment Configuration

Required environment variables:
```bash
export SLUGKIT_BASE_URL="https://dev.slugkit.dev/api/v1"
export SLUGKIT_API_KEY="your-api-key"
```

## Code Organization

**Source Structure**:
- `src/slugkit/` - Main package code
- `src/slugkit/base.py` - Shared base classes and common functionality
- `src/slugkit/sync_client.py` - Synchronous client implementation
- `src/slugkit/async_client.py` - Asynchronous client implementation  
- `src/slugkit/cli.py` - Command-line interface using Typer
- `src/slugkit/__init__.py` - Package exports

**Example Scripts**:
- `martian-bots.py` - Demo script showing multi-series ID generation for creating test data

## Important Implementation Details

**Error Handling**: The SDK handles HTTP errors gracefully and provides meaningful error messages. 404 errors from the API are caught and re-raised with response text.

**Streaming Implementation**: The streaming generators use httpx's streaming response handling to process large ID batches line by line without loading everything into memory.

**Authentication**: All authenticated endpoints require an API key. The SDK validates API key presence for operations that require it and provides clear error messages when missing.

**Dry Run Mode**: The "slice" functionality allows generating IDs from specific sequences without incrementing the project counter, useful for testing and previews.

## MCP Server Architecture

**MCP (Model Context Protocol) Server**: The SDK includes a comprehensive MCP server that enables AI assistants to generate guaranteed-unique identifiers. This solves the fundamental problem that AI cannot generate truly unique strings due to lack of persistence, coordination, and sequential awareness.

### MCP Server Components

**Server Implementation**: Located at `src/slugkit/mcp/server.py`
- Built using `fastmcp` framework for robust MCP protocol handling
- Supports both `stdio` and `http` transports
- Comprehensive logging and error handling
- Async/await architecture for high performance

**Tool Architecture**: The MCP server exposes SlugKit functionality through well-defined tools:
- **Core Generation Tools**: `forge`, `mint`, `slice` for different ID generation scenarios
- **Analysis Tools**: `validate_pattern`, `analyze_pattern`, `compare_patterns` for pattern evaluation
- **Information Tools**: `dictionary_info`, `series_info`, `key_info`, `stats` for discovery and monitoring
- **Management Tools**: `reset`, `ping` for administration and health checks
- **Documentation Tools**: `list_help_topics`, `get_help_topic` for inline help

**Resource System**: Provides access to documentation and pattern syntax through MCP resources:
- Pattern syntax EBNF grammar
- Help documentation and examples
- Best practices guides

### Key Design Patterns

**Context Management**: Uses FastMCP's context system for request lifecycle management:
```python
@asynccontextmanager
async def app_lifespan(app: FastMCP) -> AsyncIterator[AppContext]:
    # Manage global application state and client instances
```

**Client Factory Pattern**: Dynamic client creation per request:
```python
def get_client_for_session(ctx: Context["AppContext", ServerSession]) -> AsyncClient:
    # Creates properly authenticated client for each MCP session
```

**Tool Composition**: Each tool follows consistent patterns:
- Context injection for session management
- Comprehensive error handling and logging
- Input validation and transformation
- Structured response formatting

### Deployment Options

**Cloud Instance (Recommended)**:
- Hosted at `https://dev.slugkit.dev/api/v1/mcp`
- No local installation required
- Always up-to-date with latest features
- Uses `mcp-remote` bridge for MCP client compatibility

**Local Packaged Installation**:
```bash
pip install slugkit-py-sdk
slugkit-mcp
```
- Entry point: `slugkit-mcp` command
- Configurable via environment variables
- Supports debug logging and custom transports

**Development Setup**:
```bash
uv run slugkit-mcp
```
- Run directly from source tree
- Full development environment
- Hot reloading during development

### Available MCP Tools

**Generation Tools**:
- `forge(pattern, seed, sequence, count)` - Generate IDs from custom patterns
- `mint(series_slug, count, batch_size)` - Generate sequential IDs from series
- `slice(series_slug, count, batch_size, sequence)` - Preview IDs without consuming

**Analysis Tools**:
- `validate_pattern(pattern)` - Validate pattern syntax and get metadata
- `analyze_pattern(pattern)` - Deep analysis of pattern capacity and complexity
- `compare_patterns(patterns, count_per_pattern, seed)` - Side-by-side pattern comparison

**Information Tools**:
- `dictionary_info()` - Available word dictionaries and counts
- `dictionary_tags()` - Word filtering tags and content ratings
- `series_list()` - Available series in organization
- `series_info(series_slug)` - Detailed series information
- `key_info()` - API key capabilities and permissions
- `stats(series_slug)` - Usage and performance statistics

**Management Tools**:
- `reset(series_slug)` - Reset series (development/testing)
- `ping()` - Health check and connectivity test

**Documentation Tools**:
- `list_help_topics()` - Available documentation topics
- `get_help_topic(topic)` - Retrieve specific documentation

### Configuration and Environment

**Environment Variables**:
```bash
export SLUGKIT_BASE_URL="https://dev.slugkit.dev/api/v1"
export SLUGKIT_API_KEY="your-api-key"
```

**Command Line Options**:
```bash
slugkit-mcp --log-level DEBUG --transport http --host 0.0.0.0 --port 5000
```

**MCP Client Configuration**:
```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "slugkit-mcp",
            "env": {
                "SLUGKIT_API_KEY": "your-api-key"
            }
        }
    }
}
```
