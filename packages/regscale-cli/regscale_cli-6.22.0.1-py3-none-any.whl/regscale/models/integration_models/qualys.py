"""
Qualys Scan information
"""

import ast
import logging

# pylint: disable=C0415
import re
from calendar import firstweekday
from datetime import datetime
from typing import Any, Iterator, List, Optional, TextIO, TypeVar, Union

from openpyxl.reader.excel import load_workbook
from pandas import Timestamp

from regscale.core.app import create_logger
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.core.app.utils.parser_utils import safe_float, safe_int
from regscale.core.utils.date import date_str, datetime_str
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import (
    Asset,
    AssetCategory,
    AssetStatus,
    AssetType,
    ImportValidater,
    IssueSeverity,
    IssueStatus,
    SecurityPlan,
    Vulnerability,
    VulnerabilitySeverity,
    VulnerabilityStatus,
)
from regscale.models.integration_models.flat_file_importer import FlatFileImporter

logger = logging.getLogger(__name__)

T = TypeVar("T")
QG_HOST_ID = "QG Host ID"
CVE_ID = "CVE ID"
SEVERITY = "Severity"
EXPLOITABILITY = "Exploitability"
SOLUTION = "Solution"
DNS = "DNS"
IP = "IP"
OS = "OS"
NETBIOS = "NetBIOS"
FQDN = "FQDN"
IMAGE_ID_FIELD = "IMAGE ID"
CVE_ID_FIELD = "CVE ID"

SEVERITY_MAP = {
    "critical": IssueSeverity.Critical,
    "high": IssueSeverity.High,
    "medium": IssueSeverity.Moderate,
    "moderate": IssueSeverity.Moderate,
    "low": IssueSeverity.Low,
    "informational": IssueSeverity.NotAssigned,
    "none": IssueSeverity.NotAssigned,
    "info": IssueSeverity.NotAssigned,
    "unknown": IssueSeverity.NotAssigned,
}


