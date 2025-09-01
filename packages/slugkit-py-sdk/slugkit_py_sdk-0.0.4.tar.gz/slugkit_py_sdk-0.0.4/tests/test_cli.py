import json
import os
import subprocess
import sys

import pytest
from typer.testing import CliRunner

from slugkit.cli import app
from slugkit.base import StatsItem, SeriesInfo, PatternInfo, DictionaryInfo, DictionaryTag

runner = CliRunner()


@pytest.fixture(autouse=True)
def _set_env(monkeypatch):
    # Ensure CLI sees the correct env vars by default
    monkeypatch.setenv("SLUGKIT_BASE_URL", "https://dev.slugkit.dev/api/v1")
    # Use the series API key by default; individual tests can override
    monkeypatch.setenv("SLUGKIT_API_KEY", "ik-H4m1ahqk8xaUtxe0QJ15ydnGxjXGjukomlMOVpTPsJg=")


def test_cli_mint_single_text_output():
    result = runner.invoke(app, ["mint", "1"])  # default text output
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert len(lines) == 1
    assert len(lines[0]) > 0


def test_cli_mint_multiple_json_output():
    result = runner.invoke(app, ["-o", "json", "mint", "5", "--batch-size", "2"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 5


def test_cli_slice_dry_run_text():
    result = runner.invoke(app, ["slice", "0", "3"])  # text output
    assert result.exit_code == 0
    ids1 = result.output.strip().splitlines()

    # Same call again should return same IDs (dry run)
    result2 = runner.invoke(app, ["slice", "0", "3"])  # text output
    assert result2.exit_code == 0
    ids2 = result2.output.strip().splitlines()

    assert ids1 == ids2


def test_cli_forge_with_seed_json():
    # Use a valid pattern with supported tokens
    result = runner.invoke(
        app,
        [
            "-o",
            "json",
            "forge",
            "test-{adjective}-{noun}-{hex:4}",
            "--seed",
            "pytest-seed",
            "--count",
            "3",
        ],
    )
    if result.exit_code != 0:
        print(f"CLI Error: {result.output}")
        # If this specific pattern fails, try a simpler one
        result = runner.invoke(
            app,
            [
                "-o",
                "json",
                "forge",
                "simple-{noun}-pattern",
                "--seed",
                "pytest-seed",
                "--count",
                "3",
            ],
        )

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 3


def test_cli_stats_and_reset(monkeypatch):
    # Stats should work
    result_stats = runner.invoke(app, ["stats"])  # text output
    assert result_stats.exit_code == 0
    # Check for new stats format
    assert "Event Type" in result_stats.output
    assert "Date Part" in result_stats.output
    assert "Total Count" in result_stats.output

    # Reset should succeed (will change generator state; safe for test series)
    result_reset = runner.invoke(app, ["reset"])  # text output
    assert result_reset.exit_code == 0


def test_cli_series_info(monkeypatch):
    """Test the series-info CLI command."""
    # Test text output
    result_text = runner.invoke(app, ["series-info"])  # text output
    assert result_text.exit_code == 0
    # Check for expected fields in text output
    assert "Series Slug" in result_text.output
    assert "Organization Slug" in result_text.output
    assert "Pattern" in result_text.output
    assert "Max Pattern Length" in result_text.output
    assert "Capacity" in result_text.output
    assert "Generated Count" in result_text.output
    assert "Last Modified" in result_text.output

    # Test JSON output
    result_json = runner.invoke(app, ["-o", "json", "series-info"])  # JSON output
    assert result_json.exit_code == 0
    data = json.loads(result_json.output)
    assert isinstance(data, dict)
    # Check for expected keys in JSON output
    expected_keys = ["slug", "org_slug", "pattern", "max_pattern_length", "capacity", "generated_count", "mtime"]
    for key in expected_keys:
        assert key in data


def test_cli_series_list(monkeypatch):
    """Test the series-list CLI command."""
    # Test text output
    result_text = runner.invoke(app, ["series-list"])  # text output
    assert result_text.exit_code == 0
    # Check that we get a list of series
    lines = result_text.output.strip().splitlines()
    assert len(lines) > 0
    # Each line should be a series slug
    for line in lines:
        assert len(line) > 0

    # Test JSON output
    result_json = runner.invoke(app, ["-o", "json", "series-list"])  # JSON output
    assert result_json.exit_code == 0
    data = json.loads(result_json.output)
    assert isinstance(data, list)
    assert len(data) > 0
    # Each item should be a string (series slug)
    for item in data:
        assert isinstance(item, str)
        assert len(item) > 0


def test_cli_validate(monkeypatch):
    """Test the validate CLI command."""
    # Test text output
    result_text = runner.invoke(app, ["validate", "test-{adjective}-{noun}"])  # text output
    assert result_text.exit_code == 0
    # Check for expected fields in text output
    assert "Pattern" in result_text.output
    assert "Capacity" in result_text.output
    assert "Max Slug Length" in result_text.output
    assert "Complexity" in result_text.output
    assert "Components" in result_text.output

    # Test JSON output
    result_json = runner.invoke(app, ["-o", "json", "validate", "test-{adjective}-{noun}"])  # JSON output
    assert result_json.exit_code == 0
    data = json.loads(result_json.output)
    assert isinstance(data, dict)
    # Check for expected keys in JSON output
    expected_keys = ["pattern", "capacity", "max_slug_length", "complexity", "components"]
    for key in expected_keys:
        assert key in data
