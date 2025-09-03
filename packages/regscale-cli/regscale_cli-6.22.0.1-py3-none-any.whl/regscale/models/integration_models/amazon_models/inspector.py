"""
AWS Inspector Model
"""

import csv
import json
from typing import List, Optional, TYPE_CHECKING, Tuple, Union

if TYPE_CHECKING:
    from regscale.models import Mapping

from pathlib import Path
from pydantic import BaseModel

from regscale.core.app.utils.app_utils import error_and_exit


class InspectorRecord(BaseModel):
    """
    AWS Inspector Record
    """

    aws_account_id: str
    severity: Optional[str] = None
    fix_available: Optional[str] = None
    finding_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    finding_arn: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    last_updated: Optional[str] = None
    resource_id: Optional[str] = None
    container_image_tags: Optional[str] = None
    region: Optional[str] = None
    platform: Optional[str] = None
    resource_tags: Optional[str] = None
    affected_packages: Optional[str] = None
    package_installed_version: Optional[str] = None
    fixed_in_version: Optional[str] = None
    package_remediation: Optional[str] = None
    file_path: Optional[str] = None
    network_paths: Optional[str] = None
    age_days: Optional[str] = None
    remediation: Optional[str] = None
    inspector_score: Optional[str] = None
    inspector_score_vector: Optional[str] = None
    status: Optional[str] = None
    vulnerability_id: Optional[str] = None
    vendor: Optional[str] = None
    vendor_severity: Optional[str] = None
    vendor_advisory: Optional[str] = None
    vendor_advisory_published: Optional[str] = None
    nvd_cvss3_score: Optional[str] = None
    nvd_cvss3_vector: Optional[str] = None
    nvd_cvss2_score: Optional[str] = None
    nvd_cvss2_vector: Optional[str] = None
    vendor_cvss3_score: Optional[str] = None
    vendor_cvss3_vector: Optional[str] = None
    vendor_cvss2_score: Optional[str] = None
    vendor_cvss2_vector: Optional[str] = None
    resource_type: Optional[str] = None
    ami: Optional[str] = None
    resource_public_ipv4: Optional[str] = None
    resource_private_ipv4: Optional[str] = None
    resource_ipv6: Optional[str] = None
    resource_vpc: Optional[str] = None
    port_range: Optional[str] = None
    epss_score: Optional[str] = None
    exploit_available: Optional[str] = None
    last_exploited_at: Optional[str] = None
    lambda_layers: Optional[str] = None
    lambda_package_type: Optional[str] = None
    lambda_last_updated_at: Optional[str] = None
    reference_urls: Optional[str] = None
    detector_name: Optional[str] = None
    package_manager: Optional[str] = None

    @classmethod
    def process_csv(cls, file_path: Union[str, Path], mapping: "Mapping") -> Tuple[dict, List["InspectorRecord"]]:
        """
        Process CSV file

        :param Union[str, Path] file_path: File path
        :param Mapping mapping: Mapping object for different headers
        :return: A header dict and a list of InspectorRecord objects
        :rtype: Tuple[dict, List["InspectorRecord"]]
        """

        with open(file=file_path, mode="r", encoding="utf-8") as f:
            res = []
            reader = csv.DictReader(f)
            header = reader.fieldnames
            header_mapping = {name: name for name in header}
            for row in reader:
                new_row = {header_mapping[key]: value for key, value in row.items()}
                res.append(cls.create_inspector_record_from_csv_data(new_row, mapping))
        return header, res

    @classmethod
    def process_json(cls, file_path: Union[str, Path], mapping: "Mapping") -> Tuple[dict, List["InspectorRecord"]]:
        """
        Process JSON file

        :param Union[str, Path] file_path: File path
        :param Mapping mapping: Mapping object for different headers
        :rtype: Tuple[dict, List["InspectorRecord"]]
        :return: An empty dict and a list of InspectorRecord objects
        """
        with open(file=file_path, mode="r", encoding="utf-8") as file_object:
            dat = json.load(file_object)
        if not dat.get("findings"):
            error_and_exit("No findings in JSON file, check the file format and try again.")
        return {}, [cls.create_inspector_record_from_json_data(finding, mapping) for finding in dat.get("findings", [])]

    @classmethod
    def create_inspector_record_from_json_data(cls, finding: dict, mapping: "Mapping") -> "InspectorRecord":
        """
        Create an InspectorRecord from a csv row of data

        :param dict finding: The finding data
        :param Mapping mapping: Mapping object for different headers
        :return: An InspectorRecord object
        :rtype: InspectorRecord
        """
        resource = cls.get_resource(finding, mapping)
        details = resource.get("details", {})
        vulnerabilities = mapping.get_value(finding, "packageVulnerabilityDetails", {})
        platform_key = list(details.keys())[0] if details.keys() else None

        return InspectorRecord(
            aws_account_id=mapping.get_value(finding, "awsAccountId", ""),
            description=mapping.get_value(finding, "description"),
            exploit_available=mapping.get_value(finding, "exploitAvailable"),
            finding_arn=mapping.get_value(finding, "findingArn"),
            first_seen=mapping.get_value(finding, "firstObservedAt"),
            fix_available=mapping.get_value(finding, "fixAvailable"),
            last_seen=mapping.get_value(finding, "lastObservedAt"),
            remediation=mapping.get_value(finding, "remediation", {}).get("recommendation", {}).get("text", ""),
            severity=mapping.get_value(finding, "Severity"),
            status=mapping.get_value(finding, "status"),
            title=mapping.get_value(finding, "title"),
            resource_type=resource.get("type"),
            resource_id=resource.get("id"),
            region=resource.get("region"),
            last_updated=mapping.get_value(finding, "updatedAt"),
            platform=resource.get("details", {}).get(platform_key, {}).get("platform", ""),
            resource_tags=" ,".join(resource.get("details", {}).get(platform_key, {}).get("imageTags", "")),
            affected_packages=cls.get_vulnerable_package_info(vulnerabilities, "name"),
            package_installed_version=cls.get_vulnerable_package_info(vulnerabilities, "version"),
            fixed_in_version=cls.get_vulnerable_package_info(vulnerabilities, "fixedInVersion"),
            package_remediation=cls.get_vulnerable_package_info(vulnerabilities, "remediation"),
            vulnerability_id=vulnerabilities.get("vulnerabilityId") if vulnerabilities else None,
            vendor=vulnerabilities.get("source") if vulnerabilities else None,
            vendor_severity=mapping.get_value(finding, "severity"),
            vendor_advisory=vulnerabilities.get("sourceUrl") if vulnerabilities else None,
            vendor_advisory_published=vulnerabilities.get("vendorCreatedAt") if vulnerabilities else None,
            package_manager=cls.get_vulnerable_package_info(
                mapping.get_value(finding, "packageVulnerabilityDetails", {}), "packageManager"
            ),
            file_path=cls.get_vulnerable_package_info(
                mapping.get_value(finding, "packageVulnerabilityDetails", {}), "filePath"
            ),
            reference_urls=mapping.get_value(finding, "packageVulnerabilityDetails", {}).get("sourceUrl"),
        )

    @classmethod
    def create_inspector_record_from_csv_data(cls, finding: dict, mapping: "Mapping") -> "InspectorRecord":
        """
        Create an InspectorRecord from a finding

        :param dict finding: The finding data
        :param Mapping mapping: Mapping object for different headers
        :return: An InspectorRecord object
        :rtype: InspectorRecord
        """
        return InspectorRecord(
            aws_account_id=mapping.get_value(finding, "AWS Account Id"),
            severity=mapping.get_value(finding, "Severity"),
            fix_available=mapping.get_value(finding, "Fix Available"),
            finding_type=mapping.get_value(finding, "Finding Type"),
            title=mapping.get_value(finding, "Title"),
            description=mapping.get_value(finding, "Description"),
            finding_arn=mapping.get_value(finding, "Finding ARN"),
            first_seen=mapping.get_value(finding, "First Seen"),
            last_seen=mapping.get_value(finding, "Last Seen"),
            last_updated=mapping.get_value(finding, "Last Updated"),
            resource_id=mapping.get_value(finding, "Resource ID"),
            container_image_tags=mapping.get_value(finding, "Container Image Tags"),
            region=mapping.get_value(finding, "Region"),
            platform=mapping.get_value(finding, "Platform"),
            resource_tags=mapping.get_value(finding, "Resource Tags"),
            affected_packages=mapping.get_value(finding, "Affected Packages"),
            package_installed_version=mapping.get_value(finding, "Package Installed Version"),
            fixed_in_version=mapping.get_value(finding, "Fixed in Version"),
            package_remediation=mapping.get_value(finding, "Package Remediation"),
            file_path=mapping.get_value(finding, "File Path"),
            network_paths=mapping.get_value(finding, "Network Paths"),
            age_days=mapping.get_value(finding, "Age (Days)"),
            remediation=mapping.get_value(finding, "Remediation"),
            inspector_score=mapping.get_value(finding, "Inspector Score"),
            inspector_score_vector=mapping.get_value(finding, "Inspector Score Vector"),
            status=mapping.get_value(finding, "Status"),
            vulnerability_id=mapping.get_value(finding, "Vulnerability Id"),
            vendor=mapping.get_value(finding, "Vendor"),
            vendor_severity=mapping.get_value(finding, "Vendor Severity"),
            vendor_advisory=mapping.get_value(finding, "Vendor Advisory"),
            vendor_advisory_published=mapping.get_value(finding, "Vendor Advisory Published"),
            nvd_cvss3_score=mapping.get_value(finding, "NVD CVSS3 Score"),
            nvd_cvss3_vector=mapping.get_value(finding, "NVD CVSS3 Vector"),
            nvd_cvss2_score=mapping.get_value(finding, "NVD CVSS2 Score"),
            nvd_cvss2_vector=mapping.get_value(finding, "NVD CVSS2 Vector"),
            vendor_cvss3_score=mapping.get_value(finding, "Vendor CVSS3 Score"),
            vendor_cvss3_vector=mapping.get_value(finding, "Vendor CVSS3 Vector"),
            vendor_cvss2_score=mapping.get_value(finding, "Vendor CVSS2 Score"),
            vendor_cvss2_vector=mapping.get_value(finding, "Vendor CVSS2 Vector"),
            resource_type=mapping.get_value(finding, "Resource Type"),
            ami=mapping.get_value(finding, "Ami"),
            resource_public_ipv4=mapping.get_value(finding, "Resource Public Ipv4"),
            resource_private_ipv4=mapping.get_value(finding, "Resource Private Ipv4"),
            resource_ipv6=mapping.get_value(finding, "Resource Ipv6"),
            resource_vpc=mapping.get_value(finding, "Resource Vpc"),
            port_range=mapping.get_value(finding, "Port Range"),
            epss_score=mapping.get_value(finding, "Epss Score"),
            exploit_available=mapping.get_value(finding, "Exploit Available"),
            last_exploited_at=mapping.get_value(finding, "Last Exploited At"),
            lambda_layers=mapping.get_value(finding, "Lambda Layers"),
            lambda_package_type=mapping.get_value(finding, "Lambda Package Type"),
            lambda_last_updated_at=mapping.get_value(finding, "Lambda Last Updated At"),
            reference_urls=mapping.get_value(finding, "Reference Urls"),
            detector_name=mapping.get_value(finding, "Detector Name"),
            package_manager=mapping.get_value(finding, "Package Manager"),
        )

    @staticmethod
    def get_resource(finding: dict, mapping: "Mapping") -> dict:
        """
        Get the resource from a finding

        :param dict finding: The finding data
        :param Mapping mapping: Mapping object for different headers
        :return: The resource data
        :rtype: dict
        """
        resources = mapping.get_value(finding, "resources", [])
        resource = resources.pop() if resources else {}
        return resource

    @staticmethod
    def get_vulnerable_package_info(vulnerabilities: dict, key: str) -> Optional[str]:
        """
        Get information from a vulnerable package

        :param dict vulnerabilities: The vulnerabilities data
        :param str key: The key of the information to get
        :return: The information or None if not found
        :rtype: Optional[str]
        """
        vulnerable_packages = vulnerabilities.get("vulnerablePackages", [])
        return vulnerable_packages[0].get(key) if vulnerabilities and vulnerable_packages else None