class Qualys(FlatFileImporter):
    """Qualys Scan information"""

    title = "Qualys Scanner Export Integration"
    asset_identifier_field = "name"

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.vuln_title = "Title"
        self.fmt = "%Y-%m-%d"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.required_headers = [
            SEVERITY,
            self.vuln_title,
            CVE_ID,
            SOLUTION,
            DNS,
            IP,
            QG_HOST_ID,
            OS,
            FQDN,
        ]
        logger = create_logger()
        skip_rows = kwargs.pop("skip_rows")
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            self.required_headers, kwargs.get("file_path"), self.mapping_file, self.disable_mapping, skip_rows=skip_rows
        )
        self.headers = self.validater.parsed_headers
        self.mapping = self.validater.mapping
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.headers,
            header_line_number=skip_rows,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            **kwargs,
        )
        # header is line# 11
        # start self.file_data from line #12

    def create_asset(self, dat: Optional[dict] = None) -> Optional[IntegrationAsset]:
        """
        Create an integration asset from a row in the Qualys file

        :param Optional[dict] dat: Data row from CSV file
        :return: RegScale IntegrationAsset object or None
        :rtype: Optional[IntegrationAsset]
        """
        qid = str(self.mapping.get_value(dat, QG_HOST_ID))
        return IntegrationAsset(
            name=self.mapping.get_value(dat, DNS),
            ip_address=self.mapping.get_value(dat, IP),
            status=AssetStatus.Active.value,
            cpu=0,
            ram=0,
            asset_category="Hardware",
            identifier=qid,  # UUID from Qualys Host ID
            other_tracking_number=qid,
            scanning_tool="Qualys",
            asset_owner_id=self.attributes.app.config["userId"],
            asset_type="Other",
            fqdn=self.mapping.get_value(dat, FQDN),
            operating_system=Asset.find_os(self.mapping.get_value(dat, OS)),
            os_version=self.mapping.get_value(dat, OS),
        )

    def _convert_datetime_to_str(self, input_date: Union[Timestamp, datetime]) -> str:
        """
        Convert a datetime or Timestamp object to a string in the specified format.

        :param Union[Timestamp, datetime] input_date: The date to convert.
        :return: The date as a string in the format '%Y-%m-%d %H:%M:%S'.
        :rtype: str
        """
        if isinstance(input_date, Timestamp):
            input_date = input_date.to_pydatetime()
        elif isinstance(input_date, str):
            return input_date
        return input_date.strftime(self.dt_format)

    def create_vuln(self, dat: Optional[dict] = None, **kwargs) -> Optional[IntegrationFinding]:
        """
        Create a finding from a row in the Qualys file

        :param Optional[dict] dat: Data row from CSV file, defaults to None
        :rtype: IntegrationFinding
        """
        from regscale.integrations.commercial.qualys import map_qualys_severity_to_regscale

        finding: Optional[IntegrationFinding] = None
        qid = str(self.mapping.get_value(dat, QG_HOST_ID))
        cve: str = self.mapping.get_value(dat, CVE_ID)
        description: str = self.mapping.get_value(dat, "Threat")
        title = self.mapping.get_value(dat, self.vuln_title)
        severity = self.mapping.get_value(dat, SEVERITY)
        regscale_severity = map_qualys_severity_to_regscale(int(severity))[1]
        if dat:
            finding = IntegrationFinding(
                control_labels=[],  # Add an empty list for control_labels
                title=title,
                description=description,
                ip_address="0.0.0.0",
                cve=cve,
                severity=regscale_severity,
                asset_identifier=qid,
                plugin_name=description,
                plugin_id=str(self.mapping.get_value(dat, "QID")),
                cvss_v3_score=self.extract_float(self.mapping.get_value(dat, "CVSS3.1 Base", 0.0)),
                plugin_text=title,
                category="Hardware",
                status=IssueStatus.Open,
                first_seen=self._convert_datetime_to_str(self.mapping.get_value(dat, "First Detected")),
                last_seen=self._convert_datetime_to_str(self.mapping.get_value(dat, "Last Detected")),
                vulnerability_type="Vulnerability Scan",
                baseline=f"{self.name} Host",
            )
        return finding

    @staticmethod
    def extract_float(s: Union[str, float, int]) -> Optional[float]:
        """
        Extract a float from a string

        :param str s: String to extract float from
        :return: Float extracted from string or None
        :rtype: Any
        """
        if isinstance(s, (float, int)):
            return float(s)
        if matches := re.findall(r"[-+]?[0-9]*\.?[0-9]+", s):
            return float(matches[0])
        else:
            return None


