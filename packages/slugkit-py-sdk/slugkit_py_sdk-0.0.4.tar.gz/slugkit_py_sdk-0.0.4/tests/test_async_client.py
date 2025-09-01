import pytest
from unittest.mock import AsyncMock, Mock
import httpx

from slugkit.async_client import AsyncClient, AsyncSlugGenerator, AsyncRandomGenerator, AsyncSeriesClient
from slugkit.base import StatsItem, SeriesInfo, PatternInfo, DictionaryInfo, DictionaryTag


class TestAsyncClient:
    """Tests for the AsyncClient class."""

    @pytest.mark.asyncio
    async def test_async_client_initialization(self):
        """Test AsyncClient initialization."""
        client = AsyncClient("http://localhost:8000", "test-api-key")
        assert client.base_url == "http://localhost:8000"
        assert client.api_key == "test-api-key"

    @pytest.mark.asyncio
    async def test_async_client_series_property(self):
        """Test AsyncClient series property."""
        client = AsyncClient("http://localhost:8000", "test-api-key")
        series_client = client.series
        assert hasattr(series_client, "mint")
        assert hasattr(series_client, "slice")
        assert hasattr(series_client, "stats")
        assert hasattr(series_client, "info")
        assert hasattr(series_client, "list")
        assert hasattr(series_client, "reset")

    @pytest.mark.asyncio
    async def test_async_client_forge_property(self):
        """Test AsyncClient forge property."""
        client = AsyncClient("http://localhost:8000", "test-api-key")
        forge_client = client.forge
        assert hasattr(forge_client, "pattern_info")
        assert hasattr(forge_client, "dictionary_info")
        assert hasattr(forge_client, "dictionary_tags")

    @pytest.mark.asyncio
    async def test_async_client_series_access(self):
        """Test AsyncClient series access via __getitem__."""
        client = AsyncClient("http://localhost:8000", "test-api-key")
        series_client = client.series["test-series"]
        assert isinstance(series_client, AsyncSeriesClient)
        assert series_client._series == "test-series"

    @pytest.mark.asyncio
    async def test_ping_success(self, async_client_series):
        """Test successful ping to the API."""
        # This should work with a valid client
        await async_client_series.ping()
        # If we get here without exception, ping succeeded

    @pytest.mark.asyncio
    async def test_ping_without_api_key(self, base_url):
        """Test ping fails without API key."""
        client = AsyncClient(base_url=base_url)
        with pytest.raises(TypeError, match="Header value must be str or bytes, not <class 'NoneType'>"):
            await client.ping()

    @pytest.mark.asyncio
    async def test_key_info_success(self, async_client_series):
        """Test successful key info retrieval."""
        key_info = await async_client_series.key_info()

        # Verify the structure of KeyInfo
        assert hasattr(key_info, "type")
        assert hasattr(key_info, "key_scope")
        assert hasattr(key_info, "slug")
        assert hasattr(key_info, "org_slug")
        assert hasattr(key_info, "scopes")
        assert hasattr(key_info, "enabled")

        # Verify key is enabled
        assert key_info.enabled is True

        # Verify scopes contain expected operations
        expected_scopes = ["forge", "mint", "slice", "reset", "stats"]
        for scope in expected_scopes:
            assert scope in key_info.scopes

    @pytest.mark.asyncio
    async def test_key_info_without_api_key(self, base_url):
        """Test key info fails without API key."""
        client = AsyncClient(base_url=base_url)
        with pytest.raises(ValueError, match="API key is required"):
            await client.key_info()

    @pytest.mark.asyncio
    async def test_key_info_scope_validation(self, async_client_series):
        """Test that key info returns valid scope values."""
        key_info = await async_client_series.key_info()

        # Verify key_scope is one of the expected values
        assert key_info.key_scope.value in ["org", "series"]

        # Verify slug is not empty
        assert len(key_info.slug) > 0

        # Verify org_slug is not empty
        assert len(key_info.org_slug) > 0


