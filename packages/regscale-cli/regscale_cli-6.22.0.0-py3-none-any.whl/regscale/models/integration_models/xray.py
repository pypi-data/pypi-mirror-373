"""
JFrog Xray Scan information
"""

import logging
import traceback
from typing import Callable, Iterator, Optional

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import epoch_to_datetime, get_current_datetime, is_valid_fqdn
from regscale.exceptions import ValidationException
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import ImportValidater
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.regscale_models import IssueStatus, Vulnerability

logger = logging.getLogger(__name__)


class XRay(FlatFileImporter):
    """JFrog Xray Scan information

    :param str name: Name of the scan
    :param Application app: RegScale Application object
    :param str file_path: Path to the JSON files
    :param int regscale_ssp_id: RegScale System Security Plan ID
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        regscale_ssp_id = kwargs.get("regscale_ssp_id")
        # Combine related attributes to reduce instance attribute count
        self.scanner_config = {
            "cvss3_score": "cvss_v3_score",
            "vuln_title": "cve",
            "required_headers": ["impacted_artifact"],
        }
        # Combine mapping-related attributes
        self.mapping_config = {
            "mapping_file": kwargs.get("mappings_path"),
            "disable_mapping": kwargs.get("disable_mapping"),
        }
        self.validater = ImportValidater(
            self.scanner_config["required_headers"],
            kwargs.get("file_path"),
            self.mapping_config["mapping_file"],
            self.mapping_config["disable_mapping"],
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        xray_logger = create_logger()
        # set vuln count and asset count in constructor
        vuln_count = 0
        asset_count = 0
        for dat in self.validater.data:
            vuln_count += len(self.mapping.get_value(dat, "cves", []))
            asset_count += 1
        super().__init__(
            logger=xray_logger,
            app=Application(),
            headers=None,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            vuln_count=vuln_count,
            asset_count=asset_count,
            **kwargs,
        )

    def create_asset(self, dat: Optional[dict] = None) -> Optional[IntegrationAsset]:
        """
        Create an asset from a row in the Xray JSON file

        :param Optional[dict] dat: Data row from JSON file, defaults to None
        :return: RegScale Asset object
        :rtype: Optional[Asset]
        """

        if asset_name := self.mapping.get_value(dat, "impacted_artifact") if isinstance(dat, dict) else dat:
            return IntegrationAsset(
                **{
                    "name": asset_name,
                    "ip_address": "0.0.0.0",
                    "identifier": asset_name,
                    "other_tracking_number": asset_name,
                    "status": "Active (On Network)",
                    "asset_category": "Hardware",
                    "asset_type": "Other",
                    "scanning_tool": self.name,
                    "fqdn": asset_name if is_valid_fqdn(asset_name) else None,
                    "operating_system": "Linux",
                }
            )
        return None

    def create_asset_from_name(self, asset_name: str) -> IntegrationAsset:
        """Create an IntegrationAsset from an asset name

        :param str asset_name: The name of the asset
        :return: IntegrationAsset object
        :rtype: IntegrationAsset
        """
        return IntegrationAsset(
            **{
                "name": asset_name,
                "ip_address": "0.0.0.0",
                "identifier": asset_name,
                "other_tracking_number": asset_name,
                "status": "Active (On Network)",
                "asset_category": "Hardware",
                "asset_type": "Other",
                "scanning_tool": self.name,
                "fqdn": asset_name if is_valid_fqdn(asset_name) else None,
                "operating_system": "Linux",
            }
        )

    def _extract_asset_name(self, data_item) -> Optional[str]:
        """Extract asset name from data item

        :param data_item: Data item to extract asset name from
        :return: Asset name if found, None otherwise
        :rtype: Optional[str]
        """
        if isinstance(data_item, dict):
            return self.mapping.get_value(data_item, "impacted_artifact")
        return data_item if data_item else None

    def _process_list_data(self) -> Iterator[IntegrationAsset]:
        """Process list data and yield assets

        :return: Iterator of IntegrationAsset objects
        :rtype: Iterator[IntegrationAsset]
        """
        for data_item in self.file_data:
            if asset_name := self._extract_asset_name(data_item):
                yield self.create_asset_from_name(asset_name)

    def _process_dict_data(self) -> Iterator[IntegrationAsset]:
        """Process dict data and yield assets

        :return: Iterator of IntegrationAsset objects
        :rtype: Iterator[IntegrationAsset]
        """
        if asset_name := self._extract_asset_name(self.file_data):
            yield self.create_asset_from_name(asset_name)

    def asset_generator(self) -> Iterator[IntegrationAsset]:
        """Generate IntegrationAsset objects from the data

        :return: Iterator of IntegrationAsset objects
        :rtype: Iterator[IntegrationAsset]
        """
        if isinstance(self.file_data, list):
            yield from self._process_list_data()
        elif isinstance(self.file_data, dict):
            yield from self._process_dict_data()

    def process_assets(self, func: Callable) -> None:
        """
        Process the assets in the data and create an iterator of IntegrationAsset objects

        :param Callable func: Function to create asset (not used)
        :return: None
        """

        # Set the assets as an iterator directly
        self.data["assets"] = self.asset_generator()
        self.integration_assets = self.data["assets"]

    def create_vuln(self, _dat: Optional[dict] = None, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from the processed json files

        :param Optional[dict] _dat: Data row from JSON file (unused, kept for compatibility)
        :param **kwargs: Additional keyword arguments including index
        :return: A list of findings
        :rtype: Iterator[IntegrationFinding]
        """
        if findings := self.fetch_findings(**kwargs):
            yield from findings

    def _validate_cve_data(self, cve_data) -> bool:
        """Validate CVE data structure

        :param cve_data: CVE data to validate
        :return: True if valid, False otherwise
        :rtype: bool
        """
        if not isinstance(cve_data, list):
            logger.warning("CVE data is not a list, skipping vulnerability creation")
            return False
        return True

    def _get_valid_cve_data(self, cve_data: list) -> list:
        """Filter CVE data to only include valid entries

        :param list cve_data: Raw CVE data
        :return: Filtered CVE data with actual CVE IDs
        :rtype: list
        """
        return [c for c in cve_data if c.get("cve")]

    def _determine_severity_from_cve(self, cve_dat: dict) -> str:
        """Determine severity from CVE data

        :param dict cve_dat: CVE data dictionary
        :return: Severity string
        :rtype: str
        """
        cvss3_score = cve_dat.get("cvss_v3_score", 0.0)
        if cve_dat.get(self.scanner_config["cvss3_score"]):
            return Vulnerability.determine_cvss3_severity_text(float(cvss3_score))
        return "low"

    def _extract_plugin_id(self, data_item: dict) -> int:
        """Extract plugin ID from issue ID

        :param dict data_item: Data item containing issue information
        :return: Plugin ID as integer
        :rtype: int
        """
        issue_id = self.mapping.get_value(data_item, "issue_id", "Xray-0000")
        try:
            if len(issue_id) > 5:
                return int(issue_id[5:])
            return 0
        except (ValueError, TypeError):
            logger.warning("Could not parse plugin_id from issue_id: %s", issue_id)
            return 0

    def _get_title_base(self, data_item: dict) -> str:
        """Get title base for the finding

        :param dict data_item: Data item containing issue information
        :return: Title base string
        :rtype: str
        """
        return self.mapping.get_value(data_item, "issue_id") or self.mapping.get_value(
            data_item, "summary", f"XRay Vulnerability from Import {get_current_datetime()}"
        )

    def _create_finding_from_cve(self, data_item: dict, asset_name: str, cve_dat: dict) -> IntegrationFinding:
        """Create a single finding from CVE data

        :param dict data_item: Data item containing vulnerability information
        :param str asset_name: Asset name for the finding
        :param dict cve_dat: CVE data dictionary
        :return: IntegrationFinding object
        :rtype: IntegrationFinding
        """
        cve = cve_dat.get("cve")
        cvss3_score = cve_dat.get("cvss_v3_score", 0.0)
        severity = self._determine_severity_from_cve(cve_dat)
        plugin_id = self._extract_plugin_id(data_item)
        title_base = self._get_title_base(data_item)

        return IntegrationFinding(
            title=f"{title_base} on asset {asset_name}",
            description=self.mapping.get_value(data_item, "summary"),
            severity=self.determine_severity(severity),
            status=IssueStatus.Open.value,
            cvss_v3_score=cvss3_score,
            cvss_v3_vector=cve_dat.get("cvss_v3_vector", ""),
            plugin_name=self.mapping.get_value(data_item, "issue_id", "XRay"),
            plugin_id=plugin_id,
            asset_identifier=asset_name,
            cve=cve,
            first_seen=epoch_to_datetime(self.create_epoch),
            last_seen=self.scan_date,
            scan_date=self.scan_date,
            category="Software",
            control_labels=[],
        )

    def _create_findings_from_data_item(self, data_item: dict, asset_name: str) -> Iterator[IntegrationFinding]:
        """Create findings from a single data item

        :param dict data_item: The data item containing vulnerability information
        :param str asset_name: The asset name for the finding
        :yields: IntegrationFinding objects
        """
        cve_data = self.mapping.get_value(data_item, "cves", [])
        if not self._validate_cve_data(cve_data):
            return

        valid_cve_data = self._get_valid_cve_data(cve_data)
        for cve_dat in valid_cve_data:
            yield self._create_finding_from_cve(data_item, asset_name, cve_dat)

    def _process_list_findings(self) -> Iterator[IntegrationFinding]:
        """Process findings from list data

        :yields: IntegrationFinding objects
        """
        for data_item in self.file_data:
            if isinstance(data_item, list):
                continue
            asset_name = self._extract_asset_name(data_item)
            if asset_name:
                yield from self._create_findings_from_data_item(data_item, asset_name)

    def _process_dict_findings(self) -> Iterator[IntegrationFinding]:
        """Process findings from dict data

        :yields: IntegrationFinding objects
        """
        asset_name = self._extract_asset_name(self.file_data)
        if asset_name:
            yield from self._create_findings_from_data_item(self.file_data, asset_name)

    def fetch_findings(self, **_) -> Iterator[IntegrationFinding]:
        """
        Fetch findings from Xray scan data.

        :raises ValidationException: If there is an error fetching/parsing findings
        :yields: Iterator[IntegrationFinding]
        """
        try:
            if isinstance(self.file_data, list):
                yield from self._process_list_findings()
            elif isinstance(self.file_data, dict):
                yield from self._process_dict_findings()
        except Exception as exc:
            error_message = traceback.format_exc()
            logger.error("Error fetching findings: %s", error_message)
            raise ValidationException(f"Error fetching findings: {error_message}") from exc