class QualysContainerScansImporter(FlatFileImporter):  # (ScannerIntegration):
    """
    Import Qualys Container Scans data
    """

    plan_id = 0
    # asset_identifier_field: str = "otherTrackingNumber"
    threat_field = "THREAT"
    severity_field = "SEVERITY"
    title_field = "TITLE"
    asset_notes_field = "IMAGE LABEL"
    cve_v3_base = "CVSS3 BASE"
    cve_base = "CVSS BASE"
    mitigation_field = "SOLUTION"
    external_id_field = "QID"
    first_seen_field = "CREATED ON"
    last_seen_field = "UPDATED"
    container_id = "IMAGE UUID"
    records = []
    title = "Qualys Container Scanner Export Integration"  # Add explicit title for source report identification

    def __init__(self, **kwargs: dict):
        self.asset_identifier_field = "otherTrackingNumber"
        self.name = kwargs.get("name")
        self.fmt = "%Y-%m-%d"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.plan_id = kwargs.get("parent_id")
        self.required_headers = [
            self.severity_field,
            self.title_field,
            self.asset_notes_field,
            self.threat_field,
            CVE_ID_FIELD,
            self.mitigation_field,
            self.cve_v3_base,
            self.cve_base,
            self.external_id_field,
            self.first_seen_field,
            self.last_seen_field,
            self.container_id,
        ]
        self.file_path: str = kwargs.get("file_path")
        skip_rows = kwargs.pop("skip_rows")
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            required_headers=self.required_headers,
            file_path=self.file_path,
            mapping_file_path=self.mapping_file,
            disable_mapping=self.disable_mapping,
            skip_rows=skip_rows,
        )
        self.headers = self.validater.parsed_headers
        self.header = self.headers
        self.mapping = self.validater.mapping
        # super().__init__(plan_id=self.plan_id)
        # self.import_data()
        kwargs["asset_identifier_field"] = "otherTrackingNumber"
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.required_headers,
            header_line_number=skip_rows,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            **kwargs,
        )

    def create_asset(self, row: Optional[dict] = None, **kwargs) -> Optional[IntegrationAsset]:
        """
        Fetch assets from the Qualys CSV file

        :return: IntegrationAsset object
        :rtype: Optional[IntegrationAsset]
        """
        bad_ids = ["", "0", "None", "Unknown"]
        if self.mapping.get_value(row, self.container_id) in bad_ids:
            return None
        max_length = 450  # max length of asset name
        container_id = self.mapping.get_value(row, self.container_id)
        asset = IntegrationAsset(
            name=self.mapping.get_value(row, self.asset_notes_field)[:max_length] or "Unknown",
            notes=self.mapping.get_value(row, self.asset_notes_field),
            identifier=container_id,
            other_tracking_number=container_id,
            asset_type=AssetType.VM.value,
            asset_category=AssetCategory.Software.value,
            status=AssetStatus.Active,
        )
        return asset

    def handle_integration_date(self, input_date_str: str) -> str:
        """
        Handle the integration date to ingest to date and back to string to get into the correct format if needed.

        :param str date_str: Date string
        :return: Date string
        :rtype: str
        """
        date_obj_value = datetime.strptime(
            input_date_str,
            "%Y-%m-%d %H:%M:%S %z %Z",
        )
        return date_str(date_obj_value, self.dt_format)

    def create_vuln(self, row: Optional[dict] = None, **kwargs) -> Iterator[IntegrationFinding]:
        """
        Fetch vulnerabilities from the Qualys CSV file

        :return: Iterator of IntegrationFinding objects
        :rtype: Iterator[IntegrationFinding]
        """
        findings: List[IntegrationFinding] = []
        title = self.mapping.get_value(row, self.title_field)
        description = self.mapping.get_value(row, self.threat_field)
        qid = str(self.mapping.get_value(row, self.container_id))
        if self.mapping.get_value(row, CVE_ID_FIELD) and isinstance(self.mapping.get_value(row, CVE_ID_FIELD), str):
            for cve_id in self.mapping.get_value(row, CVE_ID_FIELD, "").split(","):
                finding = IntegrationFinding(
                    control_labels=[],  # Add an empty list for control_labels
                    title=self.mapping.get_value(row, self.title_field),
                    description=self.mapping.get_value(row, self.threat_field),
                    cve=cve_id,
                    severity=severity_to_regscale(self.mapping.get_value(row, self.severity_field)),
                    asset_identifier=qid,
                    plugin_name=description,
                    plugin_id=str(self.mapping.get_value(dat, "QID")),
                    cvss_v3_score=safe_float(self.mapping.get_value(row, self.cve_v3_base, 0.0)),
                    vpr_score=safe_float(self.mapping.get_value(row, self.cve_base, 0.0)),
                    plugin_text=title,
                    category="Hardware",
                    status=IssueStatus.Open,
                    first_seen=self.handle_integration_date(
                        self.mapping.get_value(row, self.first_seen_field, get_current_datetime())
                    ),
                    last_seen=self.handle_integration_date(
                        self.mapping.get_value(row, self.last_seen_field, get_current_datetime())
                    ),
                    vulnerability_type="Vulnerability Scan",
                    baseline=f"{self.name} Host",
                )
                findings.append(finding)
        yield from findings


