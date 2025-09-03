import logging
from unittest.mock import Mock

from regscale.models.integration_models.sbom.cyclone_dx import CycloneDXJsonGenerator


def test_initialization():
    device = {"deviceName": "test-device", "manufacturer": "Test Corp"}
    generator = CycloneDXJsonGenerator(device)

    assert generator.device == device
    assert isinstance(generator.logger, logging.Logger)
    assert generator.device_info.name == "test-device"
    assert generator.device_info.manufacturer == "Test Corp"


def test_initialization_custom_logger():
    logger = Mock()
    generator = CycloneDXJsonGenerator({}, logger)
    assert generator.logger == logger


def test_device_description_generation():
    device = {"manufacturer": "Test Corp", "model": "Model X", "deviceType": "Router"}
    generator = CycloneDXJsonGenerator(device)
    description = generator.generate_device_description()
    assert description == "Test Corp Model X Router"


def test_device_description_partial_info():
    device = {"model": "Model X"}
    generator = CycloneDXJsonGenerator(device)
    description = generator.generate_device_description()
    assert description == "Model X"


def test_device_description_empty():
    generator = CycloneDXJsonGenerator({})
    description = generator.generate_device_description()
    assert description == "Unknown Device"


def test_component_validation():
    generator = CycloneDXJsonGenerator({})
    valid_component = {"type": "library", "name": "test-lib"}
    invalid_type = {"type": "invalid", "name": "test"}
    missing_field = {"type": "library"}

    assert generator.validate(valid_component)
    assert not generator.validate(invalid_type)
    assert not generator.validate(missing_field)


def test_generate_sbom():
    device = {"deviceName": "test-device", "manufacturer": "Test Corp", "easDeviceId": "device-123"}
    components = [{"type": "library", "name": "lib1"}, {"type": "framework", "name": "framework1"}]

    generator = CycloneDXJsonGenerator(device)
    sbom = generator.generate_sbom(components)

    assert sbom["bomFormat"] == "CycloneDX"
    assert sbom["specVersion"] == "1.4"
    assert len(sbom["components"]) == 3  # device + 2 components
    assert len(sbom["dependencies"]) == 1
    assert sbom["dependencies"][0]["ref"] == "device-123"
    assert len(sbom["dependencies"][0]["dependsOn"]) == 2


def test_generate_sbom_invalid_components():
    device = {"deviceName": "test-device"}
    components = [
        {"type": "library", "name": "lib1"},
        {"type": "invalid", "name": "invalid1"},
        {"name": "missing-type"},
    ]

    generator = CycloneDXJsonGenerator(device)
    sbom = generator.generate_sbom(components)

    assert len(sbom["components"]) == 2  # device + 1 valid component


def test_sbom_metadata():
    generator = CycloneDXJsonGenerator({})
    sbom = generator.generate_sbom([])

    assert sbom["metadata"]["tools"][0]["name"] == "RegScale CLI"
