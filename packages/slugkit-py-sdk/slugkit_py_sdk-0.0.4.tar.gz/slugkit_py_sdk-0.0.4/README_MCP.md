# SlugKit MCP Server Guide

## The Problem: AI Cannot Generate Unique Strings

**AI assistants like Claude, ChatGPT, and others cannot generate truly unique strings.** This is a fundamental limitation of how language models work:

- **No persistence**: Each conversation is isolated, so AI can't remember what it generated before
- **No coordination**: Multiple AI instances can't coordinate to avoid duplicates
- **Probabilistic nature**: AI generates text based on patterns, not true randomness
- **Sequence awareness**: AI has no concept of sequential uniqueness across sessions

### Real-World Impact

This limitation becomes critical when you need:
- **Unique identifiers** for database records, user accounts, or API resources
- **Sequential IDs** that increment properly across multiple requests
- **Non-colliding slugs** for URLs, file names, or resource identifiers
- **Guaranteed uniqueness** in production systems where duplicates cause failures

**SlugKit MCP solves this by connecting AI assistants to a real uniqueness-guaranteed ID generation service.**

## What is MCP?

Model Context Protocol (MCP) is an open standard that allows AI assistants to securely connect to external data sources and tools. The SlugKit MCP server provides AI assistants like Claude Desktop, Cursor, and Warp with direct access to SlugKit's guaranteed-unique ID generation capabilities.

## Why Use the SlugKit MCP Server?

### Core Benefits

1. **True Uniqueness**: Unlike AI-generated strings, SlugKit guarantees every ID is unique within its series
2. **Sequential Consistency**: IDs increment properly across all requests and sessions
3. **Production Ready**: Built for high-volume, mission-critical applications
4. **Pattern Flexibility**: Generate IDs matching your specific format requirements
5. **Collision-Free**: Mathematical guarantees prevent duplicate generation

### What Your AI Assistant Can Do

- **Generate guaranteed-unique IDs** directly in conversations
- **Analyze and validate patterns** before deploying them
- **Compare different pattern designs** to optimize for your use case
- **Get comprehensive statistics** about ID generation performance
- **Access SlugKit documentation** and pattern syntax help
- **Test patterns** without affecting production series
- **Preview ID sequences** without consuming them (dry-run mode)

This creates a seamless workflow where you can discuss ID generation strategies with your AI assistant and have it immediately generate, test, and validate truly unique identifiers for you.

## Available Tools

The MCP server provides these tools to AI assistants:

### Core Generation
- **`forge`** - Generate unique IDs from custom patterns (one-off generation)
- **`mint`** - Generate sequential unique IDs from predefined series (production use)
- **`slice`** - Preview what IDs would be generated without consuming them (dry-run)

### Pattern Analysis & Validation
- **`validate_pattern`** - Validate pattern syntax and get detailed information
- **`analyze_pattern`** - Analyze pattern complexity, capacity, and performance characteristics
- **`compare_patterns`** - Compare multiple patterns side-by-side with sample outputs

### Information & Discovery
- **`dictionary_info`** - Get available word categories (adjectives, nouns, etc.) and counts
- **`dictionary_tags`** - Get word filtering options and content ratings
- **`series_list`** - List available series in your organization
- **`series_info`** - Get detailed information about a specific series
- **`key_info`** - Get your API key capabilities and permissions

### Management & Monitoring
- **`stats`** - Get comprehensive usage and performance statistics
- **`reset`** - Reset a series (development/testing only)
- **`ping`** - Test connectivity to SlugKit API

### Documentation
- **`list_help_topics`** - List available documentation topics
- **`get_help_topic`** - Retrieve specific documentation (pattern syntax, examples, etc.)

## Setup Instructions

### Option 1: Cloud Instance (Recommended)

Use our hosted MCP server for the easiest setup:

> [!NOTE]
> Most MCP clients don't support remote servers directly, so we use `mcp-remote` to bridge the connection.

**For Claude Desktop:**
```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "https://dev.slugkit.dev/api/v1/mcp",
                "--header",
                "x-api-key:YOUR_API_KEY_HERE"
            ]
        }
    }
}
```

