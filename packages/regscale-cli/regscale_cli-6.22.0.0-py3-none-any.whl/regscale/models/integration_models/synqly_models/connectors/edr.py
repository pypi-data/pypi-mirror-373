"""Vulnerabilities Connector Model"""

from typing import Iterator, Optional

from pydantic import ConfigDict

from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, ScannerIntegration
from regscale.models.integration_models.synqly_models.synqly_model import SynqlyModel
from regscale.models.regscale_models import IssueSeverity


class EDRIntegration(ScannerIntegration):
    title = "EDR Connector Integration"
    # Required fields from ScannerIntegration
    asset_identifier_field = "otherTrackingNumber"
    finding_severity_map = {
        "Critical": IssueSeverity.Critical,
        "High": IssueSeverity.High,
        "Medium": IssueSeverity.Moderate,
        "Low": IssueSeverity.Low,
    }

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from Synqly

        :yields: Iterator[IntegrationAsset]
        """
        integration_assets = kwargs.get("integration_assets")
        for asset in integration_assets:
            yield asset

    def fetch_findings(self, *args, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from the Synqly

        :yields: Iterator[IntegrationFinding]
        """
        integration_findings = kwargs.get("integration_findings")
        for finding in integration_findings:
            yield finding


class Edr(SynqlyModel):
    """Edr Connector Model"""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True, arbitrary_types_allowed=True)

    integration_id: str = ""
    scanner_integration: Optional["EDRIntegration"] = None
    provider: str = ""
    can_fetch_apps: bool = False
    can_fetch_alerts: bool = False
    can_fetch_endpoints: bool = False

    def __init__(self, integration: str, **kwargs):
        SynqlyModel.__init__(self, connector_type=self.__class__.__name__, integration=integration, **kwargs)
        self.integration_id = f"{self._connector_type.lower()}_{self.integration.lower()}"
        integration_company = self.integration.split("_")[0] if "_" in self.integration else self.integration  # noqa
        self.provider = integration_company
        self.can_fetch_apps = "query_applications" in self.capabilities
        self.can_fetch_alerts = "query_alerts" in self.capabilities
        self.can_fetch_endpoints = "query_endpoints" in self.capabilities

    def integration_sync(self, regscale_ssp_id: int, **kwargs) -> None:
        """
        Runs the integration sync process

        :param int regscale_ssp_id: The RegScale SSP ID
        :rtype: None
        """
        self.logger.info(f"Fetching alert data from {self.integration_name}...")
        alerts = (
            self.fetch_integration_data(
                func=self.tenant.engine_client.edr.query_alerts,
                **kwargs,
            )
            if self.can_fetch_alerts
            else []
        )
        self.logger.info(f"Fetching application data from {self.integration_name}...")
        apps = (
            self.fetch_integration_data(func=self.tenant.engine_client.edr.query_applications, **kwargs)
            if self.can_fetch_apps
            else []
        )
        endpoints = (
            self.fetch_integration_data(func=self.tenant.engine_client.edr.query_endpoints, **kwargs)
            if self.can_fetch_endpoints
            else []
        )

        edr_data = {"alert(s)": alerts, "app(s)": apps, "endpoint(s)": endpoints}
        integration_assets: list[IntegrationAsset] = []
        integration_findings: list[IntegrationFinding] = []

        for name, data in edr_data.items():
            if data:
                self.logger.info(f"Mapping {len(data)} {self.provider} {name} to RegScale data...")
                self.app.thread_manager.submit_tasks_from_list(
                    func=self.mapper.to_regscale,
                    items=data,
                    args=None,
                    connector=self,
                    regscale_ssp_id=regscale_ssp_id,
                    **kwargs,
                )
                if mapped_data := self.app.thread_manager.execute_and_verify(return_passed=True):
                    if isinstance(mapped_data[0], IntegrationFinding):
                        self.logger.info(f"Mapped {len(mapped_data)} {self.provider} {name} to RegScale finding(s).")
                        integration_findings.extend(mapped_data)
                    elif isinstance(mapped_data[0], IntegrationAsset):
                        self.logger.info(f"Mapped {len(mapped_data)} {self.provider} {name} to RegScale asset(s).")
                        integration_assets.extend(mapped_data)

        self.scanner_integration = EDRIntegration(plan_id=regscale_ssp_id)
        self.scanner_integration.sync_assets(
            title=f"{self.integration_name} EDR",
            plan_id=regscale_ssp_id,
            integration_assets=integration_assets,
            asset_count=len(integration_assets),
        )
        self.scanner_integration.sync_findings(
            title=f"{self.integration_name} EDR",
            plan_id=regscale_ssp_id,
            integration_findings=integration_findings,
            finding_count=len(integration_findings),
        )
        self.logger.info(f"[green]Sync from {self.integration_name} to RegScale completed.")

    def run_sync(self, *args, **kwargs) -> None:
        """
        Syncs RegScale issues with Vulnerability connector using Synqly

        :rtype: None
        """
        self.run_integration_sync(*args, **kwargs)
