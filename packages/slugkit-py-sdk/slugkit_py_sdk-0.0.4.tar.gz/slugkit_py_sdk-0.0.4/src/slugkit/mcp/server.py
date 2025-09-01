"""
SlugKit MCP Server
"""

import os
import argparse
import logging

import importlib.resources as pkg_resources

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Generator
from importlib.resources.abc import Traversable

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

from slugkit import AsyncClient
from slugkit.base import (
    PatternInfo,
    DictionaryInfo,
    DictionaryTag,
    SeriesInfo,
    StatsItem,
)
from slugkit.package_data import list_package_files, get_package_data

logger = logging.getLogger("slugkit-mcp")


@dataclass
class AppContext:
    base_url: str
    client: AsyncClient | None

    @classmethod
    def from_context(cls, ctx: Context["AppContext", ServerSession]) -> "AppContext":
        return ctx.request_context.lifespan_context


def get_client_for_session(ctx: Context["AppContext", ServerSession]) -> AsyncClient:
    app_context = AppContext.from_context(ctx)
    if app_context.client is not None:
        return app_context.client
    try:
        api_key = ctx.request_context.request.headers["x-api-key"]
        logger.debug(f"API key: {api_key}")
    except Exception as e:
        logger.error(f"Failed to get API key from request headers: {str(e)}")
        raise
    return AsyncClient(base_url=app_context.base_url, api_key=api_key)


@asynccontextmanager
async def app_lifespan(app: FastMCP) -> AsyncIterator[AppContext]:
    # Note: We can't use MCP Context logging here since no context exists yet
    # The server startup will be logged by FastMCP itself
    logger.debug(f"App lifespan started")
    base_url = os.getenv("SLUGKIT_BASE_URL", "https://dev.slugkit.dev/api/v1")
    api_key = os.getenv("SLUGKIT_API_KEY", None)

    client = AsyncClient(base_url=base_url, api_key=api_key) if api_key else None

    try:
        yield AppContext(base_url=base_url, client=client)
    finally:
        # Server shutdown will be handled by FastMCP
        pass


mcp = FastMCP(
    name="slugkit",
    lifespan=app_lifespan,
    log_level="DEBUG",  # Send all log levels to MCP client
    debug=True,  # Enable debug mode for verbose logging
)

# MCP Context logging will be used in tool functions
# This ensures logs are sent to the MCP client (inspector) via the protocol


@mcp.resource("file://docs/{file_name}")
async def docs(file_name: str) -> str:
    """
    Get the documentation for SlugKit
    """
    return get_package_data(file_name)


@mcp.resource("file://docs")
async def docs_list() -> list[str]:
    """
    Get the list of available documentation files
    """

    def filter(file_name: str) -> bool:
        return (
            file_name.endswith(".md")
            or file_name.endswith(".txt")
            or file_name.endswith(".json")
            or file_name.endswith(".ebnf")
        )

    return list_package_files(filter=filter)


@mcp.tool()
async def list_help_topics() -> list[str]:
    """
    List available help topics and documentation.

    Returns available documentation that explains SlugKit usage,
    pattern syntax, examples, and best practices.
    """
    filter = lambda x: x.endswith(".md") and not x.endswith(".ebnf")
    return list_package_files(filter=filter)


@mcp.tool()
async def get_help_topic(topic: str) -> str:
    """
    Retrieve help documentation for a specific topic.

    Args:
        topic: Name of help topic (use list_help_topics() to see available topics)

    Returns the full documentation content for the specified topic.
    Essential for understanding SlugKit pattern syntax and capabilities.
    """
    return get_package_data(f"{topic}")


@mcp.tool()
async def ping(ctx: Context[AppContext, ServerSession]) -> str:
    """
    Check if the SlugKit API server is alive and responsive.

    This tool performs a simple connectivity test to verify that the MCP server
    can successfully communicate with the SlugKit API. Use this to diagnose
    connection issues before attempting other operations.

    Returns:
        str: "pong" if the server is responsive, or error message if connection fails

    Use this tool to verify your SlugKit API configuration and connectivity
    before attempting other operations. This is a lightweight health check.
    """
    logger.info("Ping tool called - checking SlugKit API connectivity")
    try:
        client = get_client_for_session(ctx)
        await client.ping()
        logger.debug("Ping successful - SlugKit API is responsive")
        return "pong"
    except Exception as e:
        logger.error(f"Ping failed: {str(e)}")
        return f"Connection failed: {str(e)}"