class QualysWasScansImporter(FlatFileImporter):
    """
    Import Qualys Container Scans data
    """

    plan_id = 0
    threat_field = "THREAT"
    severity_field = "SEVERITY"
    title_field = "Title"
    asset_notes_field = "Url"
    cve_v3_base = "CVSS V3 Base"
    # cve_base = "CVSS BASE"
    # mitigation_field = "SOLUTION"
    external_id_field = "ID"
    first_seen_field = "Detection Date"
    last_seen_field = "Detection Date"
    container_id = "ID"
    row_key = "VULNERABILITY"
    records = []
    title = "Qualys WAS Scanner Export Integration"  # Add explicit title for source report identification

    def __init__(self, **kwargs: dict):
        self.asset_identifier_field = "otherTrackingNumber"
        self.name = kwargs.get("name")
        self.fmt = "%Y-%m-%d"
        self.dt_format = "%Y-%m-%d %H:%M:%S"
        self.plan_id = kwargs.get("parent_id")
        self.required_headers = [
            "VULNERABILITY",
            "ID",
            "Detection ID",
            "QID",
            "Url",
            "Param/Cookie",
            "Function",
            "Form Entry Point",
            "Access Path",
            "Authentication",
            "Ajax Request",
            "Ajax Request ID",
            "Ignored",
            "Ignore Reason",
            "Ignore Date",
            "Ignore User",
            "Ignore Comments",
            "Detection Date",
            "Payload #1",
            "Request Method #1",
            "Request URL #1",
            "Request Headers #1",
            "Response #1",
            "Evidence #1",
            "Unique ID",
            "Flags",
            "Protocol",
            "Virtual Host",
            "IP",
            "Port",
            "Result",
            "Info#1",
            "CVSS V3 Base",
            "CVSS V3 Temporal",
            "CVSS V3 Attack Vector",
            "Request Body #1",
            "Potential",
        ]
        self.file_path: str = kwargs.get("file_path")
        skip_rows = kwargs.pop("skip_rows")
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            required_headers=self.required_headers,
            file_path=self.file_path,
            mapping_file_path=self.mapping_file,
            disable_mapping=self.disable_mapping,
            skip_rows=skip_rows,
        )
        self.headers = self.validater.parsed_headers
        self.header = self.headers
        self.mapping = self.validater.mapping
        # super().__init__(plan_id=self.plan_id)
        # self.import_data()
        kwargs["asset_identifier_field"] = "otherTrackingNumber"
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.required_headers,
            header_line_number=skip_rows,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            **kwargs,
        )

    def convert_xlsx_to_dict(self, file: TextIO, start_line_number: int = 0) -> tuple:
        """
        Converts an xlsx file to a list of dictionaries, handling multiple sections.

        :param TextIO file: The xlsx file to convert
        :param int start_line_number: The line number to start reading from
        :return: Tuple of merged data and headers
        :rtype: tuple
        """
        # Load the workbook and select the first sheet
        workbook = load_workbook(filename=file.name)
        sheet = workbook.active

        # Get all data from the sheet
        data = list(sheet.values)

        # Identify the start of the second section (QID header row)
        second_section_start = next((i for i, row in enumerate(data) if row and row[0] == "QID"), None)
        second_section_end = next(
            (
                i
                for i, row in enumerate(data[second_section_start + 1 :], start=second_section_start + 1)
                if row and row[0] != "QID"
            ),
            None,
        )
        first_section_end = next(
            (
                i
                for i, row in enumerate(data[start_line_number + 1 :], start=start_line_number + 1)
                if row and row[0] != "VULNERABILITY"
            ),
            None,
        )

        # Extract the first section
        first_section_header = list(data[start_line_number])
        first_section_data = data[start_line_number + 1 : first_section_end]
        first_section_dict = [dict(zip(first_section_header, row)) for row in first_section_data]

        # Extract the second section
        second_section_header = list(data[second_section_start])
        second_section_data = data[second_section_start + 1 : second_section_end]
        second_section_dict = [dict(zip(second_section_header, row)) for row in second_section_data]

        # Convert second section into a lookup dictionary based on QID
        second_section_lookup = {item.get("Id"): item for item in second_section_dict}

        # Keys to extract from the second section
        keys_to_merge = ["Title", "Severity Level", "CVSS Base", "CWE", "Solution"]

        # Merge the two sections by adding specific keys from the second section
        merged_data = []
        for item in first_section_dict:
            qid = item.get("QID")
            if qid in second_section_lookup:
                for key in keys_to_merge:
                    item[key] = second_section_lookup[qid].get(key)
            merged_data.append(item)

        # Convert any string lists to actual lists
        for dat in merged_data:
            for key, val in dat.items():
                if isinstance(val, str) and val.startswith("["):
                    try:
                        dat[key] = ast.literal_eval(val)
                    except SyntaxError as rex:
                        self.attributes.app.logger.debug("SyntaxError: %s", rex)

        # Return merged data and headers
        return merged_data, first_section_header + keys_to_merge

    def create_asset(self, row: Optional[dict] = None, **kwargs) -> Optional[Asset]:
        """
        Fetch assets from the Qualys CSV file

        :return: Iterator of IntegrationAsset objects
        :rtype: Iterator[IntegrationAsset]
        """
        bad_ids = ["", "0", "None", "Unknown"]
        if self.mapping.get_value(row, self.container_id) in bad_ids:
            return None
        max_length = 450  # max length of asset name
        asset = Asset(
            name=self.mapping.get_value(row, self.asset_notes_field)[:max_length] or "Unknown",
            notes=self.mapping.get_value(row, self.asset_notes_field),
            otherTrackingNumber=self.mapping.get_value(row, self.container_id),
            # identifier=self.mapping.get_value(row, IMAGE_ID_FIELD),
            assetType=AssetType.Other.value,
            assetCategory=AssetCategory.Software.value,
            parentId=safe_int(self.plan_id),
            parentModule=SecurityPlan.get_module_slug(),
            status=AssetStatus.Active,
        )
        return asset

    def handle_integration_date(self, input_date_str: str) -> str:
        """
        Handle the integration date to ingest to date and back to string to get into the correct format if needed.

        :param str input_date_str: Date string
        :return: Date string
        :rtype: str
        """
        if not input_date_str:
            return get_current_datetime()
        try:
            date_obj_value = datetime.strptime(
                input_date_str,
                "%d %b %Y %I:%M%p %Z%z",
            )
        except ValueError:
            return get_current_datetime()
        return date_str(date_obj_value, self.dt_format)

    def create_vuln(self, row: Optional[dict] = None, **kwargs) -> Optional[Vulnerability]:
        """
        Fetch vulnerabilities from the Qualys CSV file

        :return: Iterator of IntegrationFinding objects
        :rtype: Vulnerability
        """
        # additional_fields = ["Title", "Severity Level", "CVSS Base", "CWE", "Solution"]
        asset_identifier = self.mapping.get_value(row, self.container_id)

        finding = Vulnerability(
            title=row.get("Title", self.mapping.get_value(row, "Url")),
            description=row.get("Solution"),
            cve=row.get("CWE"),
            severity=severity_to_regscale(row.get("Severity Level", "1")),
            status=VulnerabilityStatus.Open,
            cvsSv3BaseScore=safe_float(self.mapping.get_value(row, self.cve_v3_base, 0.0)),
            vprScore=safe_float(row.get("CVSS Base", 0.0)),
            firstSeen=self.handle_integration_date(
                self.mapping.get_value(row, self.first_seen_field, get_current_datetime())
            ),
            lastSeen=self.handle_integration_date(
                self.mapping.get_value(row, self.last_seen_field, get_current_datetime())
            ),
            plugInName=row.get("CWE"),
            dns=asset_identifier,  # Use consistent asset identifier
            assetIdentifier=asset_identifier,  # Add explicit asset identifier
        )
        return finding