**For Cursor:**
```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "https://dev.slugkit.dev/api/v1/mcp",
                "--header",
                "x-api-key:YOUR_API_KEY_HERE"
            ]
        }
    }
}
```

**For Warp:**
Add to your Warp MCP configuration:
```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "https://dev.slugkit.dev/api/v1/mcp",
                "--header",
                "x-api-key:YOUR_API_KEY_HERE"
            ]
        }
    }
}
```

### Option 2: Local Installation

Install and run the MCP server locally:

```bash
# Install the SlugKit Python SDK
pip install slugkit-py-sdk
```

Then add to your MCP client configuration:

```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "slugkit-mcp",
            "env": {
                "SLUGKIT_API_KEY": "YOUR_API_KEY_HERE",
                "SLUGKIT_BASE_URL": "https://dev.slugkit.dev/api/v1"
            }
        }
    }
}
```

### Option 3: Development Setup

For development or if you want to run from the source code:

```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "uv",
            "args": [
                "--directory",
                "/path/to/slugkit-py-sdk",
                "run",
                "slugkit-mcp"
            ],
            "env": {
                "SLUGKIT_API_KEY": "YOUR_API_KEY_HERE",
                "SLUGKIT_BASE_URL": "https://dev.slugkit.dev/api/v1"
            }
        }
    }
}
```

## Configuration Files

MCP client configuration files are typically located at:

- **Claude Desktop (macOS):** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Claude Desktop (Windows):** `%APPDATA%/Claude/claude_desktop_config.json`
- **Cursor:** Follow Cursor's MCP setup documentation
- **Warp:** Follow Warp's MCP setup documentation

## Getting Your API Key