@mcp.tool()
async def key_info(ctx: Context[AppContext, ServerSession]) -> dict:
    """
    Get comprehensive information about the current API key and its capabilities.

    This tool provides detailed metadata about your API key, including its scope,
    permissions, and associated organization/series. Use this to understand what
    operations you can perform and what resources you have access to.

    Returns:
        dict: Key information including:
            - type: Key type (api-key or sdk-config)
            - key_scope: Scope level (org or series)
            - slug: Key identifier
            - org_slug: Organization slug
            - series_slug: Series slug (if series-scoped)
            - scopes: List of allowed operations (forge, mint, slice, reset, stats)
            - enabled: Whether the key is active

    Use this tool to understand your key's permissions before attempting operations.
    This helps agents make informed decisions about available functionality.
    """
    logger.info("Key info tool called - retrieving API key information")
    try:
        client = get_client_for_session(ctx)
        key_info = await client.key_info()
        logger.debug(f"Key info retrieved successfully - scope: {key_info.key_scope.value}, scopes: {key_info.scopes}")
        return {
            "type": key_info.type,
            "key_scope": key_info.key_scope.value,
            "slug": key_info.slug,
            "org_slug": key_info.org_slug,
            "series_slug": key_info.series_slug,
            "scopes": key_info.scopes,
            "enabled": key_info.enabled,
        }
    except Exception as e:
        logger.error(f"Failed to get key info: {str(e)}")
        return {"error": f"Failed to get key info: {str(e)}"}


@mcp.tool()
async def validate_pattern(pattern: str, ctx: Context[AppContext, ServerSession]) -> PatternInfo | str:
    """
    Validate a SlugKit pattern and return detailed information about its structure and capabilities.

    This tool is essential for understanding pattern complexity, capacity, and constraints before using them
    in slug generation. Use this to verify pattern syntax and get metadata about the pattern.

    ⚠️  Use this FIRST before forge(), mint(), or other pattern operations!
    📚 Pattern syntax help: Use get_help_topic('pattern-syntax-reference.md')

    Args:
        pattern: The SlugKit pattern string to validate (e.g., "{adjective}-{noun}-{number:3d}")

    Returns:
        PatternInfo: The pattern information
        str: The error message
    """
    logger.info(f"Validate pattern tool called - pattern: {pattern}")
    try:
        client = get_client_for_session(ctx)
        result = await client.forge.pattern_info(pattern)
        logger.debug(f"Pattern validation successful for: {pattern}")
        return result
    except Exception as e:
        logger.error(f"Pattern validation failed for '{pattern}': {e}")
        return str(e)


@mcp.tool()
async def dictionary_info(ctx: Context[AppContext, ServerSession]) -> list[DictionaryInfo]:
    """
    Get comprehensive information about all available word dictionaries in SlugKit.

    This tool provides metadata about the word collections available for slug generation,
    including word counts for each category (adjectives, nouns, verbs, etc.).

    Returns:
        list[DictionaryInfo]: List of dictionary information including:
            - kind: Dictionary category (e.g., "adjective", "noun", "verb")
            - count: Total number of words in this dictionary

    Use this tool to understand what word types are available for your patterns.
    Combine with dictionary_tags() to get detailed information about specific word collections.
    """
    logger.info("Dictionary info tool called - retrieving available word dictionaries")
    try:
        client = get_client_for_session(ctx)
        result = await client.forge.dictionary_info()
        logger.debug(f"Successfully retrieved dictionary info for {len(result)} dictionary types")
        return result
    except Exception as e:
        logger.error(f"Failed to get dictionary info: {str(e)}")
        raise


