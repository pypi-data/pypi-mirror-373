"""Vulnerabilities Connector Model"""

from typing import Iterator, Optional

from pydantic import ConfigDict

from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, ScannerIntegration
from regscale.models.integration_models.synqly_models.synqly_model import SynqlyModel
from regscale.models.regscale_models import IssueSeverity


class VulnerabilitiesIntegration(ScannerIntegration):
    title = "Vulnerabilities Connector Integration"
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


class Vulnerabilities(SynqlyModel):
    """Vulnerabilities Connector Model"""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True, arbitrary_types_allowed=True)

    integration_id: str = ""
    scanner_integration: Optional["VulnerabilitiesIntegration"] = None
    provider: str = ""
    can_fetch_assets: bool = False
    can_fetch_vulns: bool = False

    def __init__(self, integration: str, **kwargs):
        SynqlyModel.__init__(self, connector_type=self.__class__.__name__, integration=integration, **kwargs)
        self.integration_id = f"{self._connector_type.lower()}_{self.integration.lower()}"
        integration_company = self.integration.split("_")[0] if "_" in self.integration else self.integration  # noqa
        self.provider = integration_company
        self.can_fetch_assets = "query_assets" in self.capabilities
        self.can_fetch_vulns = "query_findings" in self.capabilities

    @staticmethod
    def _handle_scan_date_options(regscale_ssp_id: int, **kwargs) -> list[str]:
        """
        Handle scan date options for the integration sync process

        :param int regscale_ssp_id: The RegScale SSP ID
        :return: List of strings to filter vulnerabilities
        :rtype: list[str]
        """
        from regscale.integrations.commercial.tenablev2.utils import get_last_pull_epoch

        if vuln_filter := kwargs.get("vuln_filter"):
            kwargs.pop("vuln_filter")
            if isinstance(vuln_filter, str):
                vuln_filter = [f"severity[in]{vuln_filter}"]
        else:
            vuln_filter = ["severity[in]critical,high,medium,low"]
        if kwargs.get("all_scans"):
            vuln_filter.append("finding.last_seen_time[gte]915148800")  # Friday, January 1, 1999 12:00:00 AM UTC
        elif scan_date := kwargs.get("scan_date"):
            from regscale.core.utils.date import date_obj

            if scan_date := date_obj(scan_date):
                vuln_filter.append(f"finding.last_seen_time[gte]{scan_date.isoformat()}")
            else:
                raise ValueError(f"Invalid scan date: {scan_date}")
        else:
            vuln_filter.append(f"finding.last_seen_time[gte]{get_last_pull_epoch(regscale_ssp_id)}")
        return vuln_filter

    def integration_sync(self, regscale_ssp_id: int, **kwargs) -> None:
        """
        Runs the integration sync process

        :param int regscale_ssp_id: The RegScale SSP ID
        :rtype: None
        """
        vuln_filter = self._handle_scan_date_options(regscale_ssp_id=regscale_ssp_id, **kwargs)
        self.logger.debug(f"Vulnerability filter: {vuln_filter}")
        self.logger.info(f"Fetching vulnerability data from {self.integration_name}...")
        findings = (
            self.fetch_integration_data(
                func=self.tenant.engine_client.vulnerabilities.query_findings,
                filter=vuln_filter,
                **kwargs,
            )
            if self.can_fetch_vulns
            else []
        )
        self.logger.info(f"Fetching asset data from {self.integration_name}...")
        assets = (
            self.fetch_integration_data(func=self.tenant.engine_client.vulnerabilities.query_assets, **kwargs)
            if self.can_fetch_assets
            else []
        )

        self.scanner_integration = VulnerabilitiesIntegration(plan_id=regscale_ssp_id)
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
                title=f"{self.integration_name} Vulnerabilities",
                plan_id=regscale_ssp_id,
                integration_assets=integration_assets,
                asset_count=len(integration_assets),
            )

        if findings:
            integration_findings = []
            self.logger.info(f"Mapping {self.provider} finding(s) data to RegScale finding(s)...")
            self.app.thread_manager.submit_tasks_from_list(
                func=self.mapper.to_regscale,
                items=findings,
                args=None,
                connector=self,
                regscale_ssp_id=regscale_ssp_id,
                **kwargs,
            )
            mapped_findings = self.app.thread_manager.execute_and_verify(return_passed=True)
            for finding in mapped_findings:
                if isinstance(finding, list):
                    integration_findings.extend(finding)
                else:
                    integration_findings.append(finding)
            self.logger.info(f"Mapped {len(integration_findings)} {self.provider} finding(s) to RegScale finding(s)...")
            self.scanner_integration.sync_findings(
                title=f"{self.integration_name} Vulnerabilities",
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
