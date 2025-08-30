"""
Tests for the IntegrationOverride class.

This module provides comprehensive test coverage for the IntegrationOverride class,
which handles custom integration mappings for findings and field validation.
"""

from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from regscale.core.app.application import Application
from regscale.integrations.integration_override import IntegrationOverride


@pytest.fixture
def basic_config() -> Dict[str, Any]:
    """Basic configuration fixture with finding mappings."""
    return {
        "findingFromMapping": {
            "tenable_sc": {
                "severity": "risk_level",
                "description": "details",
                "remediation": "rando",
                "title": "default",
            },
            "qualys": {
                "severity": "cvss_score",
                "description": "summary",
                "solution": "fix",
            },
        }
    }


@pytest.fixture
def config_with_unique_override() -> Dict[str, Any]:
    """Configuration fixture with unique override settings."""
    return {
        "findingFromMapping": {
            "tenable_sc": {
                "severity": "risk_level",
                "description": "details",
            }
        },
        "uniqueOverride": {"asset": ["ipAddress"], "issue": ["title"]},
    }


@pytest.fixture
def mock_app(basic_config: Dict[str, Any]) -> Application:
    """Mock application fixture with basic configuration."""
    app = Application()
    app.config = basic_config
    app.logger = MagicMock()
    return app


@pytest.fixture
def mock_app_with_unique_override(config_with_unique_override: Dict[str, Any]) -> Application:
    """Mock application fixture with unique override configuration."""
    app = Application()
    app.config = config_with_unique_override
    app.logger = MagicMock()
    return app


@pytest.fixture
def empty_config_app() -> Application:
    """Mock application fixture with empty configuration."""
    app = Application()
    app.config = {}
    app.logger = MagicMock()
    return app