@mcp.tool()
async def dictionary_tags(ctx: Context[AppContext, ServerSession]) -> list[DictionaryTag]:
    """
    Get detailed information about dictionary tags and their properties.

    This tool provides information about tags that can be used to filter and categorize
    words within dictionaries, such as content ratings, themes, or language variants.

    Returns:
        list[DictionaryInfo]: List of dictionary tag information including:
            - kind: Dictionary category this tag applies to
            - tag: Tag identifier (e.g., "family-friendly", "technical")
            - description: Human-readable description of the tag
            - opt_in: Whether this tag is opt-in by default
            - word_count: Number of words with this tag

    Use this tool to understand available word filtering options for creating
    appropriate content for different audiences or contexts.
    """
    logger.info("Dictionary tags tool called - retrieving dictionary tag information")
    try:
        client = get_client_for_session(ctx)
        result = await client.forge.dictionary_tags()
        logger.debug(f"Successfully retrieved {len(result)} dictionary tags")
        return result
    except Exception as e:
        logger.error(f"Failed to get dictionary tags: {str(e)}")
        raise


@mcp.tool()
async def forge(
    *,
    pattern: str,
    seed: str = "",
    sequence: int = 0,
    count: int = 1,
    ctx: Context[AppContext, ServerSession],
) -> list[str]:
    """
    Generate unique, human-readable slugs from a pattern without using a predefined series.

    This tool creates slugs on-demand using the specified pattern. It's ideal for one-off
    slug generation or when you need custom patterns that don't fit into a series.

    Args:
        pattern: The SlugKit pattern string defining the slug structure (required)
                 Examples: "{adjective}-{noun}", "{adjective}-{noun}-{number:4d}"
        seed: Optional seed string for reproducible generation (same seed = same results)
        sequence: Optional starting sequence number for number generators
        count: Number of unique slugs to generate (default: 1, max: 1000)

    Returns:
        list[str]: List of generated unique slugs matching the pattern

    Examples:
        - Basic: pattern="{adjective}-{noun}", count=3
        - With seed: pattern="{adjective}-{noun}", seed="test", count=2
        - With sequence: pattern="{adjective}-{noun}-{number:3d}", sequence=100, count=2

    Use validate_pattern() first to ensure your pattern is valid and understand its capabilities.
    For repeated generation of similar slugs, consider using mint() with a series instead.
    """
    # Handle empty string as "not provided" for seed
    actual_seed = None if seed == "" else seed

    logger.info(f"Forge tool called - pattern: {pattern}, seed: {actual_seed}, sequence: {sequence}, count: {count}")
    try:
        client = get_client_for_session(ctx)
        result = await client.forge(pattern, seed=actual_seed, sequence=sequence, count=count)
        logger.debug(f"Successfully forged {len(result)} slugs with pattern: {pattern}")
        return result
    except Exception as e:
        logger.error(f"Error forging slugs with pattern '{pattern}': {str(e)}")
        raise


@mcp.tool()
async def series_list(ctx: Context[AppContext, ServerSession]) -> list[str]:
    """
    Get a list of all available series slugs that can be used for minting or slicing.

    A series is a predefined collection of slugs with a specific pattern and configuration.
    Use this tool to discover available series before using mint() or slice() operations.

    Returns:
        list[str]: List of available series slug identifiers

    Use this tool to explore what series are available, then use series_info() to get
    detailed information about a specific series before minting or slicing from it.
    """
    logger.info("Series list tool called - retrieving available series")
    try:
        client = get_client_for_session(ctx)
        result = await client.series.list()
        logger.debug(f"Successfully retrieved {len(result)} available series")
        return result
    except Exception as e:
        logger.error(f"Failed to get series list: {str(e)}")
        raise


