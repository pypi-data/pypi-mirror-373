"""
Aqua Scan information
"""

from itertools import groupby
from operator import itemgetter
from typing import List, Optional

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import get_current_datetime, is_valid_fqdn
from regscale.core.utils.date import datetime_str
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models.app_models import ImportValidater
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.regscale_models import AssetStatus, IssueSeverity, IssueStatus
from regscale.models.regscale_models import AssetStatus, IssueSeverity, IssueStatus


class Aqua(FlatFileImporter):
    """Aqua Scan information"""

    def __init__(self, **kwargs):
        from regscale.integrations.integration_override import IntegrationOverride

        self.name = kwargs.get("name")
        self.integration_mapping = IntegrationOverride(Application())
        self.vuln_title = "Vulnerability Name"
        self.fmt = "%m/%d/%Y"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.image_name = "Image Name"
        self.OS = "OS"
        self.description = "Description"
        self.ffi = "First Found on Image"
        self.last_image_scan = "Last Image Scan"
        self.installed_version = "Installed Version"
        self.vendor_cvss_v2_severity = "Vendor CVSS v2 Severity"
        self.vendor_cvss_v3_severity = "Vendor CVSS v3 Severity"
        self.vendor_cvss_v3_score = "Vendor CVSS v3 Score"
        self.vendor_cvss_v2_score = "Vendor CVSS v2 Score"
        self.nvd_cvss_v2_severity = "NVD CVSS v2 Severity"
        self.nvd_cvss_v3_severity = "NVD CVSS v3 Severity"
        self.required_headers = [
            self.image_name,
            self.OS,
            self.vuln_title,
            self.description,
        ]
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mapping_file, self.disable_mapping
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        logger = create_logger()
        self.logger = logger
        super().__init__(
            logger=logger,
            headers=self.headers,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            app=Application(),
            ignore_validation=True,
            **kwargs,
        )

    def create_asset(self, dat: Optional[dict] = None) -> Optional[IntegrationAsset]:
        """
        Create an IntegrationAsset from a row in the Aqua file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :return: RegScale IntegrationAsset object or None
        :rtype: Optional[IntegrationAsset]
        """
        name = self.mapping.get_value(dat, self.image_name)
        if not name:
            return None
        os = self.mapping.get_value(dat, self.OS)
        return IntegrationAsset(
            identifier=name,
            name=name,
            ip_address="0.0.0.0",
            cpu=0,
            ram=0,
            status=AssetStatus.Active.value,
            asset_type="Other",
            asset_category="Hardware",
            scanning_tool=self.name,
            fqdn=name if is_valid_fqdn(name) else None,
            operating_system=os,
            other_tracking_number=name,
            software_inventory=self.generate_software_inventory(name),
        )

    def generate_software_inventory(self, name: str) -> List[dict]:
        """
        Create and post a list of software inventory for a given asset

        :param str name: The name of the asset
        :return: List of software inventory
        :rtype: List[dict]
        """
        inventory: List[dict] = []

        image_group = {
            k: list(g) for k, g in groupby(self.file_data, key=itemgetter(self.mapping.get_header(self.image_name)))
        }

        softwares = image_group[name]
        for software in softwares:
            if "Resource" not in software or self.installed_version not in software:
                continue
            inv = {
                "name": software["Resource"],
                "version": str(software[self.installed_version]),
            }
            if (inv.get("name"), inv.get("version")) not in {
                (soft.get("name"), soft.get("version")) for soft in inventory
            }:
                inventory.append(inv)

        return inventory

    def current_datetime_w_log(self, field: str) -> str:
        """
        Get the current date and time with a log message

        :param str field: The field that is missing the date
        :return: The current date and time
        :rtype: str
        """
        self.logger.info(f"Unable to determine date for the '{field}' field, falling back to current date and time.")
        return self.scan_date

    def determine_first_seen(self, dat: dict) -> str:
        """
        Determine the first seen date and time of the vulnerability

        :param dict dat: Data row from CSV file
        :return: The first seen date and time
        :rtype: str
        """
        first_detected = datetime_str(
            self.mapping.get_value(dat, self.integration_mapping.load("aqua", "dateFirstDetected"))
        )
        ffi = datetime_str(self.mapping.get_value(dat, self.ffi)) or self.current_datetime_w_log(self.ffi)
        if first_detected and first_detected != ffi:
            ffi = first_detected
        return ffi

    def create_vuln(self, dat: Optional[dict] = None, **kwargs: dict) -> Optional[IntegrationFinding]:
        """
        Create a IntegrationFinding from a row in the Aqua csv file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :param dict **kwargs: Additional keyword arguments
        :return: RegScale IntegrationFinding object or None
        :rtype: Optional[IntegrationFinding]
        """

        try:
            hostname = self.mapping.get_value(dat, self.image_name)

            # Custom Integration Mapping fields
            remediation = self.mapping.get_value(dat, self.integration_mapping.load("aqua", "remediation")) or (
                self.mapping.get_value(dat, self.description) or "Upgrade affected package"
            )  # OLDTODO: BMC would like this to use "Solution" column
            description = self.mapping.get_value(dat, self.integration_mapping.load("aqua", "description")) or (
                self.mapping.get_value(dat, self.description)
            )
            title = self.mapping.get_value(dat, self.integration_mapping.load("aqua", "title")) or (
                description[:255] if description else f"Vulnerability on {hostname}"
            )  # OLDTODO: BMC Would like the CVE here

            cvss3_score = self.mapping.get_value(dat, self.vendor_cvss_v3_score) or 0.0
            cvss_v2_score = self.mapping.get_value(dat, self.vendor_cvss_v2_score) or 0.0

            regscale_finding = None
            severity = self.determine_cvss_severity(dat)
            # Create IntegrationFinding if we have valid data and asset match

            if dat:
                return IntegrationFinding(
                    control_labels=[],  # Add an empty list for control_labels
                    title=title,
                    description=description,
                    ip_address="0.0.0.0",
                    cve=self.mapping.get_value(dat, self.vuln_title, "").upper(),
                    severity=severity,
                    asset_identifier=hostname,
                    plugin_name=description,
                    plugin_id=self.mapping.get_value(dat, self.vuln_title),
                    cvss_score=cvss_v2_score or 0.0,
                    cvss_v3_score=cvss3_score or 0.0,
                    cvss_v2_score=cvss_v2_score or 0.0,
                    plugin_text=self.mapping.get_value(dat, self.vuln_title),
                    remediation=remediation,
                    category="Hardware",
                    status=IssueStatus.Open,
                    first_seen=self.determine_first_seen(dat),
                    last_seen=datetime_str(self.mapping.get_value(dat, self.last_image_scan))
                    or self.current_datetime_w_log(self.last_image_scan),
                    vulnerability_type="Vulnerability Scan",
                    baseline=f"{self.name} Host",
                )
            return regscale_finding
        except AttributeError as e:
            self.logger.error(f"Error creating finding: {e}")
            return None

    def determine_cvss_severity(self, dat: dict) -> str:
        """
        Determine the CVSS severity of the vulnerability

        :param dict dat: Data row from CSV file
        :return: A severity derived from the CVSS scores
        :rtype: str
        """
        precedence_order = [
            self.nvd_cvss_v3_severity,
            self.nvd_cvss_v2_severity,
            self.vendor_cvss_v3_severity,
            # This field may or may not be available in the file (Coalfire has it, BMC does not.)
            (self.vendor_cvss_v2_severity if self.mapping.get_value(dat, self.vendor_cvss_v2_severity) else None),
        ]
        severity = "info"
        for key in precedence_order:
            if key and self.mapping.get_value(dat, key):
                severity = self.mapping.get_value(dat, key).lower()
                break

        return self.determine_severity(severity)

    def validate(self, ix: Optional[int], dat: dict) -> bool:
        """
        Validate the row of data, and populate with something if missing

        :param Optional[int] ix: index
        :param dict dat: Data row from CSV file
        :return: True if the row is valid or has been updated with default value
        :rtype: bool
        """
        required_keys = [self.description]
        val = True
        for key in required_keys:
            if not dat.get(key):
                default_val = f"No {key} available."
                row_skip = (
                    f"Populating {key} for row #{ix + 1} with {default_val}"
                    if isinstance(ix, int)
                    else f"Populating {key} with {default_val}"
                )
                self.attributes.logger.warning(f"Missing value for required field: {key}, {row_skip}")
                dat[key] = default_val
        return val