class QualysPolicyScansImporter(FlatFileImporter):
    """
    Import Qualys Policy Scans data
    """

    plan_id = 0
    records = []
    title = "Qualys Policy Scanner Export Integration"  # Add explicit title for source report identification

    def __init__(self, **kwargs: dict):
        self.asset_identifier_field = "qualysId"
        self.name = kwargs.get("name")
        self.fmt = "%Y-%m-%d"
        self.dt_format = "%m/%d/%Y at %H:%M:%S (%Z%z)"
        self.plan_id = kwargs.get("parent_id")
        self.required_headers = [
            "Host IP",
            "DNS Hostname",
            "NetBIOS Hostname",
            "Tracking Method",
            "Operating System",
            "NETWORK",
            "Last Scan Date",
            "Evaluation Date",
            "Control ID",
            "Technology",
            "Control",
            "Criticality Label",
            "Criticality Value",
            "Instance",
            "Rationale",
            "Status",
            "Remediation",
            "Deprecated",
            "Evidence",
            "Exception Assignee",
            "Exception Status",
            "Exception End Date",
            "Exception Creator",
            "Exception Created Date",
            "Exception Modifier",
            "Exception Modified Date",
            "Exception Comments History",
            "Cause of Failure",
            "Qualys Host ID",
            "Previous Status",
        ]
        self.file_path: str = kwargs.get("file_path")
        skip_rows = kwargs.pop("skip_rows")
        self.mapping_file = kwargs.get("mappings_path")
        self.disable_mapping = kwargs.get("disable_mapping")
        self.validater = ImportValidater(
            required_headers=self.required_headers,
            file_path=self.file_path,
            mapping_file_path=self.mapping_file,
            disable_mapping=self.disable_mapping,
            skip_rows=skip_rows,
        )
        self.headers = self.validater.parsed_headers
        self.header = self.headers
        self.mapping = self.validater.mapping
        # super().__init__(plan_id=self.plan_id)
        # self.import_data()
        kwargs["asset_identifier_field"] = self.asset_identifier_field
        super().__init__(
            logger=logger,
            app=Application(),
            headers=self.required_headers,
            header_line_number=skip_rows,
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            **kwargs,
        )

    def create_asset(self, row: Optional[dict] = None, **kwargs) -> Optional[Asset]:
        """
        Fetch assets from the Qualys CSV file

        :return: Iterator of IntegrationAsset objects
        :rtype: Iterator[IntegrationAsset]
        """
        max_length = 450  # max length of asset name
        asset = Asset(
            name=row.get("Control", "Uknown")[:max_length],
            # notes=self.mapping.get_value(row, self.asset_notes_field),
            ipAddress=self.mapping.get_value(row, "Host IP"),
            operatingSystem=self.mapping.get_value(row, "Operating System"),
            qualysId=self.mapping.get_value(row, "Control ID"),
            otherTrackingNumber=self.mapping.get_value(row, "Control ID"),
            # identifier=self.mapping.get_value(row, IMAGE_ID_FIELD),
            assetType=AssetType.Other.value,
            assetCategory=AssetCategory.Software.value,
            parentId=safe_int(self.plan_id),
            parentModule=SecurityPlan.get_module_slug(),
            status=AssetStatus.Active,
        )
        return asset

    def handle_integration_date(self, input_date_str: Optional[str]) -> str:
        """
        Handle the integration date to ingest to date and back to string to get into the correct format if needed.

        :param str input_date_str: Date string
        :return: Date string
        :rtype: str
        """
        if not input_date_str:
            return get_current_datetime()
        date_obj_value = datetime.strptime(
            input_date_str,
            self.dt_format,
        )
        return datetime_str(date_obj_value)

    def create_vuln(self, row: Optional[dict] = None, **kwargs) -> Optional[Vulnerability]:
        """
        Fetch vulnerabilities from the Qualys CSV file

        :return: Iterator of IntegrationFinding objects
        :rtype: Vulnerability
        """
        finding = Vulnerability(
            title=self.mapping.get_value(row, "Control"),
            description=self.mapping.get_value(row, "Rationale"),
            severity=severity_to_regscale(self.mapping.get_value(row, "Criticality Value")),
            status=(
                VulnerabilityStatus.Open
                if self.mapping.get_value(row, "Status") == "Failed"
                else VulnerabilityStatus.Closed
            ),
            cvsSv3BaseScore=safe_float(0.0),
            vprScore=safe_float(0.0),
            firstSeen=self.handle_integration_date(self.mapping.get_value(row, "Last Scan Date", None)),
            lastSeen=self.handle_integration_date(self.mapping.get_value(row, "Evaluation Date", None)),
            plugInId=self.mapping.get_value(row, "Control ID"),
            plugInName="QualysPolicyScan",
            dns=self.mapping.get_value(row, "Control ID"),  # really asset_identifier
        )
        return finding


def severity_to_regscale(severity: str) -> VulnerabilitySeverity:
    """
    Convert Qualys severity to RegScale severity
        severity is given in numbers from 1-5, 5 being the highest
    :param str severity: Qualys severity to map to a RegScale severity
    :return: RegScale severity
    :rtype: IssueSeverity
    """
    severity_mapping = {
        "1": VulnerabilitySeverity.Low,
        "2": VulnerabilitySeverity.Low,
        "3": VulnerabilitySeverity.Medium,
        "4": VulnerabilitySeverity.High,
        "5": VulnerabilitySeverity.Critical,
    }
    return severity_mapping.get(severity, VulnerabilitySeverity.Low)
