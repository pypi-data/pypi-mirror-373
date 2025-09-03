"""
Prisma Scan information
"""

from concurrent.futures import ThreadPoolExecutor
from itertools import groupby
from operator import attrgetter
from typing import Any, List, Optional

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import epoch_to_datetime, get_current_datetime, is_valid_fqdn
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import ImportValidater
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.regscale_models import Asset, IssueSeverity, IssueStatus, SoftwareInventory, Vulnerability

FIX_STATUS = "Fix Status"
VULNERABILITY_ID = "Vulnerability ID"
CVE_ID = "CVE ID"
RISK_FACTORS = "Risk Factors"
PACKAGE_LICENSE = "Package License"
PACKAGE_VERSION = "Package Version"
VULNERABILITY_TAGS = "Vulnerability Tags"
VULNERABILITY_LINK = "Vulnerability Link"
PACKAGE_PATH = "Package Path"
SOURCE_PACKAGE = "Source Package"
CUSTOM_LABELS = "Custom Labels"
IMAGE_ID = "Image ID"
IMAGE_NAME = "Image Name"


class Prisma(FlatFileImporter):
    """
    Prisma Scan information
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        regscale_ssp_id = kwargs.get("object_id")
        self.image_name = "Id"
        self.vuln_title = CVE_ID
        self.cvss3_score = "CVSS"
        self.required_headers = ["Hostname", "Distro", "CVSS", "CVE ID", "Description", "Fix Status"]
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mapping_file, self.disable_mapping
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        logger = create_logger()
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.headers,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            extra_headers_allowed=True,
            ignore_validation=True,
            **kwargs,
        )
        # self.create_software_inventory()

    def create_asset(self, dat: Optional[dict] = None) -> IntegrationAsset:
        """
        Create an asset from a row in the Prisma csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale IntegrationAsset object
        :rtype: IntegrationAsset
        """
        hostname = self.mapping.get_value(dat, "Hostname")
        distro = self.mapping.get_value(dat, "Distro")

        return IntegrationAsset(
            **{
                "name": hostname,
                "ip_address": self.mapping.get_value(dat, "IP Address"),
                "identifier": hostname,
                "other_tracking_number": hostname,
                "status": "Active (On Network)",
                "asset_category": "Hardware",
                "asset_type": "Other",
                "scanning_tool": self.name,
                "fqdn": hostname if is_valid_fqdn(hostname) else None,
                "operating_system": Asset.find_os(distro),
            }
        )

    def create_vuln(self, dat: Optional[dict] = None, **kwargs) -> Optional[IntegrationFinding]:
        """
        Create a IntegrationFinding from a row in the Prisma csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale IntegrationFinding object or None
        :rtype: Optional[IntegrationFinding]
        """
        cvss3_score = self.mapping.get_value(dat, self.cvss3_score)
        hostname: str = self.mapping.get_value(dat, "Hostname")
        cve: str = self.mapping.get_value(dat, CVE_ID)
        description: str = self.mapping.get_value(dat, "Description")
        regscale_finding: Optional[IntegrationFinding] = None
        severity = (
            self.determine_severity(Vulnerability.determine_cvss3_severity_text(float(cvss3_score)))
            if cvss3_score
            else IssueSeverity.NotAssigned
        )
        seen = epoch_to_datetime(self.create_epoch)
        if dat:
            return IntegrationFinding(
                control_labels=[],  # Add an empty list for control_labels
                title=self.mapping.get_value(dat, self.vuln_title),
                description=description,
                cve=cve.upper(),
                severity=severity,
                asset_identifier=hostname,
                plugin_name=self.mapping.get_value(dat, self.vuln_title),
                plugin_id=self.mapping.get_value(dat, VULNERABILITY_ID),
                cvss_v3_score=cvss3_score or 0.0,
                plugin_text=description[:255],
                remediation=self.mapping.get_value(dat, "Solution"),
                category="Hardware",
                status=IssueStatus.Open,
                first_seen=seen,
                scan_date=seen,
                vulnerability_type="Vulnerability Scan",
                baseline=f"{self.name} Host",
                recommendation_for_mitigation=self.mapping.get_value(dat, FIX_STATUS),
            )
        return regscale_finding

    def create_software_inventory(self) -> List[SoftwareInventory]:
        """
        Create and post a list of software inventory for a given asset

        :return: List of software inventory
        :rtype: List[SoftwareInventory]
        """
        scanned_assets = [
            asset for asset in self.data["assets"] if asset.id in {vuln.parentId for vuln in self.data["vulns"]}
        ]
        self.attributes.logger.info(f"Processing inventory for {len(scanned_assets)} scanned assets.")
        software_inventory = []
        for asset in scanned_assets:
            software_inventory.extend(SoftwareInventory.fetch_by_asset(self.attributes.app, asset.id))
        hardware = sorted(
            [asset for asset in scanned_assets if asset.assetCategory == "Hardware"],
            key=attrgetter("name"),
        )
        grouping = {key: list(group) for key, group in groupby(hardware, key=attrgetter("name"))}

        def process_group(key: Any, group: list) -> None:
            """
            Process a group of assets and create a software inventory for each asset

            :param Any key: Key for the group
            :param list group: List of assets
            :rtype: None
            """
            # Do something
            group_rows = [row for row in self.file_data if row["Hostname"] == key]
            for software in group_rows:
                inv = SoftwareInventory(
                    name=software[SOURCE_PACKAGE],
                    version=software[PACKAGE_VERSION],
                    createdById=self.config["userId"],
                    dateCreated=get_current_datetime(),
                    lastUpdatedById=self.config["userId"],
                    isPublic=True,
                )
                inv.parentHardwareAssetId = group[0].id
                if inv not in software_inventory:
                    software_inventory.append(SoftwareInventory.insert(self.attributes.app, inv))

        with ThreadPoolExecutor() as executor:
            for key, group in grouping.items():
                executor.submit(process_group, key, group)

        return software_inventory
