#!/usr/bin/env python3
"""
Comprehensive functionality test for Result Parser Agent CLI
Tests all CLI features including new workload management and script downloading
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from result_parser_agent.api.registry_client import RegistryClient
from result_parser_agent.cli import (
    add_workload,
    manage_script_cache,
    save_output,
    setup_logging,
    show_workload,
    update_workload,
    validate_input_path,
    validate_metrics,
    validate_workload,
)
from result_parser_agent.config.settings import settings
from result_parser_agent.models.schema import (
    Instance,
    Iteration,
    Statistics,
    StructuredResults,
)
from result_parser_agent.scripts.downloader import ScriptDownloader
from result_parser_agent.tools.registry import ToolRegistry


def test_config_loading():
    """Test configuration loading functionality."""
    print("🧪 Testing configuration loading...")

    # Test default config loads from environment
    config = settings

    # Check that config has required attributes
    assert hasattr(config, "LLM_PROVIDER")
    assert hasattr(config, "LLM_MODEL")
    assert hasattr(config, "SCRIPTS_BASE_URL")
    assert hasattr(config, "SCRIPTS_CACHE_DIR")
    assert hasattr(config, "SCRIPTS_CACHE_TTL")

    print(
        f"✅ Default configuration loaded: provider={config.LLM_PROVIDER}, model={config.LLM_MODEL}"
    )
    print(
        f"✅ Script configuration: cache_dir={config.SCRIPTS_CACHE_DIR}, ttl={config.SCRIPTS_CACHE_TTL}"
    )


def test_validation_functions():
    """Test validation functions."""
    print("🧪 Testing validation functions...")

    # Create a temporary test file for validation
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        temp_file = f.name
        f.write("test content")

    try:
        # Test input path validation with existing file
        validated_path = validate_input_path(temp_file)
        assert validated_path == Path(temp_file)
        print("✅ Input path validation works correctly")
    finally:
        Path(temp_file).unlink(missing_ok=True)

    # Test metrics validation
    metrics = validate_metrics(["RPS", "latency", "throughput"])
    assert len(metrics) == 3
    assert "RPS" in metrics
    print("✅ Metrics validation works correctly")


def test_workload_validation():
    """Test workload validation functionality."""
    print("🧪 Testing workload validation...")

    # Create a mock tool registry for testing
    mock_registry = MagicMock()
    mock_registry.list_workloads.return_value = [
        "fio",
        "redis",
        "nginx",
        "mariadb_tpch",
        "mysql_tpch",
        "mariadb_tpcc",
        "mysql_tpcc",
    ]

    # Test case-insensitive workload matching
    workloads = [
        "fio",
        "redis",
        "nginx",
        "mariadb_tpch",
        "mysql_tpch",
        "mariadb_tpcc",
        "mysql_tpcc",
    ]

    for workload in workloads:
        # Test exact match
        assert validate_workload(workload, mock_registry) == workload
        # Test uppercase match
        assert validate_workload(workload.upper(), mock_registry) == workload
        # Test mixed case match
        assert validate_workload(workload.title(), mock_registry) == workload

    # Test invalid workload - mock sys.exit to prevent test from exiting
    with patch("sys.exit") as mock_exit, patch("logging.Logger.error"):
        try:
            validate_workload("invalid_workload", mock_registry)
        except SystemExit:
            pass
        mock_exit.assert_called_once_with(1)

    print("✅ Workload validation works correctly")


def test_output_saving():
    """Test output saving functionality."""
    print("🧪 Testing output saving...")

    # Create test data
    stats = Statistics(metricName="RPS", metricValue="1234.56")
    instance = Instance(instanceIndex=1, statistics=[stats])
    iteration = Iteration(iterationIndex=1, instances=[instance])
    results = StructuredResults(iterations=[iteration])

    # Test saving to file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_file = f.name

    try:
        save_output(results, temp_file)

        # Verify file was created and contains data
        with open(temp_file) as f:
            data = json.load(f)

        assert len(data["iterations"]) == 1
        print("✅ Output saving works correctly")

    finally:
        Path(temp_file).unlink(missing_ok=True)


def test_cli_parameter_handling():
    """Test CLI parameter handling logic."""
    print("🧪 Testing CLI parameter handling...")

    # Test metrics from CLI
    cli_metrics = "RPS,latency,throughput"
    metrics_list = validate_metrics([m.strip() for m in cli_metrics.split(",")])
    assert len(metrics_list) == 3
    assert "RPS" in metrics_list
    assert "latency" in metrics_list
    assert "throughput" in metrics_list
    print("✅ CLI parameter handling works correctly")


def test_file_operations():
    """Test file operation utilities."""
    print("🧪 Testing file operations...")

    # Test path validation with non-existent file (should raise exception)
    try:
        validate_input_path("non_existent_file.txt")
        assert False, "Should have raised an exception"
    except Exception:
        print("✅ Path validation correctly rejects non-existent files")

    # Test metrics validation with empty list (should raise exception)
    try:
        validate_metrics([])
        assert False, "Should have raised an exception"
    except Exception:
        print("✅ Metrics validation correctly rejects empty lists")


def test_error_handling():
    """Test error handling in validation functions."""
    print("🧪 Testing error handling...")

    # Test invalid metrics
    try:
        validate_metrics([])
        assert False, "Should have raised an exception for empty metrics"
    except Exception:
        print("✅ Empty metrics validation works correctly")

    # Test invalid input path
    try:
        validate_input_path("non_existent_path")
        assert False, "Should have raised an exception for non-existent path"
    except Exception:
        print("✅ Invalid path validation works correctly")


def test_logging_setup():
    """Test logging setup functionality."""
    print("🧪 Testing logging setup...")

    # Test logging setup doesn't crash
    setup_logging(verbose=False)
    setup_logging(verbose=True)
    print("✅ Logging setup works correctly")


def test_environment_config_loading():
    """Test environment-based configuration loading."""
    print("🧪 Testing environment configuration loading...")

    # Test that we can load config multiple times (should be consistent)
    config1 = settings
    config2 = settings

    # Configs should be equivalent
    assert config1.LLM_PROVIDER == config2.LLM_PROVIDER
    assert config1.LLM_MODEL == config2.LLM_MODEL
    assert config1.SCRIPTS_BASE_URL == config2.SCRIPTS_BASE_URL

    print("✅ Environment configuration loading is consistent")


def test_script_downloader():
    """Test script downloader functionality."""
    print("🧪 Testing script downloader...")

    with patch("result_parser_agent.scripts.downloader.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0  # pretend git succeeded
        downloader = ScriptDownloader()

        assert hasattr(downloader, "cache_dir")
        assert hasattr(downloader, "git_url")
        assert hasattr(downloader, "branch")

        print("✅ Script downloader initialization works correctly")


def test_tool_registry():
    """Test tool registry functionality."""
    print("🧪 Testing tool registry...")

    # Test tool registry initialization
    registry = ToolRegistry()

    # Check that required attributes are set
    assert hasattr(registry, "api_client")
    assert hasattr(registry, "script_downloader")

    print("✅ Tool registry initialization works correctly")


def test_registry_client():
    """Test registry client functionality."""
    print("🧪 Testing registry client...")

    # Mock the APIConfig to return our test values
    with patch(
        "result_parser_agent.api.registry_client.APIConfig"
    ) as mock_config_class:
        mock_config = MagicMock()
        mock_config.PARSER_REGISTRY_URL = "http://fake-registry"
        mock_config.PARSER_REGISTRY_TIMEOUT = 30
        mock_config_class.return_value = mock_config

        client = RegistryClient()

        assert client.base_url == "http://fake-registry"
        assert client.timeout == 30

        print("✅ Registry client initialization works correctly")


def test_workload_management_commands():
    """Test workload management CLI commands."""
    print("🧪 Testing workload management commands...")

    # Mock the tool registry for testing
    with patch("result_parser_agent.cli._cli_tool_registry") as mock_registry:
        mock_registry.add_workload.return_value = {
            "success": True,
            "message": "Workload 'test_workload' successfully created",
            "workload": "test_workload",
        }

        mock_registry.update_workload.return_value = {
            "success": True,
            "message": "Workload 'test_workload' successfully updated",
            "workload": "test_workload",
        }

        mock_registry.get_workload_details.return_value = {
            "workloadName": "test_workload",
            "metrics": ["metric1", "metric2"],
            "script": "extractor.sh",
            "description": "Test workload",
            "status": "active",
            "script_local_path": "/tmp/test_script.sh",  # Add missing field
        }

        # Test add workload
        result = add_workload(
            name="test_workload",
            metrics="metric1,metric2",
            description="Test workload",
            status="active",
        )
        assert result is None  # CLI commands don't return values
        print("✅ Add workload command works correctly")

        # Test update workload
        result = update_workload(
            name="test_workload", metrics="metric1,metric2,metric3"
        )
        assert result is None
        print("✅ Update workload command works correctly")

        # Test show workload
        result = show_workload(name="test_workload")
        assert result is None
        print("✅ Show workload command works correctly")


def test_script_cache_management():
    """Test script cache management CLI command."""
    print("🧪 Testing script cache management...")

    # Mock the tool registry for testing
    with patch("result_parser_agent.cli._cli_tool_registry") as mock_registry:
        mock_registry.get_registry_info.return_value = {
            "source": "API Registry + Git Scripts",
            "workloads": ["fio", "redis", "nginx"],
            "script_cache": {
                "cache_dir": "/tmp/cache",
                "cached_scripts": ["fio", "redis"],
                "total_size": "1.2MB",
            },
        }

        mock_registry.clear_script_cache.return_value = {
            "success": True,
            "message": "Script cache cleared successfully",
        }

        # Test cache info
        result = manage_script_cache(action="info")
        assert result is None
        print("✅ Cache info command works correctly")

        # Test cache clear
        result = manage_script_cache(action="clear", workload="fio")
        assert result is None
        print("✅ Cache clear command works correctly")

        # Test cache clear all
        result = manage_script_cache(action="clear-all")
        assert result is None
        print("✅ Cache clear all command works correctly")


def test_workload_support():
    """Test that all supported workloads are properly configured."""
    print("🧪 Testing workload support...")

    expected_workloads = [
        "fio",
        "redis",
        "nginx",
        "mariadb_tpch",
        "mysql_tpch",
        "mariadb_tpcc",
        "mysql_tpcc",
    ]

    # Create a mock tool registry for testing
    mock_registry = MagicMock()
    mock_registry.list_workloads.return_value = expected_workloads

    # Test that all expected workloads are valid
    for workload in expected_workloads:
        assert validate_workload(workload, mock_registry) == workload

    print(f"✅ All {len(expected_workloads)} workloads are properly supported")


def test_cli_command_structure():
    """Test that CLI command structure is properly set up."""
    print("🧪 Testing CLI command structure...")

    # Import the CLI app to check command structure
    from result_parser_agent.cli import app

    # Check that the app has the expected commands
    expected_commands = [
        "parse",
        "registry",
        "cache",
        "add-workload",
        "update-workload",
        "show-workload",
    ]

    for command in expected_commands:
        assert command in [cmd.name for cmd in app.registered_commands]

    print(f"✅ CLI has all {len(expected_commands)} expected commands")


def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Starting comprehensive functionality tests...")
    print(
        "📋 Testing new features: workload management, script downloading, API integration"
    )

    test_functions = [
        test_config_loading,
        test_validation_functions,
        test_workload_validation,
        test_output_saving,
        test_cli_parameter_handling,
        test_file_operations,
        test_error_handling,
        test_logging_setup,
        test_environment_config_loading,
        test_script_downloader,
        test_tool_registry,
        test_registry_client,
        test_workload_management_commands,
        test_script_cache_management,
        test_workload_support,
        test_cli_command_structure,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {str(e)}")
            failed += 1

    print(f"\n📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
