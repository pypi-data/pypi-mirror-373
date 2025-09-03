"""
Intune Integration
"""

import logging
from typing import Any, Dict, Iterator

from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, ScannerIntegration
from regscale.models import regscale_models

logger = logging.getLogger("regscale")


class IntuneIntegration(ScannerIntegration):
    """Integration class for Intune Device Manager."""

    title: str = "Intune"
    asset_identifier_field: str = "azureIdentifier"
    finding_severity_map: Dict[str, regscale_models.IssueSeverity] = {
        "critical": regscale_models.IssueSeverity.Critical,
        "high": regscale_models.IssueSeverity.High,
        "medium": regscale_models.IssueSeverity.Moderate,
        "low": regscale_models.IssueSeverity.Low,
    }

    def fetch_assets(self, *args: Any, **kwargs: Any) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from Intune integration

        :param Tuple args: Additional arguments
        :param dict kwargs: Additional keyword arguments
        :yields: Iterator[IntegrationAsset]
        """
        if asset_num := kwargs.get("asset_num"):
            self.num_assets_to_process = asset_num
        integration_assets = kwargs.get("integration_assets")
        yield from integration_assets

    def fetch_findings(self, *args: Any, **kwargs: dict) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from the Intune integration

        :param Tuple args: Additional arguments
        :param dict kwargs: Additional keyword arguments
        :yields: Iterator[IntegrationFinding]

        """
        integration_findings = kwargs.get("integration_findings")
        yield from integration_findings
