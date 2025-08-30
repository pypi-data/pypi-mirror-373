"""Assets Connector Model"""

from typing import Iterator, Optional

from pydantic import ConfigDict

from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, ScannerIntegration
from regscale.models.integration_models.synqly_models.synqly_model import SynqlyModel
from regscale.models.regscale_models import IssueSeverity


class AssetsIntegration(ScannerIntegration):
    title = "Assets Connector Integration"
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
        Unused method, but required by the parent class

        :yields: Iterator[IntegrationFinding]
        """
        pass


class Assets(SynqlyModel):
    """Assets Connector Model"""

    integration_id: str = ""
    scanner_integration: Optional["AssetsIntegration"] = None
    provider: str = ""
    can_fetch_assets: bool = False

    def __init__(self, integration: str, **kwargs):
        SynqlyModel.__init__(self, connector_type=self.__class__.__name__, integration=integration, **kwargs)
        self.integration_id = f"{self._connector_type.lower()}_{self.integration.lower()}"
        integration_company = self.integration.split("_")[0] if "_" in self.integration else self.integration  # noqa
        self.provider = integration_company
        self.can_fetch_assets = "query_devices" in self.capabilities

    def integration_sync(self, regscale_ssp_id: int, **kwargs) -> None:
        """
        Runs the integration sync process

        :param int regscale_ssp_id: The RegScale SSP ID
        :rtype: None
        """
        self.logger.info(f"Fetching asset data from {self.integration_name}...")
        assets = (
            self.fetch_integration_data(func=self.tenant.engine_client.assets.query_devices, **kwargs)
            if self.can_fetch_assets
            else []
        )
        self.scanner_integration = AssetsIntegration(plan_id=regscale_ssp_id)
        self.logger.info(f"Mapping {self.provider} asset(s) data to RegScale asset(s)...")
        if assets:
            self.app.thread_manager.submit_tasks_from_list(
                func=self.mapper.to_regscale,
                items=assets,
                args=None,
                connector=self,
                regscale_ssp_id=regscale_ssp_id,
                **kwargs,
            )
            integration_assets = self.app.thread_manager.execute_and_verify(return_passed=True)
            self.logger.info(f"Mapped {len(integration_assets)} {self.provider} asset(s) to RegScale asset(s)...")
            self.scanner_integration.sync_assets(
                title=f"{self.integration_name} Assets",
                plan_id=regscale_ssp_id,
                integration_assets=integration_assets,
                asset_count=len(integration_assets),
            )

        self.logger.info(f"[green]Sync from {self.integration_name} to RegScale completed.")

    def run_sync(self, *args, **kwargs) -> None:
        """
        Syncs RegScale issues with Assets connector using Synqly

        :rtype: None
        """
        self.run_integration_sync(*args, **kwargs)
