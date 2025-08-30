"""Tests for the version module."""

import os
from unittest.mock import patch
import pytest
import logging
from regscale.utils.version import RegscaleVersion

logger = logging.getLogger(__name__)


@patch.object(RegscaleVersion, "get_platform_version", return_value="1.0.0.0")
def test_get_platform_version(mock_get_platform_version):
    """Test get_platform_version method."""
    version = RegscaleVersion.get_platform_version()
    assert isinstance(version, str) and RegscaleVersion.is_valid_version(version)


@pytest.mark.parametrize(
    "version, expected",
    [
        ("1.0", True),
        ("1.0.0", True),
        ("1.0.0.0", True),
        ("1.0.0.0.0", False),
        ("1.a.0", False),
        ("1.0.a", False),
        ("a.b.c", False),
        ("1.0.0-alpha", False),
        ("dev", False),
        ("localdev", False),
        ("1337-2024-10-25", False),
    ],
)
def test_is_valid_version(version, expected):
    """Test is_valid_version method."""
    assert RegscaleVersion.is_valid_version(version) == expected


@pytest.mark.parametrize(
    "version1, version2, dev_is_latest, expected",
    [
        ("1.0.0", "1.0.1", True, False),
        ("1.2.0", "1.0.1", True, True),
        ("2.0.0", "1.9.9", True, True),
        ("2.0.0", "42069-2013-07-14", True, True),
        ("42069-2013-07-14", "2.0.0", True, True),
        ("dev", "1.0.1", True, True),
        ("1.0.0", "dev", True, False),
        ("dev", "dev", True, True),
        ("localdev", "1.0.1", True, True),
        ("1.0.0", "localdev", True, False),
        ("localdev", "localdev", True, True),
        ("Unknown", "1.0.1", True, True),
        ("1.0.0", "Unknown", True, False),
        ("Unknown", "Unknown", True, True),
    ],
)
def test_compare_versions(version1, version2, dev_is_latest, expected):
    """Test compare_versions method."""
    assert RegscaleVersion.compare_versions(version1, version2, dev_is_latest) == expected


@pytest.mark.parametrize(
    "minimum_version, dev_is_latest, expected",
    [
        ("1.0.0.0", True, True),
        ("2.0.0", True, False),
        ("dev", True, False),
        ("dev", False, True),
        ("localdev", True, False),
        ("Unknown", True, False),
        ("1337-2024-10-25", True, True),
    ],
)
@patch.object(RegscaleVersion, "get_platform_version", return_value="1.0.0")
def test_meets_minimum_version(mock_get_platform_version, minimum_version, dev_is_latest, expected):
    """Test meets_minimum_version method."""
    assert RegscaleVersion.meets_minimum_version(minimum_version, dev_is_latest) == expected


def test_no_application_initialized():
    """Test no application initialized."""
    # Run the regscale version command and verify the word app is not in the console output
    import re
    import subprocess

    log_level = "LOGLEVEL"

    previous_value = os.getenv(log_level)
    os.environ[log_level] = "DEBUG"
    process = subprocess.run(
        ["regscale", "version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert not re.search(r"Initializing\s+(?:.*?\.py:\d+\s+)?Application", process.stdout)
    print(process.stdout)
    os.environ[log_level] = previous_value or "INFO"