class TestAsyncSlugGenerator:
    """Tests for the AsyncSlugGenerator class."""

    @pytest.mark.asyncio
    async def test_async_generator_basic_interface(self):
        """Test AsyncSlugGenerator basic async generator interface."""
        # Test that the generator has the required async iterator methods
        mock_http_client = AsyncMock()
        generator = AsyncSlugGenerator(mock_http_client, limit=3, batch_size=2)

        # Test that it's iterable
        assert hasattr(generator, "__aiter__")
        assert callable(generator.__aiter__)

        # Test that the stream method exists and is callable
        assert hasattr(generator, "stream")
        assert callable(generator.stream)

        # Test that the generator has the expected attributes
        assert generator._limit == 3
        assert generator._batch_size == 2
        assert generator._dry_run is False
        assert generator._sequence == 0

    @pytest.mark.asyncio
    async def test_async_generator_stream_method(self):
        """Test AsyncSlugGenerator stream method exists and is callable."""
        mock_http_client = AsyncMock()
        generator = AsyncSlugGenerator(mock_http_client, limit=3, batch_size=2)

        # Test that the stream method exists and is callable
        assert hasattr(generator, "stream")
        assert callable(generator.stream)

        # Test that calling stream() returns an async generator
        stream_gen = generator.stream()
        assert hasattr(stream_gen, "__aiter__")
        assert callable(stream_gen.__aiter__)

    @pytest.mark.asyncio
    async def test_async_generator_configuration(self):
        """Test AsyncSlugGenerator configuration options."""
        mock_http_client = AsyncMock()

        # Test with various configuration options
        generator = AsyncSlugGenerator(
            mock_http_client, series_slug="test-series", limit=10, batch_size=5, dry_run=True, sequence=100
        )

        assert generator._series_slug == "test-series"
        assert generator._limit == 10
        assert generator._batch_size == 5
        assert generator._dry_run is True
        assert generator._sequence == 100

    @pytest.mark.asyncio
    async def test_async_generator_with_series(self):
        """Test AsyncSlugGenerator with_series method."""
        mock_http_client = AsyncMock()
        generator = AsyncSlugGenerator(mock_http_client)

        # Test that with_series returns a new generator with series_slug set
        series_generator = generator.with_series("test-series")
        assert series_generator._series_slug == "test-series"
        assert series_generator is not generator  # Should be a new instance

    @pytest.mark.asyncio
    async def test_async_generator_with_dry_run(self):
        """Test AsyncSlugGenerator with_dry_run method."""
        mock_http_client = AsyncMock()
        generator = AsyncSlugGenerator(mock_http_client)

        # Test that with_dry_run returns a new generator with dry_run set
        dry_run_generator = generator.with_dry_run()
        assert dry_run_generator._dry_run is True
        assert dry_run_generator is not generator  # Should be a new instance

    @pytest.mark.asyncio
    async def test_async_generator_call_method(self):
        """Test AsyncSlugGenerator __call__ method."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_ids = ["test-1", "test-2"]
        mock_response.json.return_value = expected_ids
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        generator = AsyncSlugGenerator(mock_http_client, series_slug="test-series")
        ids = await generator(count=2)

        assert isinstance(ids, list)
        assert len(ids) == 2
        assert ids == expected_ids

        # Verify the API was called with series configuration
        mock_http_client.return_value.post.assert_called_once()
        call_args = mock_http_client.return_value.post.call_args
        assert call_args[1]["json"]["series"] == "test-series"
        assert call_args[1]["json"]["count"] == 2


class TestAsyncRandomGenerator:
    """Tests for the AsyncRandomGenerator class."""

    @pytest.mark.asyncio
    async def test_async_forge_basic(self, test_pattern):
        """Test basic forge functionality."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_ids = ["simple-cat-ab", "simple-dog-cd"]
        mock_response.json.return_value = expected_ids
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)
        ids = await generator(pattern=test_pattern, count=2)

        assert isinstance(ids, list)
        assert len(ids) == 2
        assert ids == expected_ids

        # Verify the API was called correctly
        mock_http_client.return_value.post.assert_called_once()
        call_args = mock_http_client.return_value.post.call_args
        assert call_args[1]["json"]["pattern"] == test_pattern
        assert call_args[1]["json"]["count"] == 2

    @pytest.mark.asyncio
    async def test_async_forge_with_seed(self, test_pattern):
        """Test forge with seed parameter."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_ids = ["seeded-result-1", "seeded-result-2"]
        mock_response.json.return_value = expected_ids
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)
        test_seed = "test-seed-123"
        ids = await generator(pattern=test_pattern, seed=test_seed, count=2)

        assert isinstance(ids, list)
        assert len(ids) == 2
        assert ids == expected_ids

        # Verify the API was called with seed
        mock_http_client.return_value.post.assert_called_once()
        call_args = mock_http_client.return_value.post.call_args
        assert call_args[1]["json"]["seed"] == test_seed

    @pytest.mark.asyncio
    async def test_async_forge_with_sequence(self, test_pattern):
        """Test forge with sequence parameter."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_ids = ["seq-100", "seq-101"]
        mock_response.json.return_value = expected_ids
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)
        ids = await generator(pattern=test_pattern, sequence=100, count=2)

        assert isinstance(ids, list)
        assert len(ids) == 2
        assert ids == expected_ids

        # Verify the API was called with sequence
        mock_http_client.return_value.post.assert_called_once()
        call_args = mock_http_client.return_value.post.call_args
        assert call_args[1]["json"]["sequence"] == 100

    @pytest.mark.asyncio
    async def test_async_forge_deterministic(self, test_pattern):
        """Test that forge with same parameters returns same results."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_ids = ["deterministic-1", "deterministic-2"]
        mock_response.json.return_value = expected_ids
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)
        test_seed = "deterministic-seed"
        ids1 = await generator(pattern=test_pattern, seed=test_seed, sequence=1, count=2)

        # Reset mock for second call
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        ids2 = await generator(pattern=test_pattern, seed=test_seed, sequence=1, count=2)

        assert ids1 == ids2
        assert ids1 == expected_ids

    @pytest.mark.asyncio
    async def test_async_forge_with_optional_params(self, test_pattern):
        """Test forge with various optional parameters."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = ["simple-cat-ab"]
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)

        # Test with minimal parameters
        ids = await generator(pattern=test_pattern, count=1)
        assert isinstance(ids, list)
        assert len(ids) == 1

        # Verify the API was called with correct parameters
        call_args = mock_http_client.return_value.post.call_args
        assert call_args[1]["json"]["pattern"] == test_pattern
        assert call_args[1]["json"]["count"] == 1

    @pytest.mark.asyncio
    async def test_async_pattern_info(self, test_pattern):
        """Test getting pattern information asynchronously."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_pattern_info = {
            "pattern": "test-{adjective}-{noun}-{number:3d}",
            "capacity": "1000000",
            "max_slug_length": 25,
            "complexity": 3,
            "components": 3,
        }
        mock_response.json.return_value = expected_pattern_info
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)
        pattern_info = await generator.pattern_info(test_pattern)

        assert isinstance(pattern_info, PatternInfo)
        assert pattern_info.pattern == "test-{adjective}-{noun}-{number:3d}"
        assert pattern_info.capacity == "1000000"
        assert pattern_info.max_slug_length == 25
        assert pattern_info.complexity == 3
        assert pattern_info.components == 3

    @pytest.mark.asyncio
    async def test_async_dictionary_info(self, test_pattern):
        """Test getting dictionary information asynchronously."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_dict_info = [
            {"kind": "adjective", "count": 1000},
            {"kind": "noun", "count": 2000},
            {"kind": "verb", "count": 1500},
        ]
        mock_response.json.return_value = expected_dict_info
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.get = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)
        dict_info = await generator.dictionary_info()

        assert isinstance(dict_info, list)
        assert len(dict_info) == 3
        for item in dict_info:
            assert isinstance(item, DictionaryInfo)
            assert item.kind in ["adjective", "noun", "verb"]
            assert item.count > 0

    @pytest.mark.asyncio
    async def test_async_dictionary_tags(self, test_pattern):
        """Test getting dictionary tags asynchronously."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_dict_tags = [
            {
                "kind": "adjective",
                "tag": "positive",
                "description": "Positive adjectives",
                "opt_in": True,
                "word_count": 500,
            },
            {"kind": "noun", "tag": "animals", "description": "Animal names", "opt_in": False, "word_count": 300},
        ]
        mock_response.json.return_value = expected_dict_tags
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.get = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)
        dict_tags = await generator.dictionary_tags()

        assert isinstance(dict_tags, list)
        assert len(dict_tags) == 2
        for item in dict_tags:
            assert isinstance(item, DictionaryTag)
            assert item.kind in ["adjective", "noun"]
            assert hasattr(item, "tag")
            assert hasattr(item, "description")
            assert hasattr(item, "opt_in")
            assert hasattr(item, "word_count")


class TestAsyncErrorHandling:
    """Tests for error handling in async operations."""

    @pytest.mark.asyncio
    async def test_async_http_error_handling(self):
        """Test HTTP error handling in async operations."""
        mock_http_client = AsyncMock()
        mock_http_client.return_value.post = AsyncMock(
            side_effect=httpx.HTTPStatusError("404 Not Found", request=Mock(), response=Mock())
        )

        generator = AsyncRandomGenerator(mock_http_client)

        with pytest.raises(httpx.HTTPStatusError):
            await generator(pattern="test-{noun}", count=1)

    @pytest.mark.asyncio
    async def test_async_invalid_json_response(self):
        """Test handling of invalid JSON responses."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)

        with pytest.raises(ValueError):
            await generator(pattern="test-{noun}", count=1)


