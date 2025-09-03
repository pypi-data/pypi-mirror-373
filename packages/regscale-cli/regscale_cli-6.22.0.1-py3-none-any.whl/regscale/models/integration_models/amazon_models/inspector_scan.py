"""
AWS Inspector Scan information
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import is_valid_fqdn
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import ImportValidater
from regscale.models.integration_models.amazon_models.inspector import InspectorRecord
from regscale.models.integration_models.flat_file_importer import FlatFileImporter
from regscale.models.regscale_models import Asset, AssetStatus, IssueStatus, Vulnerability


class InspectorScan(FlatFileImporter):
    """
    AWS Inspector Scan
    """

    def __init__(self, **kwargs: dict):
        self.name = "amazon"
        self.vuln_title = "Vulnerability Name"
        self.fmt = "%m/%d/%Y"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.image_name = "Image Name"
        self.ffi = "First Found on Image"
        json_headers = [
            "awsAccountId",
            "resources",
            "packageVulnerabilityDetails",
            "title",
            "description",
        ]
        csv_headers = [
            "AWS Account Id",
            "Resource ID",
            "Title",
            "Description",
        ]
        file_type = kwargs.get("file_type")
        if file_type == ".json":
            self.required_headers = json_headers
            key = "findings"
        elif file_type == ".csv":
            self.required_headers = csv_headers
            key = None
        else:
            from regscale.exceptions import ValidationException

            raise ValidationException(f"Unsupported file format: {file_type}, must be .json or .csv.")
        self.mappings_path = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mappings_path, self.disable_mapping, key=key
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        logger = create_logger()
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.headers,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            **kwargs,
        )

    def file_to_list_of_dicts(self) -> Tuple[dict, List[InspectorRecord]]:
        """
        Override the base class method to handle the AWS Inspector CSV or JSON file format

        :raises ValueError: If the file format is not supported
        :return: Tuple of a header and a list of inspector objects
        :rtype: Tuple[dict, List[InspectorRecord]]
        """
        file_path = Path(self.attributes.file_path)
        file_ext = file_path.suffix
        if file_ext == ".csv":
            header, res = InspectorRecord.process_csv(file_path, self.mapping)
        elif file_ext == ".json":
            header, res = InspectorRecord.process_json(file_path, self.mapping)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        return header, res

    def create_asset(self, dat: Optional[InspectorRecord] = None) -> Asset:
        """
        Create an asset from a row in an Inspector Record

        :param Optional[InspectorRecord] dat: Data row from an Inspector Record, defaults to None
        :return: RegScale Asset object
        :rtype: Asset
        """
        hostname = dat.resource_id
        distro = dat.platform
        # Container Image, Virtual Machine (VM), etc.
        asset_type = self.amazon_type_map().get(dat.resource_type, "Other")

        return IntegrationAsset(
            identifier=hostname,
            name=hostname,
            ip_address="0.0.0.0",
            cpu=0,
            ram=0,
            status=AssetStatus.Active.value,
            asset_type=asset_type,
            asset_category="Software",
            operating_system=Asset.find_os(distro),
            fqdn=hostname if is_valid_fqdn(hostname) else None,
        )

    def create_vuln(self, dat: Optional[InspectorRecord] = None, **kwargs) -> Optional[Vulnerability]:
        """
        Create a vulnerability from an Inspector Record

        :param Optional[InspectorRecord] dat: Data row an Inspector Record, defaults to None
        :return: RegScale Vulnerability object or None
        :rtype: Optional[Vulnerability]
        """
        hostname = dat.resource_id
        cve: str = dat.vulnerability_id
        description: str = dat.description
        title = dat.title if dat.title else dat.description
        aws_severity = dat.severity
        severity = self.severity_mapper(aws_severity)
        if dat:
            return IntegrationFinding(
                title=title,
                description=description,
                severity=self.determine_severity(severity),
                status=IssueStatus.Open.value,
                ip_address="0.0.0.0",
                plugin_text=title,
                plugin_name=dat.title,
                plugin_id=self.convert_cve_string_to_int(dat.vulnerability_id),
                asset_identifier=hostname,
                remediation=dat.remediation,
                cve=cve,
                first_seen=dat.first_seen,
                last_seen=dat.last_seen,
                scan_date=self.scan_date,
                category="Software",
                control_labels=[],
            )
        return None

    @staticmethod
    def amazon_type_map() -> dict:
        """
        Map Amazon Inspector resource types to RegScale asset types
        """
        return {
            "AWS_EC2_INSTANCE": "Virtual Machine (VM)",
            "AWS_ECR_CONTAINER_IMAGE": "Container Image",
        }

    @staticmethod
    def severity_mapper(aws_severity):
        """
        Map AWS Inspector severity to RegScale severity
        """

        severity_map = {"CRITICAL": "high", "HIGH": "high", "LOW": "low", "MEDIUM": "medium", "UNTRIAGED": "high"}
        return severity_map.get(aws_severity, "low")

    @staticmethod
    def convert_cve_string_to_int(s: str) -> int:
        """
        Convert a CVE string to an integer

        :param str s: CVE string
        :return: CVE integer
        :rtype: int
        """
        numbers = re.findall(r"\d+", s)
        # merge numbers to string
        return int("".join(numbers))