@mcp.tool()
async def series_info(
    *,
    series_slug: str = "",
    ctx: Context[AppContext, ServerSession],
) -> SeriesInfo:
    """
    Get detailed information about a series, including its pattern, capacity, and usage statistics.

    This tool provides comprehensive metadata about a series, helping you understand its
    capabilities and current state before using it for slug generation.

    Note: Series info is cached by the server for 30-60 seconds, so the results may not be up to date.
    Don't expect the results to be accurate immediately after each operation.

    Args:
        series_slug: The slug identifier of the series to examine (optional)
                    If not provided, returns info about the default/current series

    Returns:
        SeriesInfo: Detailed series information including:
            - slug: Series identifier
            - org_slug: Organization that owns the series
            - pattern: The pattern used for generating slugs in this series
            - max_pattern_length: Maximum allowed length for generated slugs
            - capacity: Total possible unique slugs this series can generate
            - generated_count: Number of slugs already generated
            - mtime: Last modification time

    Use this tool to understand a series's capabilities and current usage before
    minting or slicing from it. Combine with stats() to get performance metrics.
    """
    # Handle empty string as "not provided"
    client = get_client_for_session(ctx)
    if series_slug:
        logger.debug(f"Getting info for specific series: {series_slug}")
        return await client.series[series_slug].info()
    else:
        logger.debug("Getting info for default series")
        return await client.series.info()


@mcp.tool()
async def reset(
    *,
    series_slug: str = "",
    ctx: Context[AppContext, ServerSession],
) -> str:
    """
    Reset a series to its initial state, clearing all generated slugs and resetting counters.

    This tool is useful for testing, development, or when you want to start fresh
    with a series. Be cautious as this operation cannot be undone.

    Args:
        series_slug: The slug identifier of the series to reset (optional)
                    If not provided, resets the default/current series

    Returns:
        str: Confirmation message indicating the reset was successful

    Use this tool carefully as it will permanently clear all generated slugs from
    the specified series. Consider backing up any important slugs before resetting.
    """
    # Handle empty string as "not provided"
    logger.info(f"Reset tool called - series: {series_slug or 'default'}")
    try:
        if series_slug:
            client = get_client_for_session(ctx)
            await client.series[series_slug].reset()
        else:
            client = get_client_for_session(ctx)
            await client.series.reset()
        logger.debug(f"Successfully reset series: {series_slug or 'default'}")
        return f"Series {series_slug or 'default'} has been reset successfully"
    except Exception as e:
        logger.error(f"Failed to reset series {series_slug or 'default'}: {str(e)}")
        return f"Failed to reset series: {str(e)}"


@mcp.tool()
async def stats(
    *,
    series_slug: str = "",
    ctx: Context[AppContext, ServerSession],
) -> list[StatsItem]:
    """
    Get comprehensive performance and usage statistics for a series.

    This tool provides detailed metrics about slug generation performance, including
    request counts, durations, and event types across different time periods.

    Note: Stats aggregation is run every 60 seconds by the server, so the results may
    not be up to date. Don't expect the results to be accurate immediately after each
    operation.

    Args:
        series_slug: The slug identifier of the series to get stats for (optional)
                    If not provided, returns stats for the default/current series

    Returns:
        list[StatsItem]: List of statistics including:
            - event_type: Type of operation (forge, mint, slice, reset)
            - date_part: Time period (hour, day, week, month, year, total)
            - total_count: Total slugs generated in this period
            - request_count: Number of API requests made
            - total_duration_us: Total processing time in microseconds
            - avg_duration_us: Average processing time per request

    Use this tool to monitor series performance, track usage patterns, and identify
    potential bottlenecks or optimization opportunities.
    """
    # Handle empty string as "not provided"
    logger.info(f"Stats tool called - series: {series_slug or 'default'}")
    try:
        client = get_client_for_session(ctx)
        if series_slug:
            result = await client.series[series_slug].stats()
        else:
            result = await client.series.stats()
        logger.debug(f"Successfully retrieved stats for series: {series_slug or 'default'}")
        return result
    except Exception as e:
        logger.error(f"Failed to get stats for series {series_slug or 'default'}: {str(e)}")
        raise


