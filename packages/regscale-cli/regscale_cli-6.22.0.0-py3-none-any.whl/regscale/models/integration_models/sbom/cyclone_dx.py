"""
This module contains a class to generate CycloneDX SBOM JSON from a device and a list of components.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from regscale import __version__

UNKNOWN_DEVICE = "Unknown Device"


@dataclass
class DeviceInfo:
    """
    Device Information
    """

    name: str
    version: str = "1.0.0"
    manufacturer: Optional[str] = None
    description: Optional[str] = None


class CycloneDXJsonGenerator:
    """
    CycloneDX Generator
    """

    def __init__(self, device: Dict, logger=None):
        if not logger:
            import logging

            logger = logging.getLogger("regscale")
        self.logger = logger
        self.device = device
        self.device_info = DeviceInfo(
            name=device.get("deviceName", UNKNOWN_DEVICE),
            version=device.get("osVersion", "1.0.0"),
            manufacturer=device.get("manufacturer"),
            description=self.generate_device_description(),
        )

    def generate_device_description(self) -> str:
        """
        Generate device description

        :rtype: str
        :return: Device description
        """
        parts = []

        if manufacturer := self.device.get("manufacturer"):
            parts.append(manufacturer)

        if model := self.device.get("model"):
            parts.append(model)

        if device_type := self.device.get("deviceType"):
            parts.append(device_type)

        return " ".join(filter(None, parts)) if parts else UNKNOWN_DEVICE

    def generate_sbom(self, components: List[Dict]) -> Dict:
        """
        Generate CycloneDX SBOM JSON

        :param List[Dict] components: List of components
        :rtype: Dict
        :return: SBOM JSON
        """
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tools": [{"vendor": "RegScale, Inc.", "name": "RegScale CLI", "version": __version__}],
            },
            "components": [],
            "dependencies": [],
        }

        # Add device as first component
        device_ref = self.device.get("easDeviceId") or "device-001"

        device_component = {
            "type": "device",
            "name": self.device_info.name or UNKNOWN_DEVICE,
            "bom-ref": device_ref,
            "version": self.device_info.version or "1.0.0",
        }
        sbom["components"].append(device_component)

        # Add all other components
        component_refs = []
        for idx, component in enumerate(components, 1):
            if self.validate(component):
                comp_ref = f"comp-{idx:03d}"
                component_refs.append(comp_ref)
                comp = {"bom-ref": comp_ref, **component}
                sbom["components"].append(comp)

        # Add dependencies
        device_deps = {"ref": device_ref, "dependsOn": component_refs}
        sbom["dependencies"].append(device_deps)

        return sbom

    def validate(self, component: Dict) -> bool:
        """
        Validate component

        :param Dict component: Component information
        :rtype: bool
        :return: True if valid, False otherwise
        """
        required_types = {
            "application",
            "framework",
            "library",
            "container",
            "operating-system",
            "device",
            "firmware",
            "file",
        }
        try:
            if missing := {"type", "name"} - component.keys():
                raise ValueError(f"Missing required keys: {missing}")
            if component["type"] not in required_types:
                raise ValueError(f"Invalid type: {component['type']}")
            return True
        except ValueError as e:
            self.logger.error(e)
            return False