class TestAsyncEdgeCases:
    """Tests for edge cases in async operations."""

    @pytest.mark.asyncio
    async def test_async_empty_response(self):
        """Test handling of empty responses."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)
        ids = await generator(pattern="test-{noun}", count=5)

        assert isinstance(ids, list)
        assert len(ids) == 0

    @pytest.mark.asyncio
    async def test_async_large_count(self):
        """Test handling of large count values."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = ["slug"] * 1000
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        generator = AsyncRandomGenerator(mock_http_client)
        ids = await generator(pattern="test-{noun}", count=1000)

        assert isinstance(ids, list)
        assert len(ids) == 1000
        assert all(isinstance(id_, str) for id_ in ids)


class TestAsyncIntegration:
    """Integration tests for AsyncClient operations."""

    @pytest.mark.asyncio
    async def test_async_client_mint_operation(self):
        """Test async minting via client.series.mint."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_ids = ["mint-1", "mint-2"]
        mock_response.json.return_value = expected_ids
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        client = AsyncClient("http://localhost:8000", "test-api-key")
        client._http_client = mock_http_client

        ids = await client.series.mint(count=2)

        assert isinstance(ids, list)
        assert len(ids) == 2
        assert ids == expected_ids

    @pytest.mark.asyncio
    async def test_async_client_slice_operation(self):
        """Test async slicing via client.series.slice."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_ids = ["slice-1", "slice-2"]
        mock_response.json.return_value = expected_ids
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        client = AsyncClient("http://localhost:8000", "test-api-key")
        client._http_client = mock_http_client

        ids = await client.series.slice(count=2)

        assert isinstance(ids, list)
        assert len(ids) == 2
        assert ids == expected_ids

    @pytest.mark.asyncio
    async def test_async_client_forge_operation(self):
        """Test async forging via client.forge."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_ids = ["forge-1", "forge-2"]
        mock_response.json.return_value = expected_ids
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        client = AsyncClient("http://localhost:8000", "test-api-key")
        client._http_client = mock_http_client

        ids = await client.forge(pattern="test-{noun}", count=2)

        assert isinstance(ids, list)
        assert len(ids) == 2
        assert ids == expected_ids

    @pytest.mark.asyncio
    async def test_async_client_series_access(self):
        """Test accessing specific series via client.series['slug']."""
        mock_http_client = AsyncMock()
        mock_response = Mock()
        expected_ids = ["series-1", "series-2"]
        mock_response.json.return_value = expected_ids
        mock_response.raise_for_status.return_value = None
        mock_http_client.return_value.post = AsyncMock(return_value=mock_response)

        client = AsyncClient("http://localhost:8000", "test-api-key")
        client._http_client = mock_http_client

        series_client = client.series["test-series"]
        ids = await series_client.mint(count=2)

        assert isinstance(ids, list)
        assert len(ids) == 2
        assert ids == expected_ids

    @pytest.mark.asyncio
    async def test_async_client_error_handling(self):
        """Test HTTP error handling in async client operations."""
        mock_http_client = AsyncMock()
        mock_http_client.return_value.post = AsyncMock(
            side_effect=httpx.HTTPStatusError("500 Internal Server Error", request=Mock(), response=Mock())
        )

        client = AsyncClient("http://localhost:8000", "test-api-key")
        client._http_client = mock_http_client

        with pytest.raises(httpx.HTTPStatusError):
            await client.series.mint(count=1)

    @pytest.mark.asyncio
    async def test_async_client_api_key_validation(self):
        """Test API key requirement for async client operations."""
        client = AsyncClient("http://localhost:8000", None)

        with pytest.raises(ValueError, match="API key is required"):
            await client.series.mint(count=1)

        with pytest.raises(ValueError, match="API key is required"):
            await client.series.slice(count=1)

        with pytest.raises(ValueError, match="API key is required"):
            await client.forge(pattern="test-{noun}", count=1)


class TestAsyncLiveIntegration:
    """Live integration tests that make real API calls and test actual streaming."""

    @pytest.mark.asyncio
    async def test_live_async_forge_streaming(self, async_client_series, test_pattern):
        """Test live async forge with real streaming of IDs."""
        # Test basic forge functionality with real streaming
        ids = await async_client_series.forge(pattern=test_pattern, count=5)

        assert isinstance(ids, list)
        assert len(ids) == 5
        assert all(isinstance(id_, str) for id_ in ids)
        assert all(len(id_) > 0 for id_ in ids)

        # Verify we got actual unique IDs
        assert len(set(ids)) == 5  # All should be unique
        print(f"Generated IDs: {ids}")

    @pytest.mark.asyncio
    async def test_live_async_series_mint_streaming(self, async_client_series, series_slug):
        """Test live async series minting with real streaming of IDs."""
        # Test minting from a specific series with real streaming
        series_client = async_client_series.series[series_slug]

        # Mint 3 IDs from the series
        ids = await series_client.mint(count=3)

        assert isinstance(ids, list)
        assert len(ids) == 3
        assert all(isinstance(id_, str) for id_ in ids)
        assert all(len(id_) > 0 for id_ in ids)

        # Verify we got actual unique IDs
        assert len(set(ids)) == 3  # All should be unique
        print(f"Minted IDs from series {series_slug}: {ids}")

    @pytest.mark.asyncio
    async def test_live_async_series_slice_streaming(self, async_client_series, series_slug):
        """Test live async series slicing with real streaming of IDs."""
        # Test slicing (dry run) from a specific series with real streaming
        series_client = async_client_series.series[series_slug]

        # Slice 3 IDs from the series
        ids = await series_client.slice(count=3)

        assert isinstance(ids, list)
        assert len(ids) == 3
        assert all(isinstance(id_, str) for id_ in ids)
        assert all(len(id_) > 0 for id_ in ids)

        # Verify we got actual unique IDs
        assert len(set(ids)) == 3  # All should be unique
        print(f"Sliced IDs from series {series_slug}: {ids}")

    @pytest.mark.asyncio
    async def test_live_async_generator_real_streaming(self, async_client_series, series_slug):
        """Test live async generator with real streaming iteration."""
        # Test the actual AsyncSlugGenerator streaming interface
        series_client = async_client_series.series[series_slug]
        generator = series_client.mint

        # Set a reasonable limit to avoid long-running tests
        generator = generator.with_limit(5).with_batch_size(2)

        # Actually iterate over the async generator
        collected_ids = []
        async for id_ in generator:
            collected_ids.append(id_)
            print(f"Streamed ID: {id_}")
            if len(collected_ids) >= 5:  # Limit to 5 for test performance
                break

        # Should have collected some actual IDs
        assert len(collected_ids) > 0
        assert all(isinstance(id_, str) for id_ in collected_ids)
        assert all(len(id_) > 0 for id_ in collected_ids)

        # Verify we got actual unique IDs
        assert len(set(collected_ids)) == len(collected_ids)  # All should be unique
        print(f"Total streamed IDs: {collected_ids}")

    @pytest.mark.asyncio
    async def test_live_async_generator_stream_method(self, async_client_series, series_slug):
        """Test live async generator stream method with real streaming."""
        # Test the stream method directly
        series_client = async_client_series.series[series_slug]
        generator = series_client.mint

        # Set a reasonable limit
        generator = generator.with_limit(4).with_batch_size(2)

        # Use the stream method directly
        stream_gen = generator.stream()

        # Actually iterate over the stream
        collected_ids = []
        async for id_ in stream_gen:
            collected_ids.append(id_)
            print(f"Stream method ID: {id_}")
            if len(collected_ids) >= 4:  # Limit to 4 for test performance
                break

        # Should have collected some actual IDs
        assert len(collected_ids) > 0
        assert all(isinstance(id_, str) for id_ in collected_ids)
        assert all(len(id_) > 0 for id_ in collected_ids)

        # Verify we got actual unique IDs
        assert len(set(collected_ids)) == len(collected_ids)  # All should be unique
        print(f"Total stream method IDs: {collected_ids}")

    @pytest.mark.asyncio
    async def test_live_async_forge_with_seed_reproducibility(self, async_client_series, test_pattern, test_seed):
        """Test live async forge with seed for actual reproducibility."""
        # Test forge with seed - should be deterministic
        ids1 = await async_client_series.forge(pattern=test_pattern, seed=test_seed, count=3)
        ids2 = await async_client_series.forge(pattern=test_pattern, seed=test_seed, count=3)

        assert isinstance(ids1, list)
        assert isinstance(ids2, list)
        assert len(ids1) == 3
        assert len(ids2) == 3

        # With same seed, should get same results
        assert ids1 == ids2

        # Verify we got actual unique IDs
        assert len(set(ids1)) == 3  # All should be unique
        print(f"Seed {test_seed} generated IDs: {ids1}")

    @pytest.mark.asyncio
    async def test_live_async_forge_with_sequence(self, async_client_series, test_pattern):
        """Test live async forge with sequence parameter for actual ID generation."""
        # Test forge with sequence
        ids = await async_client_series.forge(pattern=test_pattern, sequence=100, count=3)

        assert isinstance(ids, list)
        assert len(ids) == 3
        assert all(isinstance(id_, str) for id_ in ids)
        assert all(len(id_) > 0 for id_ in ids)

        # Verify we got actual unique IDs
        assert len(set(ids)) == 3  # All should be unique
        print(f"Sequence 100 generated IDs: {ids}")

    @pytest.mark.asyncio
    async def test_live_async_large_batch_streaming(self, async_client_series, test_pattern):
        """Test live async forge with larger batch for real streaming performance."""
        import time

        # Test with a larger batch to see real streaming performance
        start_time = time.time()

        ids = await async_client_series.forge(pattern=test_pattern, count=10)

        end_time = time.time()
        total_time = end_time - start_time

        assert isinstance(ids, list)
        assert len(ids) == 10
        assert all(isinstance(id_, str) for id_ in ids)
        assert all(len(id_) > 0 for id_ in ids)

        # Verify we got actual unique IDs
        assert len(set(ids)) == 10  # All should be unique

        # Should complete reasonably quickly
        assert total_time < 5.0  # Under 5 seconds for 10 IDs

        print(f"Large batch generated {len(ids)} IDs in {total_time:.2f}s: {ids[:5]}...")

    @pytest.mark.asyncio
    async def test_live_async_series_stats_after_generation(self, async_client_series, series_slug):
        """Test live async series stats after generating IDs to see real data."""
        # First generate some IDs to create activity
        series_client = async_client_series.series[series_slug]
        ids = await series_client.mint(count=2)

        # Then check stats to see the real data
        stats = await async_client_series.series.stats()

        assert isinstance(stats, list)
        # Stats should reflect the recent activity
        for item in stats:
            assert isinstance(item, StatsItem)
            assert hasattr(item, "event_type")
            assert hasattr(item, "date_part")
            assert hasattr(item, "total_count")
            assert hasattr(item, "request_count")
            assert hasattr(item, "total_duration_us")
            assert hasattr(item, "avg_duration_us")

        print(f"Stats after generating {len(ids)} IDs: {[s.event_type for s in stats]}")

    @pytest.mark.asyncio
    async def test_live_async_series_info_real_data(self, async_client_series, series_slug):
        """Test live async series info with real data."""
        series_info = await async_client_series.series.info()

        assert isinstance(series_info, SeriesInfo)
        assert hasattr(series_info, "slug")
        assert hasattr(series_info, "org_slug")
        assert hasattr(series_info, "pattern")
        assert hasattr(series_info, "max_pattern_length")
        assert hasattr(series_info, "capacity")
        assert hasattr(series_info, "generated_count")
        assert hasattr(series_info, "mtime")

        # Verify we got real data
        assert series_info.slug == series_slug
        assert len(series_info.pattern) > 0
        assert series_info.max_pattern_length > 0
        assert int(series_info.capacity) > 0

        print(f"Series info: {series_info.slug}, pattern: {series_info.pattern}, capacity: {series_info.capacity}")

    @pytest.mark.asyncio
    async def test_live_async_dictionary_info_real_data(self, async_client_series):
        """Test live async dictionary info with real data."""
        dict_info = await async_client_series.forge.dictionary_info()

        assert isinstance(dict_info, list)
        assert len(dict_info) > 0

        for item in dict_info:
            assert isinstance(item, DictionaryInfo)
            assert hasattr(item, "kind")
            assert hasattr(item, "count")
            assert item.count > 0

        # Print actual dictionary data
        for item in dict_info:
            print(f"Dictionary: {item.kind} - {item.count} words")

    @pytest.mark.asyncio
    async def test_live_async_performance_real_streaming(self, async_client_series, test_pattern):
        """Test live async performance with real streaming."""
        import time

        # Test performance of multiple streaming requests
        start_time = time.time()

        # Make several streaming requests
        all_ids = []
        for i in range(3):
            ids = await async_client_series.forge(pattern=test_pattern, count=3)
            assert isinstance(ids, list)
            assert len(ids) == 3
            all_ids.extend(ids)

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete reasonably quickly
        assert total_time < 10.0

        # Verify we got actual unique IDs
        assert len(set(all_ids)) == len(all_ids)  # All should be unique
        print(f"Generated {len(all_ids)} IDs in {total_time:.2f}s")