@mcp.tool()
async def mint(
    *,
    series_slug: str = "",
    count: int = 1,
    batch_size: int = 1000,
    ctx: Context[AppContext, ServerSession],
) -> list[str]:
    """
    Mint new, unique slugs from a series using its predefined pattern.

    Minting creates new slugs that are tracked and managed within the series.
    This is ideal for production use where you need consistent, managed slug generation.

    Args:
        series_slug: The slug identifier of the series to mint from (optional)
                    If not provided, mints from the default/current series
        count: Number of unique slugs to mint (default: 1, max: 10000)
        batch_size: Internal batch size for efficient processing (default: 1000)
                   Higher values may improve performance for large counts

    Returns:
        list[str]: List of newly minted, unique slugs from the series

    Use this tool when you need to generate slugs that are part of a managed series.
    The generated slugs will be tracked in the series statistics and cannot be
    regenerated (unlike forge which can generate the same slug multiple times).

    Examples:
        - Mint 5 slugs from default series: count=5
        - Mint 100 slugs from specific series: series_slug="my-series", count=100
        - Optimize for large batches: count=5000, batch_size=2000
    """
    # Handle empty string as "not provided"
    logger.info(f"Mint tool called - series: {series_slug or 'default'}, count: {count}, batch_size: {batch_size}")
    try:
        client = get_client_for_session(ctx)
        series = client.series
        if series_slug:
            series = series[series_slug]

        generator = series.mint.with_batch_size(batch_size).with_limit(count)
        result: list[str] = []
        async for slug in generator:
            result.append(slug)

        logger.debug(f"Successfully minted {len(result)} slugs")
        return result
    except Exception as e:
        logger.error(f"Error minting slugs: {str(e)}")
        return [f"Error minting slugs: {str(e)}"]


@mcp.tool()
async def slice(
    *,
    series_slug: str = "",
    count: int = 1,
    batch_size: int = 1000,
    sequence: int = 0,
    ctx: Context[AppContext, ServerSession],
) -> list[str]:
    """
    Slice (dry-run preview) slugs from a series without actually consuming them.

    Slicing provides a preview of what slugs would be generated without affecting
    the series state. This is useful for testing, validation, or planning purposes.

    Args:
        series_slug: The slug identifier of the series to slice from (optional)
                    If not provided, slices from the default/current series
        count: Number of slugs to preview (default: 1, max: 10000)
        batch_size: Internal batch size for efficient processing (default: 1000)
        sequence: Starting sequence number for reproducible slicing (default: 0)
                 Same sequence will always produce the same results

    Returns:
        list[str]: List of previewed slugs (these are NOT consumed from the series)

    Use this tool when you want to see what slugs would be generated without
    actually minting them. This is perfect for testing patterns, validating
    output, or planning slug usage without consuming series capacity.

    Examples:
        - Preview 10 slugs: count=10
        - Preview from specific sequence: sequence=100, count=5
        - Preview from specific series: series_slug="my-series", count=20
    """
    try:
        # Handle empty string as "not provided"
        logger.info(
            f"Slicing tool called - series: {series_slug or 'default'}, count: {count}, batch_size: {batch_size}, sequence: {sequence}"
        )
        client = get_client_for_session(ctx)
        series = client.series
        if series_slug:
            series = series[series_slug]
        generator = series.slice.with_batch_size(batch_size).with_limit(count).starting_from(sequence)
        result: list[str] = []
        async for slug in generator:
            result.append(slug)
        return result
    except Exception as e:
        return [f"Error slicing slugs: {str(e)}"]