1. Visit [SlugKit.dev](https://dev.slugkit.dev)
2. Sign up or log in to your account
3. Create a new organization or select an existing one
4. Generate an API key with appropriate permissions
5. Replace `YOUR_API_KEY_HERE` in the configuration above

## Usage Examples

Once configured, you can ask your AI assistant to:

### Generate Unique IDs (The Core Benefit)
```
"I need 10 unique identifiers for user accounts using the pattern user-{adjective}-{noun}-{number:4d}"
```
*Response: Generates 10 guaranteed-unique IDs like "user-happy-dolphin-0001", "user-bright-falcon-0002", etc.*

### Analyze Pattern Capacity
```
"Analyze this pattern: {color}-{animal}-{number:4,hex} and tell me how many unique IDs it can generate"
```
*Response: Shows total capacity (e.g., "2.1M unique combinations"), complexity analysis, and recommendations*

### Compare Pattern Options
```
"Compare these patterns and recommend the best one for a URL slug system:
- {adjective}-{noun}
- {verb}-{noun}-{number:2d}
- {adverb}-{adjective}-{animal}"
```
*Response: Generates samples from each pattern, analyzes capacity and performance, recommends best option*

### Validate Before Production
```
"Is this pattern valid and production-ready: {adjective:+positive}-{noun:+animals}-{special:3-5}?"
```
*Response: Validates syntax, shows capacity, identifies any issues, suggests improvements*

### Sequential ID Generation
```
"Generate the next 5 IDs in sequence from my main series"
```
*Response: Returns the next 5 sequential, unique IDs from your production series*

### Preview Without Consuming
```
"Show me what the next 10 IDs would look like without actually generating them"
```
*Response: Uses slice/dry-run mode to preview upcoming IDs without incrementing counters*

## The Uniqueness Guarantee

### How SlugKit Ensures Uniqueness

1. **Server-Side State**: SlugKit maintains state across all requests and sessions
2. **Atomic Operations**: Each ID generation is an atomic operation with database backing
3. **Sequential Tracking**: Series maintain counters that never repeat
4. **Collision Detection**: Mathematical guarantees prevent duplicate generation within patterns
5. **Global Coordination**: All clients coordinate through the central service

### Comparison: AI vs SlugKit

| Aspect | AI Assistant Alone | With SlugKit MCP |
|--------|-------------------|------------------|
| **Uniqueness** | ❌ Cannot guarantee | ✅ Mathematically guaranteed |
| **Sequences** | ❌ No sequence awareness | ✅ Proper sequential generation |
| **Persistence** | ❌ Forgets between sessions | ✅ Persistent state across all sessions |
| **Collision Prevention** | ❌ High collision probability | ✅ Zero collision guarantee |
| **Production Ready** | ❌ Not suitable for production | ✅ Battle-tested for production use |
| **Scale** | ❌ Breaks down with volume | ✅ Handles millions of IDs |

## Troubleshooting

### Connection Issues

**Problem:** "Connection failed" or timeout errors

**Solutions:**
1. Verify your API key is correct and has not expired
2. Check that `SLUGKIT_BASE_URL` is set to `https://dev.slugkit.dev/api/v1`
3. Test connectivity: Ask the assistant to run the `ping` tool
4. For cloud instance: Ensure `mcp-remote` is working with `npx -y mcp-remote --version`

### Authentication Issues

**Problem:** "Unauthorized" or API key errors

**Solutions:**
1. Verify your API key is valid at [SlugKit.dev](https://dev.slugkit.dev)
2. Check that the API key has the necessary scopes (forge, mint, slice, stats)
3. Ensure the API key is properly set in the environment variables
4. Use the `key_info` tool to verify your key's permissions

### Installation Issues

**Problem:** Command not found or package errors

**Solutions:**
1. **For cloud instance:** Run `npm install -g mcp-remote` if npx fails
2. **For local installation:** Ensure `pip install slugkit-py-sdk` completed successfully
3. **For development:** Make sure `uv` is installed and the path is correct
4. Restart your MCP client after configuration changes

### Pattern Issues

**Problem:** Pattern validation or generation errors

**Solutions:**
1. Use the `validate_pattern` tool to check syntax
2. Check the pattern syntax documentation with `get_help_topic`
3. Start with simple patterns like `{adjective}-{noun}` and build complexity
4. Use `analyze_pattern` to understand pattern limitations

## Advanced Configuration

### Custom Base URL

If you're using a different SlugKit instance:

```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "slugkit-mcp",
            "env": {
                "SLUGKIT_API_KEY": "YOUR_API_KEY_HERE",
                "SLUGKIT_BASE_URL": "https://your-instance.com/api/v1"
            }
        }
    }
}
```

### Logging and Debug

For troubleshooting, you can enable debug logging:

```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "slugkit-mcp",
            "args": ["--log-level", "DEBUG"],
            "env": {
                "SLUGKIT_API_KEY": "YOUR_API_KEY_HERE"
            }
        }
    }
}
```

### HTTP Transport

For advanced setups, you can run the MCP server with HTTP transport:

```bash
slugkit-mcp --transport http --host 127.0.0.1 --port 3000 --path /mcp
```

Then configure your MCP client to connect to `http://127.0.0.1:3000/mcp`.

## Best Practices

1. **Start Simple:** Begin with basic patterns like `{adjective}-{noun}` and gradually add complexity
2. **Validate First:** Always use `validate_pattern` before deploying patterns to production
3. **Use Dry-Run:** Use `slice` to preview IDs before `mint`ing them in production
4. **Monitor Usage:** Regularly check `stats` to understand your usage patterns and performance
5. **Test Patterns:** Use `forge` for testing and experimentation, `mint` for production series
6. **Check Capacity:** Use `analyze_pattern` to ensure patterns have sufficient capacity for your needs
7. **Plan for Scale:** Consider future growth when choosing patterns - start with higher capacity than you need

## Getting Help

- **Documentation:** Use the `get_help_topic` tool for pattern syntax and examples
- **API Reference:** Visit [SlugKit.dev documentation](https://dev.slugkit.dev/docs)
- **Support:** Contact support through the SlugKit.dev website
- **Issues:** Report bugs or request features on the GitHub repository
- **Community:** Join discussions about unique identifier generation and best practices