class TestIntegrationOverrideSingleton:
    """Test the singleton pattern implementation."""

    def test_singleton_pattern(self, mock_app: Application):
        """Test that IntegrationOverride follows singleton pattern."""
        # Reset singleton instance for clean test
        IntegrationOverride._instance = None

        instance1 = IntegrationOverride(mock_app)
        instance2 = IntegrationOverride(mock_app)

        assert instance1 is instance2
        assert id(instance1) == id(instance2)

    def test_singleton_thread_safety(self, mock_app: Application):
        """Test that singleton creation is thread-safe."""
        # Reset singleton instance for clean test
        IntegrationOverride._instance = None

        import threading
        import time

        instances = []

        def create_instance():
            time.sleep(0.01)  # Small delay to increase race condition chance
            instances.append(IntegrationOverride(mock_app))

        threads = [threading.Thread(target=create_instance) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All instances should be the same
        assert len(set(instances)) == 1
        assert all(instance is instances[0] for instance in instances)


class TestIntegrationOverrideInitialization:
    """Test the initialization and configuration loading."""

    def test_initialization_with_config(self, mock_app: Application):
        """Test initialization with valid configuration."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.app == mock_app
        assert "tenable_sc" in integration_override.mapping
        assert "qualys" in integration_override.mapping
        assert integration_override.mapping["tenable_sc"]["severity"] == "risk_level"

    def test_initialization_with_empty_config(self, empty_config_app: Application):
        """Test initialization with empty configuration."""
        integration_override = IntegrationOverride(empty_config_app)

        assert integration_override.app == empty_config_app
        assert integration_override.mapping == {}

    def test_initialization_only_once(self, mock_app: Application):
        """Test that console and logging are only initialized once."""
        # Reset singleton instance for clean test
        IntegrationOverride._instance = None

        # Patch the rich imports inside the method
        with patch("rich.console.Console") as mock_console, patch("rich.table.Table") as mock_table:
            mock_table_instance = Mock()
            mock_table.return_value = mock_table_instance
            mock_table_instance.row_count = 0

            IntegrationOverride(mock_app)
            IntegrationOverride(mock_app)

            # Console should only be created once
            mock_console.assert_called_once()


class TestIntegrationOverrideMappingMethods:
    """Test the mapping-related methods."""

    def test_get_mapping(self, mock_app: Application):
        """Test _get_mapping method."""
        integration_override = IntegrationOverride(mock_app)

        mapping = integration_override._get_mapping(mock_app.config)
        assert mapping == mock_app.config["findingFromMapping"]

    def test_get_mapping_without_finding_from_mapping(self, empty_config_app: Application):
        """Test _get_mapping when findingFromMapping is not present."""
        integration_override = IntegrationOverride(empty_config_app)

        mapping = integration_override._get_mapping(empty_config_app.config)
        assert mapping == {}

    def test_mapping_exists_valid_mapping(self, mock_app: Application):
        """Test mapping_exists with valid mapping."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.mapping_exists("tenable_sc", "severity") is True
        assert integration_override.mapping_exists("qualys", "severity") is True

    def test_mapping_exists_default_value(self, mock_app: Application):
        """Test mapping_exists with default value."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.mapping_exists("tenable_sc", "title") is False

    def test_mapping_exists_nonexistent_integration(self, mock_app: Application):
        """Test mapping_exists with nonexistent integration."""
        integration_override = IntegrationOverride(mock_app)

        # The method now returns False when integration doesn't exist
        assert integration_override.mapping_exists("nonexistent", "severity") is False

    def test_mapping_exists_nonexistent_field(self, mock_app: Application):
        """Test mapping_exists with nonexistent field."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.mapping_exists("tenable_sc", "nonexistent") is False

    def test_mapping_exists_case_insensitive(self, mock_app: Application):
        """Test mapping_exists is case insensitive."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.mapping_exists("TENABLE_SC", "SEVERITY") is True
        assert integration_override.mapping_exists("Tenable_Sc", "Severity") is True

    def test_mapping_exists_with_none_values(self, mock_app: Application):
        """Test mapping_exists with None values."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.mapping_exists(None, "severity") is False
        assert integration_override.mapping_exists("tenable_sc", None) is False
        assert integration_override.mapping_exists(None, None) is False


class TestIntegrationOverrideLoadMethod:
    """Test the load method."""

    def test_load_valid_mapping(self, mock_app: Application):
        """Test load with valid mapping."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.load("tenable_sc", "severity") == "risk_level"
        assert integration_override.load("tenable_sc", "description") == "details"
        assert integration_override.load("qualys", "severity") == "cvss_score"

    def test_load_default_value(self, mock_app: Application):
        """Test load with default value."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.load("tenable_sc", "title") is None

    def test_load_nonexistent_integration(self, mock_app: Application):
        """Test load with nonexistent integration."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.load("nonexistent", "severity") is None

    def test_load_nonexistent_field(self, mock_app: Application):
        """Test load with nonexistent field."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.load("tenable_sc", "nonexistent") is None

    def test_load_none_parameters(self, mock_app: Application):
        """Test load with None parameters."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.load(None, None) is None
        # The method should handle None field_name gracefully
        assert integration_override.load("tenable_sc", None) is None
        assert integration_override.load(None, "severity") is None

    def test_load_case_insensitive(self, mock_app: Application):
        """Test load is case insensitive."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.load("TENABLE_SC", "SEVERITY") == "risk_level"
        assert integration_override.load("Tenable_Sc", "Severity") == "risk_level"


class TestIntegrationOverrideFieldMapValidation:
    """Test the field_map_validation method."""

    def test_field_map_validation_no_unique_override(self, mock_app: Application):
        """Test field_map_validation when no uniqueOverride is configured."""
        integration_override = IntegrationOverride(mock_app)
        obj = {"ip": "192.168.1.1"}

        result = integration_override.field_map_validation(obj, "asset")
        assert result is None

    def test_field_map_validation_empty_unique_override(self, mock_app_with_unique_override: Application):
        """Test field_map_validation with empty uniqueOverride for model type."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)
        obj = {"ip": "192.168.1.1"}

        # Override config to have empty list for asset
        integration_override.app.config["uniqueOverride"]["asset"] = []

        result = integration_override.field_map_validation(obj, "asset")
        assert result is None

    def test_field_map_validation_unsupported_field(self, mock_app_with_unique_override: Application):
        """Test field_map_validation with unsupported field."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)
        obj = {"ip": "192.168.1.1"}

        # Override config to have unsupported field
        integration_override.app.config["uniqueOverride"]["asset"] = ["unsupported_field"]

        result = integration_override.field_map_validation(obj, "asset")
        assert result is None

    def test_field_map_validation_unsupported_model_type(self, mock_app_with_unique_override: Application):
        """Test field_map_validation with unsupported model type."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)
        obj = {"ip": "192.168.1.1"}

        result = integration_override.field_map_validation(obj, "unsupported_type")
        assert result is None

    def test_field_map_validation_dict_object_tenableasset(self, mock_app_with_unique_override: Application):
        """Test field_map_validation with dict object for tenableasset model."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)

        # Create a dict-like object that has a class name
        class DictLikeObject(dict):
            """Dict-like object with custom class name for testing."""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.__class__.__name__ = "TenableAsset"

        obj = DictLikeObject({"ip": "192.168.1.1", "dnsName": "test.example.com"})

        result = integration_override.field_map_validation(obj, "asset")
        assert result == "192.168.1.1"

    def test_field_map_validation_dict_object_dict(self, mock_app_with_unique_override: Application):
        """Test field_map_validation with dict object for dict model."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)

        # Create a dict-like object that has a class name
        class DictLikeObject(dict):
            """Dict-like object with custom class name for testing."""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.__class__.__name__ = "dict"

        obj = DictLikeObject({"ipv4": "192.168.1.1", "fqdn": "test.example.com"})

        result = integration_override.field_map_validation(obj, "asset")
        assert result == "192.168.1.1"

    def test_field_map_validation_object_with_attributes(self, mock_app_with_unique_override: Application):
        """Test field_map_validation with object that has attributes."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)

        # Create mock object with attributes
        obj = Mock()
        obj.__class__.__name__ = "TenableAsset"
        obj.ip = "192.168.1.1"
        obj.dnsName = "test.example.com"

        result = integration_override.field_map_validation(obj, "asset")
        assert result == "192.168.1.1"

    def test_field_map_validation_missing_mapped_field(self, mock_app_with_unique_override: Application):
        """Test field_map_validation when mapped field is missing."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)

        # Create a dict-like object missing the mapped field
        class DictLikeObject(dict):
            """Dict-like object with custom class name for testing."""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.__class__.__name__ = "TenableAsset"

        obj = DictLikeObject({"dnsName": "test.example.com"})  # Missing "ip"

        result = integration_override.field_map_validation(obj, "asset")
        assert result is None

    def test_field_map_validation_exception_handling(self, mock_app_with_unique_override: Application):
        """Test field_map_validation handles exceptions gracefully."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)

        # Create an object that will cause an exception when accessing __class__.__name__
        class ProblematicObject:
            """Object that raises AttributeError when accessing __class__.__name__."""

            @property
            def __class__(self):
                # This will cause an AttributeError when trying to access __name__
                raise AttributeError("Simulated error")

        obj = ProblematicObject()

        result = integration_override.field_map_validation(obj, "asset")
        assert result is None
        integration_override.app.logger.warning.assert_called_once()

    def test_field_map_validation_different_field_mappings(self, mock_app_with_unique_override: Application):
        """Test field_map_validation with different field mappings."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)

        # Test name field mapping
        integration_override.app.config["uniqueOverride"]["asset"] = ["name"]

        class DictLikeObject(dict):
            """Dict-like object with custom class name for testing."""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.__class__.__name__ = "TenableAsset"

        obj = DictLikeObject({"dnsName": "test.example.com"})

        result = integration_override.field_map_validation(obj, "asset")
        assert result == "test.example.com"

        # Test dns field mapping
        integration_override.app.config["uniqueOverride"]["asset"] = ["dns"]

        result = integration_override.field_map_validation(obj, "asset")
        assert result == "test.example.com"

        # Test fqdn field mapping
        integration_override.app.config["uniqueOverride"]["asset"] = ["fqdn"]

        result = integration_override.field_map_validation(obj, "asset")
        assert result == "test.example.com"


class TestIntegrationOverrideLogging:
    """Test the logging functionality."""

    def test_log_mappings_with_mappings(self, mock_app: Application):
        """Test _log_mappings when mappings exist."""
        # Reset singleton instance for clean test
        IntegrationOverride._instance = None

        # Patch the rich imports inside the method
        with patch("rich.table.Table") as mock_table, patch("rich.console.Console") as mock_console:
            mock_table_instance = Mock()
            mock_table.return_value = mock_table_instance
            mock_table_instance.row_count = 2  # Simulate rows in table

            IntegrationOverride(mock_app)

            # Verify table was created and printed
            mock_table.assert_called_once()
            mock_console_instance = mock_console.return_value
            mock_console_instance.print.assert_called_once_with(mock_table_instance)

    def test_log_mappings_no_mappings(self, empty_config_app: Application):
        """Test _log_mappings when no mappings exist."""
        # Reset singleton instance for clean test
        IntegrationOverride._instance = None

        # Patch the rich imports inside the method
        with patch("rich.table.Table") as mock_table, patch("rich.console.Console") as mock_console:
            mock_table_instance = Mock()
            mock_table.return_value = mock_table_instance
            mock_table_instance.row_count = 0  # No rows in table

            IntegrationOverride(empty_config_app)

            # Verify table was created but not printed (no rows)
            mock_table.assert_called_once()
            mock_console_instance = mock_console.return_value
            mock_console_instance.print.assert_not_called()


class TestIntegrationOverrideEdgeCases:
    """Test edge cases and error conditions."""

    def test_load_with_empty_strings(self, mock_app: Application):
        """Test load with empty strings."""
        integration_override = IntegrationOverride(mock_app)

        assert integration_override.load("", "") is None
        assert integration_override.load("tenable_sc", "") is None
        assert integration_override.load("", "severity") is None

    def test_mapping_exists_with_empty_strings(self, mock_app: Application):
        """Test mapping_exists with empty strings."""
        integration_override = IntegrationOverride(mock_app)

        # Empty strings should be handled gracefully and return False
        assert integration_override.mapping_exists("", "") is False
        assert integration_override.mapping_exists("tenable_sc", "") is False
        assert integration_override.mapping_exists("", "severity") is False

    def test_field_map_validation_with_none_object(self, mock_app_with_unique_override: Application):
        """Test field_map_validation with None object."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)

        result = integration_override.field_map_validation(None, "asset")
        assert result is None

    def test_field_map_validation_with_none_model_type(self, mock_app_with_unique_override: Application):
        """Test field_map_validation with None model type."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)
        obj = {"ip": "192.168.1.1"}

        result = integration_override.field_map_validation(obj, None)
        assert result is None

    def test_field_map_validation_with_empty_string_model_type(self, mock_app_with_unique_override: Application):
        """Test field_map_validation with empty string model type."""
        integration_override = IntegrationOverride(mock_app_with_unique_override)
        obj = {"ip": "192.168.1.1"}

        result = integration_override.field_map_validation(obj, "")
        assert result is None


@pytest.mark.integration
class TestIntegrationOverrideIntegration:
    """Integration tests for IntegrationOverride."""

    def test_full_workflow_with_tenable_sc(self, mock_app: Application):
        """Test complete workflow with Tenable SC integration."""
        integration_override = IntegrationOverride(mock_app)

        # Test mapping exists
        assert integration_override.mapping_exists("tenable_sc", "severity") is True

        # Test load mapping
        mapped_field = integration_override.load("tenable_sc", "severity")
        assert mapped_field == "risk_level"

        # Test that default values are not loaded
        assert integration_override.load("tenable_sc", "title") is None

    def test_full_workflow_with_qualys(self, mock_app: Application):
        """Test complete workflow with Qualys integration."""
        integration_override = IntegrationOverride(mock_app)

        # Test mapping exists
        assert integration_override.mapping_exists("qualys", "severity") is True

        # Test load mapping
        mapped_field = integration_override.load("qualys", "severity")
        assert mapped_field == "cvss_score"

        # Test solution mapping
        solution_field = integration_override.load("qualys", "solution")
        assert solution_field == "fix"

    def test_case_insensitive_workflow(self, mock_app: Application):
        """Test complete workflow with case insensitive handling."""
        integration_override = IntegrationOverride(mock_app)

        # Test with mixed case
        assert integration_override.mapping_exists("TENABLE_SC", "SEVERITY") is True
        assert integration_override.load("TENABLE_SC", "SEVERITY") == "risk_level"

        # Test with title case
        assert integration_override.mapping_exists("Tenable_Sc", "Severity") is True
        assert integration_override.load("Tenable_Sc", "Severity") == "risk_level"
