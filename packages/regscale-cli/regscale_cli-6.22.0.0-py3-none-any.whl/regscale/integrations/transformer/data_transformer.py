#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Transformer Module

This module provides a DataTransformer class that can transform data from
various formats (JSON, XML, dict) into IntegrationAsset and IntegrationFinding objects
using a mapping file.
"""

import json
import logging
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Optional, Union

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import regscale_models

logger = logging.getLogger("regscale")


@dataclass
class DataMapping:
    """
    Data structure to hold mapping configuration for transforming data.
    """

    asset_mapping: Dict[str, str]
    finding_mapping: Dict[str, str]
    asset_defaults: Dict[str, Any]
    finding_defaults: Dict[str, Any]
    severity_mapping: Dict[str, str]


class DataTransformer:
    """
    Transforms data from various formats (JSON, XML, dict) into IntegrationAsset and
    IntegrationFinding objects using a mapping file.

    This class provides functionality to:
    1. Load mapping configurations
    2. Transform source data into IntegrationAsset objects
    3. Transform source data into IntegrationFinding objects
    4. Handle different input formats (JSON, XML, dict)

    The mapping file should contain mappings for both assets and findings,
    as well as default values and transformations.
    """

    def __init__(self, mapping_file: Optional[str] = None, mapping_data: Optional[Dict[str, Any]] = None):
        """
        Initialize the DataTransformer with a mapping file or mapping data.

        Args:
            mapping_file (Optional[str]): Path to the mapping file (JSON format)
            mapping_data (Optional[Dict[str, Any]]): Mapping data as a dictionary

        Raises:
            ValueError: If neither mapping_file nor mapping_data is provided
        """
        if not mapping_file and not mapping_data:
            raise ValueError("Either mapping_file or mapping_data must be provided")

        self.mapping = self._load_mapping(mapping_file, mapping_data)
        self.scan_date = get_current_datetime()

    def _load_mapping(self, mapping_file: Optional[str], mapping_data: Optional[Dict[str, Any]]) -> DataMapping:
        """
        Load mapping configuration from a file or dictionary.

        Args:
            mapping_file (Optional[str]): Path to the mapping file
            mapping_data (Optional[Dict[str, Any]]): Mapping data as a dictionary

        Returns:
            DataMapping: The loaded mapping configuration

        Raises:
            FileNotFoundError: If the mapping file does not exist
            json.JSONDecodeError: If the mapping file is not valid JSON
        """
        if mapping_file and os.path.exists(mapping_file):
            logger.info(f"Loading mapping from file: {mapping_file}")
            try:
                with open(mapping_file, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing mapping file {mapping_file}: {str(e)}")
                raise
        elif mapping_data:
            logger.info("Using provided mapping data")
            data = mapping_data
        else:
            raise FileNotFoundError(f"Mapping file {mapping_file} not found")

        return DataMapping(
            asset_mapping=data.get("asset_mapping", {}),
            finding_mapping=data.get("finding_mapping", {}),
            asset_defaults=data.get("asset_defaults", {}),
            finding_defaults=data.get("finding_defaults", {}),
            severity_mapping=data.get("severity_mapping", {}),
        )

    def _get_data_value(self, data: Dict[str, Any], field_path: str, default: Any = None) -> Any:
        """
        Extract a value from nested data using a dot-notation path.

        Args:
            data (Dict[str, Any]): The data to extract from
            field_path (str): The path to the field (e.g., 'asset.info.name')
            default (Any): Default value if the field is not found

        Returns:
            Any: The extracted value or the default
        """
        if not field_path:
            return default

        parts = field_path.split(".")
        current = data

        try:
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list) and part.isdigit():
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return default
                else:
                    return default
            return current
        except (KeyError, TypeError, IndexError):
            return default

    def _apply_mapping(
        self, source_data: Dict[str, Any], mapping: Dict[str, str], defaults: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply mapping configuration to source data.

        Args:
            source_data (Dict[str, Any]): The source data to transform
            mapping (Dict[str, str]): The field mapping (target_field -> source_field_path)
            defaults (Dict[str, Any]): Default values for fields

        Returns:
            Dict[str, Any]: The transformed data
        """
        result = {}

        # Apply defaults first
        for field, value in defaults.items():
            result[field] = value

        # Apply mappings, overriding defaults if needed
        for target_field, source_path in mapping.items():
            value = self._get_data_value(source_data, source_path)
            if value is not None:
                result[target_field] = value

        return result

    def _parse_data_source(self, data_source: Union[str, Dict[str, Any], bytes]) -> Dict[str, Any]:
        """
        Parse the data source into a dictionary.

        Args:
            data_source: The data source (JSON string, XML string, dictionary, or file path)

        Returns:
            Dict[str, Any]: The parsed data

        Raises:
            ValueError: If the data source format is not recognized
        """
        if isinstance(data_source, dict):
            return data_source

        if isinstance(data_source, str):
            # Check if it's a file path
            if os.path.exists(data_source):
                with open(data_source, "r") as f:
                    content = f.read()
            else:
                content = data_source

            # Try to parse as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass

            # Try to parse as XML
            try:
                root = ET.fromstring(content)
                return self._xml_to_dict(root)
            except ET.ParseError:
                pass

            raise ValueError(f"Could not parse data source as JSON or XML: {data_source[:50]}...")

        if isinstance(data_source, bytes):
            # Try to parse as JSON
            try:
                return json.loads(data_source)
            except json.JSONDecodeError:
                pass

            # Try to parse as XML
            try:
                root = ET.fromstring(data_source.decode("utf-8"))
                return self._xml_to_dict(root)
            except ET.ParseError:
                pass

            raise ValueError("Could not parse data source as JSON or XML")

        raise ValueError(f"Unsupported data source type: {type(data_source)}")

    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """
        Convert an XML element to a dictionary.

        Args:
            element (ET.Element): The XML element to convert

        Returns:
            Dict[str, Any]: The converted dictionary
        """
        result = {}

        # Add attributes
        for key, value in element.attrib.items():
            result[f"@{key}"] = value

        # Add children
        for child in element:
            child_data = self._xml_to_dict(child)

            if child.tag in result:
                if isinstance(result[child.tag], list):
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = [result[child.tag], child_data]
            else:
                result[child.tag] = child_data

        # Add text content
        if element.text and element.text.strip():
            if result:
                result["#text"] = element.text.strip()
            else:
                return element.text.strip()

        return result

    def transform_to_asset(
        self, data_source: Union[str, Dict[str, Any], bytes], plan_id: Optional[int] = None
    ) -> IntegrationAsset:
        """
        Transform data source into an IntegrationAsset object.

        Args:
            data_source: The data source to transform
            plan_id (Optional[int]): The ID of the security plan

        Returns:
            IntegrationAsset: The transformed asset
        """
        data = self._parse_data_source(data_source)

        # Apply mapping
        mapped_data = self._apply_mapping(data, self.mapping.asset_mapping, self.mapping.asset_defaults)

        # Ensure required fields have values
        if "name" not in mapped_data:
            mapped_data["name"] = "Unknown Asset"

        if "identifier" not in mapped_data:
            if "ip_address" in mapped_data:
                mapped_data["identifier"] = mapped_data["ip_address"]
            else:
                mapped_data["identifier"] = mapped_data["name"]

        # Add plan ID if provided
        if plan_id:
            mapped_data["parent_id"] = plan_id
            mapped_data["parent_module"] = regscale_models.SecurityPlan.get_module_slug()

        # Create IntegrationAsset
        return IntegrationAsset(**mapped_data)

    def transform_to_finding(
        self, data_source: Union[str, Dict[str, Any], bytes], asset_identifier: Optional[str] = None
    ) -> IntegrationFinding:
        """
        Transform data source into an IntegrationFinding object.

        Args:
            data_source: The data source to transform
            asset_identifier (Optional[str]): The identifier of the associated asset

        Returns:
            IntegrationFinding: The transformed finding
        """
        data = self._parse_data_source(data_source)

        # Apply mapping
        mapped_data = self._apply_mapping(data, self.mapping.finding_mapping, self.mapping.finding_defaults)

        # Map severity if needed
        if "severity" in mapped_data:
            raw_severity = str(mapped_data["severity"])
            if raw_severity in self.mapping.severity_mapping:
                mapped_severity = self.mapping.severity_mapping[raw_severity]
                try:
                    mapped_data["severity"] = getattr(regscale_models.IssueSeverity, mapped_severity)
                except AttributeError:
                    logger.warning(f"Invalid severity mapping: {mapped_severity}")

        # Ensure required fields have values
        if "title" not in mapped_data:
            mapped_data["title"] = "Unknown Finding"

        if "description" not in mapped_data:
            mapped_data["description"] = "No description available"

        if "category" not in mapped_data:
            mapped_data["category"] = "Vulnerability"

        if "control_labels" not in mapped_data:
            mapped_data["control_labels"] = []

        if "plugin_name" not in mapped_data:
            mapped_data["plugin_name"] = mapped_data["title"]

        if "status" not in mapped_data:
            mapped_data["status"] = regscale_models.IssueStatus.Open

        # Set the asset identifier
        if asset_identifier:
            mapped_data["asset_identifier"] = asset_identifier
        elif "asset_identifier" not in mapped_data:
            mapped_data["asset_identifier"] = ""

        # Set scan date
        if "scan_date" not in mapped_data:
            mapped_data["scan_date"] = self.scan_date

        # Create IntegrationFinding
        return IntegrationFinding(**mapped_data)

    def batch_transform_to_assets(
        self, data_sources: List[Union[str, Dict[str, Any], bytes]], plan_id: Optional[int] = None
    ) -> Iterator[IntegrationAsset]:
        """
        Transform multiple data sources into IntegrationAsset objects.

        Args:
            data_sources: List of data sources to transform
            plan_id (Optional[int]): The ID of the security plan

        Yields:
            IntegrationAsset: The transformed assets
        """
        for data_source in data_sources:
            try:
                yield self.transform_to_asset(data_source, plan_id)
            except Exception as e:
                logger.error(f"Error transforming data source to asset: {str(e)}")

    def batch_transform_to_findings(
        self, data_sources: List[Union[str, Dict[str, Any], bytes]], asset_identifier: Optional[str] = None
    ) -> Iterator[IntegrationFinding]:
        """
        Transform multiple data sources into IntegrationFinding objects.

        Args:
            data_sources: List of data sources to transform
            asset_identifier (Optional[str]): The identifier of the associated asset

        Yields:
            IntegrationFinding: The transformed findings
        """
        for data_source in data_sources:
            try:
                yield self.transform_to_finding(data_source, asset_identifier)
            except Exception as e:
                logger.error(f"Error transforming data source to finding: {str(e)}")