@mcp.tool()
async def analyze_pattern(
    *,
    pattern: str,
    ctx: Context[AppContext, ServerSession],
) -> dict:
    """
    Analyze a SlugKit pattern to understand its characteristics and capabilities.

    This tool provides detailed analysis of a pattern's structure, capacity,
    and characteristics without performing validation. It's useful for understanding
    pattern design and planning slug generation strategies.

    Args:
        pattern: The SlugKit pattern string to analyze (required)
                Examples: "{adjective}-{noun}", "{adjective}-{noun}-{number:4d}"

    Returns:
        dict: Pattern analysis including:
            - pattern: The analyzed pattern string
            - capacity: Total possible unique combinations
            - capacity_formatted: Human-readable capacity (e.g., "1.2M", "500K")
            - max_slug_length: Maximum length of generated slugs
            - complexity: Pattern complexity score (higher = more complex)
            - components: Number of placeholder components
            - uniqueness_score: Relative uniqueness rating
            - recommendations: Suggestions for optimization

    Use this tool to evaluate pattern designs and understand their scalability
    before implementing them in production systems. This is analysis-focused,
    unlike validate_pattern() which performs validation.

    Examples:
        - Simple pattern: "{adjective}-{noun}" -> low complexity, high capacity
        - Complex pattern: "{adjective}-{noun}-{number:4d}[==15]" -> high complexity, constrained
    """
    logger.info(f"Analyze pattern tool called - pattern: {pattern}")
    try:
        client = get_client_for_session(ctx)
        pattern_info = await client.forge.pattern_info(pattern)

        # Format capacity for readability with proper SI prefixes
        capacity = int(pattern_info.capacity)
        if capacity >= 1_000_000_000_000_000_000:  # 10^18 (quintillion)
            capacity_formatted = f"{capacity / 1_000_000_000_000_000_000:.2f}Qi"
        elif capacity >= 1_000_000_000_000_000:  # 10^15 (quadrillion)
            capacity_formatted = f"{capacity / 1_000_000_000_000_000:.2f}Qa"
        elif capacity >= 1_000_000_000_000:  # 10^12 (trillion)
            capacity_formatted = f"{capacity / 1_000_000_000_000:.2f}T"
        elif capacity >= 1_000_000_000:  # 10^9 (billion)
            capacity_formatted = f"{capacity / 1_000_000_000:.2f}B"
        elif capacity >= 1_000_000:  # 10^6 (million)
            capacity_formatted = f"{capacity / 1_000_000:.2f}M"
        elif capacity >= 1_000:  # 10^3 (thousand)
            capacity_formatted = f"{capacity / 1_000:.0f}K"
        else:
            capacity_formatted = str(capacity)

        # Fallback for extremely large numbers
        if capacity >= 1_000_000_000_000_000_000_000:  # 10^21
            import math

            power = int(math.log10(capacity))
            capacity_formatted = f"10^{power}"

            # Calculate uniqueness score based on actual complexity ranges
        if capacity >= 1_000_000_000_000_000_000:  # 10^18 (quintillion)
            uniqueness_score = "Astronomically High"
        elif capacity >= 1_000_000_000_000_000:  # 10^15 (quadrillion)
            uniqueness_score = "Extremely High"
        elif capacity >= 1_000_000_000_000:  # 10^12 (trillion)
            uniqueness_score = "Very High"
        elif capacity >= 1_000_000_000:  # 10^9 (billion)
            uniqueness_score = "High"
        elif capacity >= 1_000_000:  # 10^6 (million)
            uniqueness_score = "Medium"
        elif capacity >= 10_000:  # 10^4 (thousand)
            uniqueness_score = "Low"
        else:
            uniqueness_score = "Very Low"

        # Generate recommendations based on actual complexity ranges
        recommendations = []
        if capacity < 100_000:
            recommendations.append("Consider adding more components or using larger number ranges")
        if pattern_info.complexity > 30:
            recommendations.append("Pattern is very complex - consider simplifying for better performance")
        elif pattern_info.complexity > 20:
            recommendations.append("Pattern is complex - monitor performance")
        if pattern_info.max_slug_length > 50:
            recommendations.append("Generated slugs may be long - consider length constraints")

        logger.debug(
            f"Pattern analysis successful - pattern: {pattern}, capacity: {capacity_formatted}, complexity: {pattern_info.complexity}"
        )
        return {
            "pattern": pattern,
            "total_capacity": capacity,
            "capacity_formatted": capacity_formatted,
            "uniqueness_score": uniqueness_score,
            "max_slug_length": pattern_info.max_slug_length,
            "complexity": pattern_info.complexity,
            "components": pattern_info.components,
            "recommendations": recommendations,
        }

    except Exception as e:
        logger.error(f"Pattern analysis failed for '{pattern}': {str(e)}")
        return {"error": f"Pattern analysis failed: {str(e)}", "pattern": pattern}


