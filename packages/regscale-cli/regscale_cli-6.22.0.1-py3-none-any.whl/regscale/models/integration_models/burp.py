#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pydantic model for a Burp Scan"""
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generator, List, Optional, TextIO
from urllib.parse import urlparse
from xml.etree.ElementTree import Element, ParseError, fromstring, parse
from logging import getLogger

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import check_file_path, get_current_datetime
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models.integration_models.burp_models import BurpRequest, BurpResponse, Issue, RequestResponse
from regscale.models.regscale_models import File
from regscale.models.regscale_models import Issue as RegscaleIssue

# standard python imports


class Burp:
    """Burp Scan information"""

    def __init__(self, app: Application, file_path: str, encoding="utf-8", **kwargs) -> "Burp":
        logger = getLogger("regscale")
        logger.info("Now processing %s", file_path)
        self.integration_assets: Generator[IntegrationAsset, None, None] = (x for x in [])
        self.integration_findings: Generator[IntegrationFinding, None, None] = (x for x in [])
        self.num_assets = 0
        self.num_findings = 0
        self.job_complete = False
        self.logger = logger
        self.app = app
        self.api = Api()
        self.parent_id = 0
        self.parent_module = "assets"
        if "parentId" in kwargs and kwargs["parentId"]:
            self.parent_id = kwargs["parentId"]
        if "parentModule" in kwargs and kwargs["parentModule"]:
            self.parent_module = kwargs["parentModule"]
        self.encoding = encoding
        self.file_path = Path(file_path)
        self.version = None
        self.export_time = None
        self.burp_issues = []
        self.existing_issues = []
        self.from_file()

    def move_files(self, upload_file: Optional[bool] = True) -> None:
        """
        Move files to processed directory and upload to RegScale after processing

        :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing. Default is True.
        :rtype: None
        """
        api = Api()
        # Create processed directory if it doesn't exist, and copy file to it.

        new_file_path: Path = Path()
        processed_dir = self.file_path.parent / "processed"
        check_file_path(str(processed_dir.absolute()))
        try:
            if self.parent_id and self.job_complete:
                file_name = f"{self.file_path.stem}_{get_current_datetime('%Y%m%d-%I%M%S%p')}".replace(" ", "_")
                # Rename to friendly file name and post to Regscale
                new_file_path = self.file_path.rename(self.file_path.parent / (file_name + ".xml"))
                self.logger.info(
                    "Renaming %s to %s...",
                    self.file_path.name,
                    new_file_path.name,
                )
                if upload_file and File.upload_file_to_regscale(
                    file_name=str(new_file_path.absolute()),
                    parent_id=self.parent_id,
                    parent_module="securityplans",
                    api=api,
                ):
                    self.logger.info("Uploaded %s to RegScale securityplans #%i.", new_file_path.name, self.parent_id)
                shutil.move(new_file_path, processed_dir)
                try:
                    # Clean up the gzipped file created
                    os.remove(new_file_path.with_suffix(".gz"))
                except FileNotFoundError:
                    self.logger.debug(
                        "File %s already exists in %s",
                        new_file_path.with_suffix(".gz").name,
                        processed_dir,
                    )
        except shutil.Error:
            self.logger.debug(
                "File %s already exists in %s",
                new_file_path.name,
                processed_dir,
            )

    def from_file(self) -> None:
        """
        Read Burp Scan file

        :rtype: None
        """
        self.logger.debug(os.getcwd())
        try:
            with open(file=self.file_path, mode="r", encoding=self.encoding) as file:
                root = self.file_root_element(file)
                self.version = root.attrib["burpVersion"]
                self.export_time = root.attrib["exportTime"]
                self.gen_findings(root)
                self.gen_assets()
                self.job_complete = True
        except (FileNotFoundError, ParseError):
            self.logger.error("File not found: %s", self.file_path)

    @staticmethod
    def file_root_element(file: TextIO) -> Element:
        """
        Function returns the root element for tree of given file with scan results

        :param TextIO file: file with scan results
        :return: root element for this tree
        :rtype: Element
        """

        scan_file_parsed = parse(file)
        root = scan_file_parsed.getroot()
        return root

    def create_issue(self, xml: Element) -> Issue:
        """
        Create an issue from the XML

        :param Element xml: XML
        :return: Issue object from XML
        :rtype: Issue
        """
        issue = Issue()
        issue.serialNumber = self.get(xml, "serialNumber")
        issue.type = self.get(xml, "type")
        issue.host = self.get_domain_name(self.get(xml, "host"))
        issue.path = self.get(xml, "path")
        issue.name = self.get(xml, "name")
        issue.location = self.get(xml, "location")
        issue.severity = self.get(xml, "severity")
        issue.confidence = self.get(xml, "confidence")
        issue.background = self.strip_html_tags(self.get(xml, "issueBackground"))
        issue.detail = self.get(xml, "issueDetail")
        issue.remediation_background = self.strip_html_tags(self.get(xml, "remediationBackground"))
        issue.remediation_detail = self.strip_html_tags(self.get(xml, "remediationDetail"))
        issue.links = self.extract_links(self.get(xml, "vulnerabilityClassifications"))
        issue.cwes = self.extract_classifications(self.get(xml, "vulnerabilityClassifications"))
        issue.request_response = self.get_io(xml)
        return issue

    def create_regscale_finding(self, issue: Issue, scan_time: datetime, fmt: str) -> Optional[IntegrationFinding]:
        """
        Create a RegScale finding from a Burp Issue

        :param Issue issue: Burp Issue
        :param datetime scan_time: Scan time
        :param str fmt: Format for datetime object
        :return: RegScale Issue
        :rtype: Optional[IntegrationFinding]
        """
        remediation_actions = None
        if issue.severity.lower() == "info":
            return None
        due_date = self.get_due_delta(issue.severity)
        if issue.detail and issue.remediation_background:
            remediation_actions = issue.detail + "<br>" + issue.remediation_background
        elif issue.remediation_background:
            remediation_actions = issue.remediation_background
        elif issue.detail:
            remediation_actions = issue.detail
        # No CVE available, must use background
        cve = self.extract_cve(issue.background)
        external_id = str(hex(int(issue.type)) if issue.type and (issue.type).isdigit() else issue.type).replace(
            "0x", "0x00"
        )  # Use burp hexidecimal issue type and format as external_id
        finding = IntegrationFinding(
            control_labels=[],  # Add an empty list for control_labels
            category="Burp Vulnerability",  # Add a default category
            title=issue.name,
            description=(issue.background if issue.background else "")[:255],
            severity=RegscaleIssue.assign_severity(issue.severity),
            status="Open",
            asset_identifier=issue.host,
            external_id=external_id,
            remediation=(remediation_actions if remediation_actions else "update affected package")[:255],
            cvss_score=None,
            cve=cve,
            cvss_v3_base_score=None,
            source_rule_id=str(issue.type),
            vulnerability_type="Vulnerability Scan",
            baseline="Burp Host",
            recommendation_for_mitigation=issue.remediation_background,
            results=issue.detail,
            plugin_name=issue.type,
            plugin_id=issue.type,
            ip_address=issue.host,
        )
        if issue.detail:
            finding.description = finding.description + "<br>" + issue.detail
        if issue.cwes:
            finding.description = finding.description + "<br>" + ", ".join(issue.cwes)
        finding.first_seen = datetime.strftime(scan_time, fmt)
        finding.last_seen = datetime.strftime(scan_time, fmt)
        if scan_time + timedelta(days=due_date) < datetime.now():
            finding.due_date = datetime.strftime(datetime.now() + timedelta(days=due_date), fmt)
        else:
            finding.due_date = datetime.strftime(scan_time + timedelta(days=due_date), fmt)
        finding.basis_for_adjustment = "Burp Scan import"

        return finding

    def gen_findings(self, root: Element) -> None:
        """
        Generate issues

        :param Element root: Root
        :rtype: None
        """
        issues = []
        findings = set()
        self.existing_issues = RegscaleIssue.get_all_by_parent(parent_id=self.parent_id, parent_module="securityplans")
        root_issues = root.findall("issue")
        fmt = "%Y-%m-%d %H:%M:%S"
        scan_time = datetime.strptime(root.attrib["exportTime"], "%a %b %d %H:%M:%S %Z %Y")
        for xml in root_issues:
            issue = self.create_issue(xml)
            issues.append(issue)
            regscale_finding = self.create_regscale_finding(issue, scan_time, fmt)
            if regscale_finding and regscale_finding not in findings:
                findings.add(regscale_finding)
                self.num_findings += 1
        self.burp_issues = issues
        self.integration_findings = (x for x in findings)

    def get_due_delta(self, severity: str) -> int:
        """
        Find the due delta from the config file

        :param str severity: The severity level
        :return: Due date delta
        :rtype: int
        """
        # Leave at Tenable for now
        due_delta = self.app.config["issues"]["tenable"]["low"]
        if severity.lower() in ["medium", "moderate"]:
            due_delta = self.app.config["issues"]["tenable"]["moderate"]
        elif severity.lower() == "high":
            due_delta = self.app.config["issues"]["tenable"]["high"]
        elif severity.lower() == "critical":
            due_delta = self.app.config["issues"]["tenable"]["critical"]
        return due_delta

    @classmethod
    def get(cls, item: Any, key: Any) -> Optional[Any]:
        """
        Get item

        :param Any item: Object to try and get value from
        :param Any key: The key to get the value with
        :return: item stored at the provided key, or None if not found
        :rtype: Optional[Any]
        """
        try:
            return item.find(key).text
        except (AttributeError, KeyError):
            return None

    @staticmethod
    def extract_numbers(string: str) -> List[int]:
        """
        Extract numbers from string

        :param str string: string with numbers
        :return: List of numbers found in provided string
        :rtype: List[int]
        """
        return re.findall(r"\d+", string)

    @staticmethod
    def get_request_response(item: Element) -> RequestResponse:
        """
        Get the Request/Response object

        :param Element item: item
        :return: The Request/Response object
        :rtype: RequestResponse
        """
        request_data = item.find(".//request")
        if (response_data := item.find(".//response")) is not None:
            base64_dat = request_data.attrib.get("base64", "false").lower() == "true"
            response_data_is_base64 = BurpResponse.is_base64(response_data.text)
            method = request_data.attrib.get("method", "GET")
            request = (
                BurpRequest(dataString=request_data.text, base64=base64_dat, method=method)
                if BurpRequest.is_base64(request_data.text)
                else None
            )
            response = BurpResponse(
                dataString=response_data.text if response_data_is_base64 else None,
                base64=(bool(item.find(".//response").attrib["base64"]) if response_data_is_base64 else False),
            )
            return RequestResponse(request=request, response=response)
        return RequestResponse(request=None, response=None)

    def get_io(self, xml: Element) -> RequestResponse:
        """
        Generate the Response Request object

        :param Element xml: xml
        :return: The Request/Response object
        :rtype: RequestResponse
        """
        for item in xml.findall("requestresponse"):
            dat = item.find(".//request")
            if dat.tag == "request":
                return self.get_request_response(item)

    def gen_assets(self) -> None:
        """
        Generate RegScale Assets from Burp Issues

        :rtype: None
        :return: None
        """
        assets: List[IntegrationAsset] = []
        for issue in self.burp_issues:
            host_name = None
            hosts = self.extract_ip_address(issue.host)
            host_name = issue.host
            if hosts:
                host_name = hosts[0]
            integration_asset = IntegrationAsset(
                name=host_name,
                identifier=host_name,
                asset_type="Virtual Machine (VM)",
                asset_owner_id=self.app.config["userId"],
                parent_id=self.parent_id,
                parent_module=self.parent_module,
                asset_category="Hardware",
                date_last_updated=get_current_datetime(),
                status="Active (On Network)",
                ip_address=host_name if hosts else None,
                is_public_facing=False,
                mac_address="",
                fqdn="",
                disk_storage=0,
                cpu=0,
                ram=0,
            )
            if integration_asset.name not in [asset.name for asset in assets]:
                assets.append(integration_asset)
                self.num_assets += 1
        self.integration_assets = (x for x in assets)

    @staticmethod
    def extract_ip_address(string: str) -> List[str]:
        """
        Extract IP address from string

        :param str string: string to extract IP address from
        :return: List of IP addresses found in provided string
        :rtype: List[str]
        """
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        return re.findall(ip_pattern, string)

    @staticmethod
    def extract_links(html: str) -> List[str]:
        """
        Extract links from html with standard library

        :param str html: HTML
        :return: List containing links found in the provided HTML string
        :rtype: List[str]
        """
        root = fromstring(html)
        return [link.attrib["href"] for link in root.iter("a")]

    @staticmethod
    def extract_classifications(html: str) -> List[str]:
        """
        Extract classifications from html with standard library

        :param str html: HTML to parse classifications from
        :return: List containing classifications found in the provided HTML string
        :rtype: List[str]
        """
        root = fromstring(html)
        return [link.text.strip() for link in root.iter("a")]

    @staticmethod
    def get_domain_name(url: str) -> str:
        """
        Get the domain name from a URL

        :param str url: URL
        :return: Domain name
        :rtype: str
        """
        parsed_url = urlparse(url)
        domain_name = parsed_url.hostname
        return domain_name

    @staticmethod
    def strip_html_tags(text: str) -> str:
        """
        Strip HTML tags from a string.

        :param str text: The string containing HTML tags
        :return: The string without HTML tags
        :rtype: str
        """
        if not text:
            return text
        clean = re.sub(r"<.*?>", "", text)
        return clean

    @staticmethod
    def extract_cve(input_string: str) -> Optional[str]:
        """
        Extract CVEs from a string.

        :param str input_string: The string to extract CVEs from
        :return: List of CVEs found in the provided string
        :rtype: Optional[str]
        """
        cve_pattern = r"CVE-\d{4}-\d{4,7}"
        cve_ids = re.findall(cve_pattern, input_string)
        return cve_ids.pop() if cve_ids else None