# Example Tenable SC mapping file structure for reference
TENABLE_SC_MAPPING = {
    "asset_mapping": {
        "name": "dnsName",
        "identifier": "ip",
        "ip_address": "ip",
        "mac_address": "macAddress",
        "asset_type": "family.type",
        "asset_category": "Hardware",
        "fqdn": "dnsName",
        "status": "",  # Will be handled by transformation logic
    },
    "finding_mapping": {
        "title": "pluginName",
        "description": "description",
        "plugin_name": "pluginName",
        "plugin_id": "pluginID",
        "severity": "severity.name",
        "category": "family.name",
        "cve": "cve",
        "cvss_v3_score": "cvssV3BaseScore",
        "cvss_v2_score": "cvssV2BaseScore",
        "cvss_v3_vector": "cvssV3Vector",
        "cvss_v2_vector": "cvssV2Vector",
        "recommendation_for_mitigation": "solution",
        "identified_risk": "risk_factor",
        "evidence": "output",
    },
    "asset_defaults": {
        "asset_owner_id": "",  # Will be set by ScannerIntegration
        "status": "Active (On Network)",
        "asset_type": "Other",
        "asset_category": "Hardware",
    },
    "finding_defaults": {"priority": "Medium", "status": "Open", "issue_type": "Risk"},
    "severity_mapping": {
        "Critical": "Critical",
        "High": "High",
        "Medium": "Moderate",
        "Low": "Low",
        "Info": "NotAssigned",
        "4": "Critical",
        "3": "High",
        "2": "Moderate",
        "1": "Low",
        "0": "NotAssigned",
    },
}
