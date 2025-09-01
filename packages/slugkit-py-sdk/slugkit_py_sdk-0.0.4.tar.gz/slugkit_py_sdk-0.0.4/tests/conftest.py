import pytest
import asyncio
import logging
from slugkit import SyncClient, AsyncClient


# Test configuration constants
BASE_URL = "https://dev.slugkit.dev/api/v1"
SERIES_API_KEY = "ik-H4m1ahqk8xaUtxe0QJ15ydnGxjXGjukomlMOVpTPsJg="
ORG_API_KEY = "ik-/Ai9BzzlZwShGC49u//XmHeCidWkpkmjICrNmGX6qVU="
SERIES_SLUG = "whole-blond-rower-a597"

# Known test series
TEST_SERIES_1 = "test-series-1"
TEST_SERIES_2 = "test-series-2"

# Setup logging
logging.basicConfig(level=logging.INFO)


@pytest.fixture
def base_url():
    """Base URL for SlugKit API."""
    return BASE_URL


@pytest.fixture
def series_api_key():
    """API key for series-level access."""
    return SERIES_API_KEY


@pytest.fixture
def org_api_key():
    """API key for organization-level access."""
    return ORG_API_KEY


@pytest.fixture
def series_slug():
    """Test series slug."""
    return SERIES_SLUG


@pytest.fixture
def sync_client_series(base_url, series_api_key):
    """Sync client configured with series API key."""
    return SyncClient(base_url=base_url, api_key=series_api_key)


@pytest.fixture
def sync_client_org(base_url, org_api_key):
    """Sync client configured with organization API key."""
    return SyncClient(base_url=base_url, api_key=org_api_key)


@pytest.fixture
def async_client_series(base_url, series_api_key):
    """Async client configured with series API key."""
    return AsyncClient(base_url=base_url, api_key=series_api_key)


@pytest.fixture
def async_client_org(base_url, org_api_key):
    """Async client configured with organization API key."""
    return AsyncClient(base_url=base_url, api_key=org_api_key)


@pytest.fixture
def test_pattern():
    """A test pattern for forge operations."""
    return "test-{adjective}-{noun}-{number:4,hex}"


@pytest.fixture
def test_seed():
    """A test seed for reproducible pattern generation."""
    return "pytest-test-seed"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
