# SlugKit Python SDK

A Python SDK for generating human-readable IDs using SlugKit.dev service.

Please see [SlugKit documentation](https://dev.slugkit.dev) for information
on creating series and obtaining API keys.

## Installation

```bash
pip install slugkit-py-sdk
```

## API Overview

The SDK provides a comprehensive interface to generate human-readable IDs, test patterns, and manage generator state.

### Basic Usage

```python
from slugkit import SyncClient

# Initialize the client
client = SyncClient(
    base_url="https://dev.slugkit.dev/api/v1",
    api_key="your-api-key"
)

# Generate a single ID
id = client.series.mint()[0]

# Generate multiple IDs
ids = client.series.mint(count=5)

# Get generator stats
stats = client.series.stats()

# Get series information
series_info = client.series.info()

# Get list of available series
series_list = client.series.list()

# Reset the generator
client.series.reset()
```

### Advanced Generator Configuration

```python
# Configure generator with limits and batch sizes
generator = client.series.mint.with_limit(100).with_batch_size(10)

# Start from a specific sequence
generator = generator.starting_from(1000)

# Use dry-run mode (for testing)
generator = generator.with_dry_run()

# Generate IDs with configuration
ids = list(generator)
```

### Pattern Testing (Forge)

```python
# Test a pattern with various options
ids = client.forge(
    pattern="{adjective}-{noun}-{number:3d}",
    seed="optional-seed",
    sequence=1,
    count=5
)

# Get pattern information
pattern_info = client.forge.pattern_info("{adjective}-{noun}-{number:3d}")

# Get dictionary information
dict_info = client.forge.dictionary_info()

# Get dictionary tags
dict_tags = client.forge.dictionary_tags()

# Use different pattern types
ids = client.forge(
    pattern="simple-{noun}-{number:2,hex}",
    count=3
)
```

### Series Management

```python
# Access a specific series
series_generator = client.series["series-slug"]

# Generate IDs for specific series
ids = series_generator(count=10)

# Get stats for specific series
stats = series_generator.stats()

# Get series info for specific series
series_info = series_generator.series_info()
```

### Async Usage

The SDK also provides an async client for use with async/await code:

```python
import asyncio
from slugkit import AsyncClient

async def main():
    # Initialize the async client
    client = AsyncClient(
        base_url="https://dev.slugkit.dev/api/v1",
        api_key="your-api-key"
    )

    # Generate a single ID
    id = await client.series.mint()[0]

    # Generate multiple IDs
    ids = await client.series.mint(count=5)

    # Get generator stats
    stats = await client.series.stats()

    # Get series information
series_info = await client.series.info()

# Get list of available series
series_list = await client.series.list()

# Reset the generator
await client.series.reset()

    # Test a pattern
ids = await client.forge(
    pattern="{adjective}-{noun}-{number:3d}",
    seed="optional-seed",
    sequence=1,
    count=5
)

# Get pattern information
pattern_info = await client.forge.pattern_info("{adjective}-{noun}-{number:3d}")

# Get dictionary information
dict_info = await client.forge.dictionary_info()

# Get dictionary tags
dict_tags = await client.forge.dictionary_tags()

    # Stream IDs asynchronously
    async for id in client.series.mint:
        print(id)

# Run the async code
asyncio.run(main())
```

## Command Line Interface

The SDK includes a command-line interface for easy usage:

### Generate IDs

```bash
# Generate a single ID
slugkit mint

# Generate multiple IDs
slugkit mint 5

# Generate IDs with custom batch size
slugkit mint 10 --batch-size 2
```

### Test Patterns

```bash
# Test a pattern
slugkit forge "your-pattern"

# Test with specific seed and sequence
slugkit forge "your-pattern" --seed "my-seed" --sequence 1

# Generate multiple test IDs
slugkit forge "your-pattern" --count 5

# Validate a pattern and get information
slugkit validate "your-pattern"
```

### Generator Management

```bash
# Get generator stats
slugkit stats

# Get list of available series
slugkit series-list

# Get series information
slugkit series-info

# Reset the generator
slugkit reset
```

### Configuration

The CLI can be configured using environment variables or command-line options:

```bash
# Set base URL
export SLUGKIT_BASE_URL="https://dev.slugkit.dev/api/v1"

# Set API key
export SLUGKIT_API_KEY="your-api-key"

# Or use command-line options
slugkit --base-url "https://dev.slugkit.dev/api/v1" --api-key "your-api-key" mint
```

### Output Format

The CLI supports different output formats:

```bash
# Text output (default)
slugkit mint

# JSON output
slugkit mint --output-format json
```

## Data Types

The SDK provides structured data types for API responses:

### StatsItem

Represents generator statistics:

```python
from slugkit.base import StatsItem

stats = client.series.stats()
for item in stats:
    print(f"Event: {item.event_type}")
    print(f"Total Count: {item.total_count}")
    print(f"Request Count: {item.request_count}")
    print(f"Average Duration: {item.avg_duration_us}μs")
```

### SeriesInfo

Represents series information:

```python
from slugkit.base import SeriesInfo

series_info = client.series.info()
print(f"Pattern: {series_info.pattern}")
print(f"Capacity: {series_info.capacity}")
print(f"Generated: {series_info.generated_count}")
print(f"Last Modified: {series_info.mtime}")
```

### PatternInfo

Represents pattern information:

```python
from slugkit.base import PatternInfo

pattern_info = client.forge.pattern_info("test-{adjective}-{noun}")
print(f"Pattern: {pattern_info.pattern}")
print(f"Capacity: {pattern_info.capacity}")
print(f"Max Slug Length: {pattern_info.max_slug_length}")
print(f"Complexity: {pattern_info.complexity}")
print(f"Components: {pattern_info.components}")
```

### DictionaryInfo

Represents dictionary information:

```python
from slugkit.base import DictionaryInfo

dict_info = client.forge.dictionary_info()
for item in dict_info:
    print(f"Kind: {item.kind}, Count: {item.count}")
```

### DictionaryTag

Represents dictionary tags:

```python
from slugkit.base import DictionaryTag

dict_tags = client.forge.dictionary_tags()
for tag in dict_tags:
    print(f"Kind: {tag.kind}, Tag: {tag.tag}, Words: {tag.word_count}")
```

## API Response Examples

### Stats Response

```json
[
  {
    "event_type": "mint",
    "date_part": "total",
    "total_count": 104517,
    "request_count": 118,
    "total_duration_us": 1092348,
    "avg_duration_us": 10.45
  },
  {
    "event_type": "forge",
    "date_part": "total",
    "total_count": 15,
    "request_count": 5,
    "total_duration_us": 500,
    "avg_duration_us": 50.0
  }
]
```

### Series Info Response

```json
{
  "slug": "whole-blond-rower-a597",
  "org_slug": "alias-first-glute-67d9",
  "pattern": "{adverb}-{adjective}-{noun}-{number:3d}",
  "max_pattern_length": 80,
  "capacity": "1281739952493000",
  "generated_count": "105",
  "mtime": "2025-08-29T00:54:35.128902+00:00"
}
```

### Pattern Info Response

```json
{
  "pattern": "{adjective}-{noun}-{number:3d}",
  "capacity": "1000000",
  "max_slug_length": 25,
  "complexity": 3,
  "components": 3
}
```

### Dictionary Info Response

```json
[
  {
    "kind": "adjective",
    "count": 1000
  },
  {
    "kind": "noun",
    "count": 2000
  },
  {
    "kind": "verb",
    "count": 1500
  }
]
```

### Dictionary Tags Response

```json
[
  {
    "kind": "adjective",
    "tag": "positive",
    "description": "Positive adjectives",
    "opt_in": true,
    "word_count": 500
  },
  {
    "kind": "noun",
    "tag": "animals",
    "description": "Animal names",
    "opt_in": false,
    "word_count": 300
  }
]
```

### Series List Response

```json
[
  "series-1",
  "series-2",
  "series-3"
]
```

## Error Handling

The SDK provides comprehensive error handling:

```python
import httpx

try:
    ids = client.series.mint(count=10)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 400:
        print(f"Bad request: {e.response.text}")
    elif e.response.status_code == 401:
        print("Unauthorized - check your API key")
    elif e.response.status_code == 404:
        print("Resource not found")
    else:
        print(f"HTTP error {e.response.status_code}: {e.response.text}")
except httpx.ConnectError:
    print("Connection failed - check your network and base URL")
```

## Pattern Language

The SDK supports SlugKit's pattern language for generating structured IDs:

### Basic Tokens

- `{adjective}` - Random adjective
- `{noun}` - Random noun  
- `{adverb}` - Random adverb
- `{verb}` - Random verb

### Number Generators

- `{number:3d}` - 3-digit decimal number
- `{number:4,hex}` - 4-character hexadecimal
- `{number:2r}` - up to 2-character roman number, lowercase
- `{number:6R}` - up to 6-character roman number, uppercase

### Examples

```python
# Simple patterns
pattern1 = "{adjective}-{noun}"
pattern2 = "{color}-{animal}-{number:3d}"

# Complex patterns with constraints
pattern3 = "{adverb}-{adjective}-{noun}-{number:4,hex}[==5]"

# Generate IDs
ids = client.forge(pattern=pattern3, count=5)
```

## MCP Server: AI Assistant Integration

**⚡ The SlugKit MCP Server enables AI assistants to generate truly unique identifiers!**

### The Problem with AI-Generated IDs

AI assistants cannot generate truly unique strings because they:
- Have no persistence between conversations
- Cannot coordinate across multiple instances
- Generate probabilistic, not truly random content
- Have no concept of sequential uniqueness

This makes AI-generated identifiers unsuitable for production use where uniqueness is critical.

### The Solution: SlugKit MCP Integration

The SlugKit MCP (Model Context Protocol) server connects AI assistants like Claude Desktop, Cursor, and Warp directly to SlugKit's guaranteed-unique ID generation service.

**Key Benefits:**
- ✅ **Guaranteed Uniqueness** - Mathematical guarantees, not probabilistic generation
- ✅ **Sequential Consistency** - Proper sequential IDs across all sessions
- ✅ **Production Ready** - Battle-tested for high-volume applications
- ✅ **Zero Collisions** - Impossible to generate duplicate IDs
- ✅ **Pattern Flexibility** - Generate IDs matching your exact requirements

### Quick Setup

**Cloud Instance (Recommended):**
```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "npx",
            "args": [
                "-y", "mcp-remote",
                "https://dev.slugkit.dev/api/v1/mcp",
                "--header", "x-api-key:YOUR_API_KEY_HERE"
            ]
        }
    }
}
```

**Local Installation:**
```bash
pip install slugkit-py-sdk
```

```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "slugkit-mcp",
            "env": {
                "SLUGKIT_API_KEY": "YOUR_API_KEY_HERE"
            }
        }
    }
}
```

### Usage Examples

Once configured, ask your AI assistant:

```
"Generate 10 unique user IDs with the pattern user-{adjective}-{noun}-{number:4d}"
```
*→ Returns guaranteed-unique IDs like "user-happy-dolphin-0001", "user-bright-falcon-0002"*

```
"Analyze this pattern: {color}-{animal}-{number:3,hex} - how many unique IDs can it generate?"
```
*→ Shows capacity analysis: "1.2M unique combinations, medium complexity"*

```
"Compare these URL slug patterns and recommend the best one: {adjective}-{noun} vs {verb}-{noun}-{number:2d}"
```
*→ Generates samples, analyzes capacity, recommends optimal choice*

### Available Capabilities

The MCP server provides AI assistants with access to:

- **ID Generation:** `forge` (custom patterns), `mint` (series), `slice` (preview)
- **Pattern Analysis:** `validate_pattern`, `analyze_pattern`, `compare_patterns` 
- **Information:** `dictionary_info`, `series_info`, `key_info`, `stats`
- **Management:** `series_list`, `reset` (dev/test)
- **Documentation:** `get_help_topic`, pattern syntax references

**📚 For detailed setup instructions, troubleshooting, and advanced configuration, see [README_MCP.md](README_MCP.md)**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
