from random import randint, random
from unittest.mock import Mock

import pytest

from regscale.integrations.integration_override import IntegrationOverride
from regscale.models.integration_models.tenable_models.models import Family, Repository, Severity, TenableAsset


@pytest.fixture
def random_local_ip():
    """
    Returns a random local ip address
    """

    # ip
    return f"192.168.{randint(0, 255)}.{randint(0, 255)}"


@pytest.fixture
def tenable_asset(random_local_ip):
    return TenableAsset(
        pluginID="1234",
        severity=Severity(id="high", name="High", description="High"),
        hasBeenMitigated="false",
        acceptRisk="false",
        recastRisk="false",
        ip=random_local_ip,
        uuid="test-uuid",
        port="80",
        protocol="tcp",
        pluginName="Test Plugin",
        firstSeen="2024-01-01",
        lastSeen="2024-01-02",
        exploitAvailable="true",
        exploitEase="easy",
        exploitFrameworks="test",
        synopsis="test",
        description="test",
        solution="test",
        seeAlso="test",
        riskFactor="High",
        stigSeverity="High",
        vprScore="9.0",
        vprContext="test",
        baseScore="9.0",
        temporalScore="9.0",
        cvssVector="test",
        cvssV3BaseScore="9.0",
        cvssV3TemporalScore="9.0",
        cvssV3Vector="test",
        cpe="test",
        vulnPubDate="2024-01-01",
        patchPubDate="2024-01-01",
        pluginPubDate="2024-01-01",
        pluginModDate="2024-01-01",
        checkType="test",
        version="1.0",
        cve="CVE-2024-1234",
        bid="1234",
        xref="test",
        pluginText="test",
        dnsName="test.example.com",
        macAddress="00:11:22:33:44:55",
        netbiosName="TEST",
        operatingSystem="Linux",
        ips=random_local_ip,
        recastRiskRuleComment="test",
        acceptRiskRuleComment="test",
        hostUniqueness="test",
        acrScore="9.0",
        keyDrivers="test",
        uniqueness="test",
        family=Family(id="1", name="Test Family", type="Test Type"),
        repository=Repository(id="rep", name="Test", description="Test", dataFormat="Test"),
        pluginInfo="test",
    )


def test_field_map_validation_with_dict(tenable_asset, random_local_ip):
    app = Mock()
    app.config = {"uniqueOverride": {"asset": ["ipAddress"]}}
    override = IntegrationOverride(app)

    dict_cases = [
        ({"ipv4": random_local_ip}, random_local_ip),
        ({}, None),
        ({"ipv4": None}, None),
        ({"other_field": "value"}, None),
    ]

    for test_input, expected in dict_cases:
        assert override.field_map_validation(test_input, "asset") == expected


def test_field_map_validation_with_tenable_asset(tenable_asset, random_local_ip):
    app = Mock()
    app.config = {"uniqueOverride": {"asset": ["ipAddress"]}}
    override = IntegrationOverride(app)

    assert override.field_map_validation(tenable_asset, "asset") == random_local_ip


def test_field_map_validation_with_multiple_fields(random_local_ip):
    app = Mock()
    app.config = {"uniqueOverride": {"asset": ["ipAddress", "macAddress", "hostname"]}}
    override = IntegrationOverride(app)
    dict_obj = {"ipv4": random_local_ip, "mac": "00:11:22:33:44:55", "hostname": "test.example.com"}
    assert override.field_map_validation(dict_obj, "asset") == random_local_ip


def test_field_map_validation_with_empty_and_invalid_configs(random_local_ip):
    app = Mock()
    dict_obj = {"ipv4": random_local_ip, "mac": "00:11:22:33:44:55", "hostname": "test.example.com"}

    # Invalid configs here
    config_cases = [
        ({}, None),
        ({"uniqueOverride": {}}, None),
        ({"uniqueOverride": {"asset": []}}, None),
        ({"uniqueOverride": None}, None),
        ({"uniqueOverride": {"issue": ["title"]}}, None),  # issue is not supported yet ..
        ({"uniqueOverride": {"invalid_type": ["ipAddress"]}}, None),
        ({"uniqueOverride": {"asset": [None]}}, None),
    ]

    for config, expected in config_cases:
        app.config = config
        override = IntegrationOverride(app)
        try:
            key = next(iter(config.get("uniqueOverride", {})), None)
        except TypeError:
            key = None
        assert override.field_map_validation(dict_obj, key) == expected
        del override


def test_field_map_validation_with_multiple_fields_for_multiple_integrations(random_local_ip):
    app = Mock()
    app.config = {"uniqueOverride": {"asset": ["ipAddress"]}}
    override = IntegrationOverride(app)

    dict_obj = {"ipv4": random_local_ip, "mac": "00:11:22:33:44:55", "hostname": "test.example.com"}
    assert override.field_map_validation(dict_obj, "invalid_type") is None


def test_field_map_validation_with_invalid_model_types(random_local_ip):
    app = Mock()
    app.config = {"uniqueOverride": {"asset": ["ipAddress"]}}
    override = IntegrationOverride(app)
    dict_obj = {"ipv4": random_local_ip, "mac": "00:11:22:33:44:55", "hostname": "test.example.com"}

    assert override.field_map_validation(dict_obj, "invalid_type") is None


def test_field_map_validation_with_non_dict_non_model_objects():
    app = Mock()
    app.config = {"uniqueOverride": {"asset": ["ipAddress"]}}
    override = IntegrationOverride(app)

    invalid_objects = [None, "string", 123, ["list"]]
    for obj in invalid_objects:
        assert override.field_map_validation(obj, "asset") is None