@mcp.tool()
async def compare_patterns(
    *,
    patterns: list[str],
    count_per_pattern: int = 3,
    seed: str = "",
    ctx: Context[AppContext, ServerSession],
) -> dict:
    """
    Compare multiple SlugKit patterns by generating sample slugs from each.

    This tool is useful when you need to evaluate different pattern designs
    or compare pattern outputs for selection purposes. It generates the same
    number of slugs from each pattern for fair comparison.

    Args:
        patterns: List of SlugKit pattern strings to compare (required)
                 Each pattern will generate the specified number of slugs
        count_per_pattern: Number of slugs to generate per pattern (default: 3)
        seed: Optional seed string for reproducible generation across all patterns

    Returns:
        dict: Comparison results including:
            - comparison: Dictionary mapping each pattern to its generated slugs
            - analysis: Pattern analysis for each pattern
            - recommendations: Suggestions for pattern selection

    Use this tool when you need to compare outputs from different patterns
    or generate variations for testing and selection purposes.

    Examples:
        - Compare 2 patterns: patterns=["{adjective}-{noun}", "{verb}-{noun}"]
        - Use seed for reproducible comparison: seed="test", count_per_pattern=5
    """
    # Handle empty string as "not provided"
    actual_seed = None if seed == "" else seed

    logger.info(
        f"Compare patterns tool called - patterns: {patterns}, count_per_pattern: {count_per_pattern}, seed: {actual_seed}"
    )
    try:
        client = get_client_for_session(ctx)
        results = {}
        analysis = {}

        for pattern in patterns:
            try:
                # Generate slugs
                slugs = await client.forge(pattern, seed=actual_seed, count=count_per_pattern)
                results[pattern] = slugs

                # Get pattern analysis
                pattern_info = await client.forge.pattern_info(pattern)
                analysis[pattern] = {
                    "capacity": pattern_info.capacity,
                    "max_slug_length": pattern_info.max_slug_length,
                    "complexity": pattern_info.complexity,
                    "components": pattern_info.components,
                }
            except Exception as e:
                results[pattern] = [f"Error: {str(e)}"]
                analysis[pattern] = {"error": str(e)}

                # Generate recommendations based on actual complexity ranges
        recommendations = []
        if len(patterns) > 1:
            capacities = [int(analysis[p].get("capacity", 0)) for p in patterns if "capacity" in analysis[p]]
            if capacities:
                max_capacity = max(capacities)
                min_capacity = min(capacities)
                if max_capacity / min_capacity > 1000:  # More realistic threshold
                    recommendations.append(
                        "Patterns have significantly different capacities - consider this for scalability"
                    )

            complexities = [analysis[p].get("complexity", 0) for p in patterns if "complexity" in analysis[p]]
            if complexities:
                avg_complexity = sum(complexities) / len(complexities)
                if avg_complexity > 30:
                    recommendations.append(
                        "Some patterns are very complex - consider simplifying for better performance"
                    )
                elif avg_complexity > 20:
                    recommendations.append("Patterns have moderate complexity - monitor performance")

        logger.debug(f"Pattern comparison successful - compared {len(patterns)} patterns")
        return {"comparison": results, "analysis": analysis, "recommendations": recommendations}

    except Exception as e:
        logger.error(f"Pattern comparison failed: {str(e)}")
        return {"error": f"Pattern comparison failed: {str(e)}"}


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--help", action="help", help=argparse.SUPPRESS)
    parser.add_argument(
        "--log-level", "-l", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO"
    )
    parser.add_argument("--transport", "-t", type=str, choices=["http", "stdio"], default="stdio")
    http_group = parser.add_argument_group("HTTP Transport Options")

    http_group.add_argument(
        "--host", "-h", type=str, default=os.getenv("SLUGKIT_MCP_HOST", "0.0.0.0"), help="Host interface to bind to"
    )
    http_group.add_argument(
        "--port", "-p", type=int, default=int(os.getenv("SLUGKIT_MCP_PORT", 5000)), help="Port to listen on"
    )
    http_group.add_argument("--path", "-P", type=str, default=os.getenv("SLUGKIT_MCP_PATH", "/mcp"), help="Mount path")
    return parser.parse_args()


def main():
    args = parse_args()
    log_level = logging._nameToLevel[args.log_level]
    logging.basicConfig(level=log_level, format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s")
    # Suppress httpx logs
    logging.getLogger("httpx").setLevel(logging.ERROR)
    if args.transport == "http":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.settings.streamable_http_path = args.path
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
