#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example using ApiPaginator with JSONLScannerIntegration.

This file demonstrates how to use the ApiPaginator class to fetch paginated API responses
and integrate them with the JSONLScannerIntegration class.
"""

import logging
import os
from typing import Dict, Any, Union, Tuple, Iterator, Optional

import click
from pathlib import Path

from regscale.integrations.api_paginator import ApiPaginator
from regscale.integrations.jsonl_scanner_integration import (
    JSONLScannerIntegration,
    IntegrationAsset,
    IntegrationFinding,
)
from regscale.models import IssueSeverity, IssueStatus, AssetStatus

logger = logging.getLogger("regscale")


class ApiScannerExample(JSONLScannerIntegration):
    """
    Example integration class that uses ApiPaginator to fetch data.

    This class demonstrates how to combine ApiPaginator with JSONLScannerIntegration
    to create a full API-based scanner integration.
    """

    # Class constants
    title = "API Scanner Example"
    asset_identifier_field = "otherTrackingNumber"

    # Custom file paths
    ASSETS_FILE = "./artifacts/api_example_assets.jsonl"
    FINDINGS_FILE = "./artifacts/api_example_findings.jsonl"

    # Severity mapping
    finding_severity_map = {
        "CRITICAL": IssueSeverity.Critical,
        "HIGH": IssueSeverity.High,
        "MEDIUM": IssueSeverity.Moderate,
        "LOW": IssueSeverity.Low,
        "INFO": IssueSeverity.Low,
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize the ApiScannerExample integration.

        Args:
            api_url (str): Base URL for the API
            api_key (str): API key for authentication
            api_token (str): API token for authentication
        """
        # Extract API-specific parameters
        self.api_url = kwargs.pop("api_url", None)
        self.api_key = kwargs.pop("api_key", None)
        self.api_token = kwargs.pop("api_token", None)

        # Set file pattern
        kwargs["file_pattern"] = "*.json"

        # Call parent initializer
        super().__init__(*args, **kwargs)

        # Create API paginator
        self.paginator = self._create_paginator()

    def _create_paginator(self) -> ApiPaginator:
        """
        Create an ApiPaginator instance configured for this integration.

        Returns:
            ApiPaginator: Configured paginator instance
        """
        if not self.api_url:
            raise ValueError("API URL is required")

        # Create authentication headers
        auth_headers = {}
        if self.api_key:
            auth_headers["X-API-Key"] = self.api_key
        if self.api_token:
            auth_headers["Authorization"] = f"Bearer {self.api_token}"

        # Create paginator with default settings
        return ApiPaginator(
            base_url=self.api_url,
            auth_headers=auth_headers,
            output_file=None,  # We'll set this per-operation
            page_size=100,
            timeout=30,
            retry_attempts=3,
            ssl_verify=self.ssl_verify,
        )

    def fetch_assets_from_api(self) -> None:
        """
        Fetch assets from the API and write them to the ASSETS_FILE.
        """
        logger.info(f"Fetching assets from API {self.api_url}")

        # Ensure artifacts directory exists
        os.makedirs(os.path.dirname(self.ASSETS_FILE), exist_ok=True)

        # Configure paginator for this operation
        self.paginator.output_file = self.ASSETS_FILE
        self.paginator.clear_output_file()  # Clear any existing data

        # Fetch assets with pagination
        try:
            self.paginator.fetch_paginated_results(
                endpoint="assets", params={"type": "all"}, data_path="items", pagination_type="offset"
            )
            logger.info(f"Successfully wrote assets to {self.ASSETS_FILE}")
        except Exception as e:
            logger.error(f"Error fetching assets: {str(e)}")
            raise

    def fetch_findings_from_api(self) -> None:
        """
        Fetch findings from the API and write them to the FINDINGS_FILE.
        """
        logger.info(f"Fetching findings from API {self.api_url}")

        # Ensure artifacts directory exists
        os.makedirs(os.path.dirname(self.FINDINGS_FILE), exist_ok=True)

        # Configure paginator for this operation
        self.paginator.output_file = self.FINDINGS_FILE
        self.paginator.clear_output_file()  # Clear any existing data

        # Fetch findings with pagination
        try:
            self.paginator.fetch_paginated_results(
                endpoint="findings", params={"status": "open"}, data_path="items", pagination_type="offset"
            )
            logger.info(f"Successfully wrote findings to {self.FINDINGS_FILE}")
        except Exception as e:
            logger.error(f"Error fetching findings: {str(e)}")
            raise

    def fetch_assets_and_findings_from_api(self) -> Tuple[str, str]:
        """
        Fetch both assets and findings from the API.

        Returns:
            Tuple[str, str]: Paths to the assets and findings files
        """
        self.fetch_assets_from_api()
        self.fetch_findings_from_api()
        return self.ASSETS_FILE, self.FINDINGS_FILE

    def find_valid_files(self, path: Union[Path, str]) -> Iterator[Tuple[Union[Path, str], Dict[str, Any]]]:
        """
        Override to use our API fetcher instead of looking for files.

        Args:
            path (Union[Path, str]): Path to search for files (ignored)

        Returns:
            Iterator: Iterator of (path, data) tuples
        """
        # Instead of searching for files, we'll fetch directly from the API
        # This demonstrates how to inject the API fetching into the JSONLScannerIntegration flow

        # Fetch data from API and use the JSONL files as our source
        self.fetch_assets_and_findings_from_api()

        # Use the parent class's file finding method to process the JSONL files we created
        artifacts_dir = Path("./artifacts")
        if artifacts_dir.exists():
            yield from super().find_valid_files(artifacts_dir)

    def is_valid_file(self, data: Any, file_path: Union[Path, str]) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate that the file has the expected structure.

        Args:
            data (Any): Data parsed from the file
            file_path (Union[Path, str]): Path to the file

        Returns:
            Tuple[bool, Optional[Dict[str, Any]]]: (is_valid, validated_data)
        """
        if not isinstance(data, dict):
            return False, None

        # Simple validation - this would be more specific in a real integration
        return True, data

    def parse_asset(self, file_path: Union[Path, str], data: Dict[str, Any]) -> IntegrationAsset:
        """
        Parse a single asset from source data.

        Args:
            file_path (Union[Path, str]): Path to the file
            data (Dict[str, Any]): The parsed data

        Returns:
            IntegrationAsset: Parsed asset object
        """
        # Extract basic asset information
        asset_id = data.get("id", "unknown")
        asset_name = data.get("name", f"Asset {asset_id}")
        asset_type = data.get("type", "Other")

        return IntegrationAsset(
            identifier=asset_id,
            name=asset_name,
            asset_type=asset_type,
            asset_category=data.get("category", "Software"),
            ip_address=data.get("ipAddress", ""),
            status=AssetStatus.Active,
            parent_id=self.plan_id,
            parent_module="securityplans",
            source_data=data,
        )

    def parse_finding(self, asset_identifier: str, data: Dict[str, Any], item: Dict[str, Any]) -> IntegrationFinding:
        """
        Parse a single finding from source data.

        Args:
            asset_identifier (str): Identifier of the asset this finding belongs to
            data (Dict[str, Any]): The asset data
            item (Dict[str, Any]): The finding data

        Returns:
            IntegrationFinding: Parsed finding object
        """
        # Map severity from source to RegScale severity
        raw_severity = item.get("severity", "MEDIUM")
        severity = self.finding_severity_map.get(raw_severity, IssueSeverity.Moderate)

        return IntegrationFinding(
            title=item.get("title", "Unknown Finding"),
            description=item.get("description", "No description available"),
            severity=severity,
            status=IssueStatus.Open,
            asset_identifier=asset_identifier,
            category="Vulnerability",
            control_labels=[],  # Add control labels if applicable
            plugin_name=self.title,
            cve=item.get("cveId", ""),
            cvss_v3_score=item.get("cvssScore", None),
            recommendation_for_mitigation=item.get("remediation", ""),
            scan_date=self.scan_date,
        )

    def _get_findings_data_from_file(self, data: Dict[str, Any]) -> list:
        """
        Extract findings data from file data.

        Args:
            data (Dict[str, Any]): The data from the file

        Returns:
            list: List of finding items
        """
        # In our example, findings are directly in the data
        # In a real integration, this might navigate a more complex structure
        return [data] if data else []


@click.group()
def api_scanner():
    """API Scanner Integration commands."""
    pass


@api_scanner.command(name="sync_assets")
@click.option("--api-url", required=True, help="Base URL for the API")
@click.option("--api-key", help="API key for authentication")
@click.option("--api-token", help="API token for authentication")
@click.option("--plan-id", required=True, type=int, help="RegScale ID to create assets under")
def sync_assets(api_url: str, api_key: str, api_token: str, plan_id: int):
    """Sync assets from API to RegScale."""
    integration = ApiScannerExample(
        plan_id=plan_id,
        api_url=api_url,
        api_key=api_key,
        api_token=api_token,
    )

    # Fetch assets from API
    integration.fetch_assets_from_api()

    # Process assets
    assets = integration.fetch_assets()
    count = integration.update_regscale_assets(assets)

    logger.info(f"Synchronized {count} assets from API to RegScale")


@api_scanner.command(name="sync_findings")
@click.option("--api-url", required=True, help="Base URL for the API")
@click.option("--api-key", help="API key for authentication")
@click.option("--api-token", help="API token for authentication")
@click.option("--plan-id", required=True, type=int, help="RegScale ID to create findings under")
def sync_findings(api_url: str, api_key: str, api_token: str, plan_id: int):
    """Sync findings from API to RegScale."""
    integration = ApiScannerExample(
        plan_id=plan_id,
        api_url=api_url,
        api_key=api_key,
        api_token=api_token,
    )

    # Fetch findings from API
    integration.fetch_findings_from_api()

    # Process findings
    findings = integration.fetch_findings()
    count = integration.update_regscale_findings(findings)

    logger.info(f"Synchronized {count} findings from API to RegScale")


@api_scanner.command(name="sync_all")
@click.option("--api-url", required=True, help="Base URL for the API")
@click.option("--api-key", help="API key for authentication")
@click.option("--api-token", help="API token for authentication")
@click.option("--plan-id", required=True, type=int, help="RegScale ID for synchronization")
def sync_all(api_url: str, api_key: str, api_token: str, plan_id: int):
    """Sync both assets and findings from API to RegScale."""
    integration = ApiScannerExample(
        plan_id=plan_id,
        api_url=api_url,
        api_key=api_key,
        api_token=api_token,
    )

    # Fetch and process both assets and findings
    integration.sync_assets_and_findings()

    logger.info("Synchronized assets and findings from API to RegScale")


if __name__ == "__main__":
    api_scanner()
