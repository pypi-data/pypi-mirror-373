#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=I1101, W0212
"""Functions used to interact with RegScale API"""

# standard imports
import io
import json
import pickle
import re
import tempfile
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Set, Tuple, Union
from xml.etree.ElementTree import Element

import psutil
import requests
from lxml import etree

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import convert_datetime_to_regscale_string, error_and_exit
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.vulnerability import Vulnerability

logger = create_logger()
ARTIFACTS_PATH = Path.cwd() / "artifacts"


class IteratorConsumptionError(Exception):
    """
    Exception raised when an error occurs while consuming an iterator

    :param str message: Error message, defaults to "Error while consuming iterator"
    """

    def __init__(self, message: str = "Error while consuming iterator"):
        self.message = message
        super().__init__(self.message)


def extract_version(cpe: str) -> Optional[Any]:
    """
    Function returns version from CPE string

    :param str cpe: CPE string
    :return: version
    :rtype: Optional[Any]
    """
    match = re.search(r"\d+(\.\d+)*", cpe)
    if match and len(match.group()) > 1:
        return match.group()
    return None


def determine_identifier(asset: Asset) -> str:
    """
    Function returns asset identifier

    :param Asset asset: RegScale Asset
    :return: asset identifier
    :rtype: str
    """
    # Determine the identifier based on the following priority order.
    # If the first attribute is not set, then the next attribute is checked, etc.
    attributes_to_check = [
        asset.name,
        asset.fqdn,
        asset.ipAddress,
        asset.macAddress,
        asset.awsIdentifier,
    ]
    return next((attr for attr in attributes_to_check if attr), "")


def get_cpe_file(download: bool = False) -> Path:
    """
    Function updates CPE file

    :param bool download: Whether to download the file, defaults to False
    :return: Path to CPE file
    :rtype: Path
    """
    url = "https://nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.2.xml.zip"
    save_path = ARTIFACTS_PATH / "official-cpe-dictionary_v2.2.xml"
    if not ARTIFACTS_PATH.exists():
        ARTIFACTS_PATH.mkdir()
        download = True
    if not save_path.exists():
        download = True
    # Download file
    if download:
        # rm file if already exists
        if save_path.exists():
            save_path.unlink()
        logger.info("Downloading CPE file from %s", url)
        response = requests.get(url=url, timeout=60)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content), "r") as zip_ref:
                zip_ref.extractall(ARTIFACTS_PATH)
            logger.info("File downloaded and extracted successfully to %s", ARTIFACTS_PATH)
        else:
            logger.error("Failed to download the file. Status code: %i", response.status_code)
    return save_path


def filter_severity(list_of_vulns: List[Vulnerability], minimum_severity: str) -> List[Vulnerability]:
    """
    Filter out vulnerabilities based on a minimum severity level

    :param List[Vulnerability] list_of_vulns: list of vulnerabilities
    :param str minimum_severity: minimum severity level
    :return: list of vulnerabilities
    :rtype: List[Vulnerability]
    """
    result_vulns = []
    severities = {0: "low", 1: "moderate", 2: "high", 3: "critical"}
    # select severity from severities by value
    try:
        val = next(severity for severity, value in severities.items() if value == minimum_severity)
    except StopIteration:
        logger.warning(
            "Unable to get minimum_severity value from config value: %s, defaulting to low",
            minimum_severity,
        )
        val = 0
    for vuln in list_of_vulns:
        vuln.severity = "moderate" if vuln.severity == "medium" else vuln.severity
        try:
            vuln_val = next(severity for severity, value in severities.items() if value == vuln.severity.lower())
        except StopIteration:
            logger.warning(
                "Unable to get severity value from vulnerability: %s, defaulting to low",
                vuln.severity,
            )
        if vuln_val >= val:
            result_vulns.append(vuln)
    return result_vulns


def get_cpe_data() -> Tuple[etree._ElementTree, List[dict[Any, Any]]]:
    """
    Get the CPE data

    :return: CPE Root and CPE data
    :rtype: Tuple[etree._ElementTree, List[dict[Any, Any]]]
    """
    cpe_list = []
    cpe_root = etree._ElementTree()
    try:
        cpe_root = etree.parse(get_cpe_file())
        cpe_list = cpe_xml_to_dict(cpe_root)
    except OSError:
        error_and_exit("Error parsing CPE file, unable to access file.")
    return cpe_root, cpe_list


def get_min_cvss_score(severity: str) -> float:
    """
    Get the minimum CVSS score for a given severity level

    :param str severity: The severity level
    :return: The minimum CVSS score
    :rtype: float
    """
    severity_levels = {
        "critical": 9.9,
        "high": 7.0,
        "medium": 4.0,
        "moderate": 4.0,
        "low": 0.1,
        "info": 0.0,  # Assuming Info has a minimum value of 0
        # You can add more severity levels if needed
    }

    return severity_levels.get(severity, None)


def get_due_delta(app: Application, severity: str) -> int:
    """
    Find the due delta from the config file

    :param Application app: The app object
    :param str severity: The severity level
    :return: Due date delta
    :rtype: int
    """
    due_delta = app.config["issues"]["tenable"]["low"]
    if severity.lower() in ["medium", "moderate"]:
        due_delta = app.config["issues"]["tenable"]["moderate"]
    elif severity.lower() == "high":
        due_delta = app.config["issues"]["tenable"]["high"]
    elif severity.lower() == "critical":
        due_delta = app.config["issues"]["tenable"]["critical"]
    return due_delta


def determine_available_space() -> float:
    """
    Determine if there is enough space to store the reports

    :return: Available space in bytes for the temp directory
    :rtype: float
    """
    tmp_dir = tempfile.gettempdir()
    available_space = psutil.disk_usage(tmp_dir).free
    return available_space


def determine_needed_space(vuln_list: List[dict], total_chunks: int) -> int:
    """
    Determine the approximate size required to store Tenable IO data temporarily on temp disk.

    :param List[dict] vuln_list: List of vulnerabilities
    :param int total_chunks: Total number of chunks
    :return: Rough size of all chunks in bytes
    :rtype: int
    """
    if not vuln_list:
        # No list, you have an empty query
        return 0
    with tempfile.TemporaryFile() as temp_file:
        # determine the size of the first chunk as a pickle
        pickle.dump(vuln_list, temp_file)
        # Get the size of the file in bytes
        temp_file.seek(0, 2)  # Seek to the end of the file
        file_size = temp_file.tell()
        logger.debug("1st Chunk File size: %s", file_size)
        # file deletes on close
    return total_chunks * file_size


def get_minimum_severity(app: Application) -> str:
    """
    Find the minimum severity level from the config file

    :param Application app: The app object
    :return: Minimum severity level
    :rtype: str
    """
    config = app.config
    minimum_severity = "low"
    if "tenableMinimumSeverityFilter" in config:
        minimum_severity = app.config["tenableMinimumSeverityFilter"]
    else:
        # update config
        config["tenableMinimumSeverityFilter"] = minimum_severity
        app.save_config(config)
    return minimum_severity


def lookup_kev(cve: Optional[str], data: Optional[list[dict]] = None) -> Tuple[Any, Any]:
    """
    Determine if the cve is part of the published CISA KEV list

    :param Optional[str] cve: The CVE to lookup.
    :param Optional[list[dict]] data: The KEV data, defaults to None
    :return: A tuple containing the KEV data and the date.
    :rtype: Tuple[Any, Any]
    """
    kev_data = None
    kev_date = None
    if not cve:
        return kev_data, kev_date
    if data:
        try:
            # Update kev and date
            kev_data = next(
                dat
                for dat in data["vulnerabilities"]
                if "vulnerabilities" in data and cve and dat["cveID"].lower() == cve.lower()
            )
        except (StopIteration, ConnectionRefusedError):
            kev_data = None
    if kev_data:
        # Convert YYYY-MM-DD to datetime
        kev_date = convert_datetime_to_regscale_string(datetime.strptime(kev_data["dueDate"], "%Y-%m-%d"))
    return kev_data, kev_date


def cpe_xml_to_dict(cpe_root: etree._ElementTree) -> List[dict]:
    """
    Function returns a dict of CPEs by name

    :param etree._ElementTree cpe_root: cpe root element
    :return: cpe_items
    :rtype: List[dict]
    """
    mitre_reference_ns = (
        "{http://cpe.mitre.org/dictionary/2.0}references/{http://cpe.mitre.org/dictionary/2.0}reference"
    )
    cpe_items = []
    # Create folder with Path
    artifacts_path = Path.cwd() / "artifacts"
    artifacts_path.mkdir(parents=True, exist_ok=True)
    cpe_json = artifacts_path / "cpe_items.json"
    if not cpe_json.exists():
        logger.info("Creating cpe_items.json on initial run.")
        for cpe_item in cpe_root.iterfind("{http://cpe.mitre.org/dictionary/2.0}cpe-item"):
            name = cpe_item.get("name")
            title = cpe_item.find("{http://cpe.mitre.org/dictionary/2.0}title").text
            references = [ref.get("href") for ref in cpe_item.iterfind(mitre_reference_ns)]
            cpe_items.append({"name": name, "title": title, "references": references})
        with open(cpe_json, "w", encoding="utf-8") as file:
            json.dump(cpe_items, file)
    else:
        logger.debug("Loading cpe_items.json")
        with open(cpe_json, "r", encoding="utf-8") as file:
            cpe_items = json.load(file)
    return cpe_items


def lookup_cpes_by_name(cpes: Set[dict], cpe_items: List[dict]) -> List[dict]:
    """
    Function returns CPE items by name

    :param Set[dict] cpes: set of CPE names
    :param List[dict] cpe_items: list of cpe-item dicts
    :return: CPE items
    :rtype: List[dict]
    """

    def gen_items():
        """
        Generator function returns CPE items by name

        """
        result = []
        for cpe_item in cpe_items:
            if cpe_item["name"] in cpes:
                cpe_item["version"] = extract_version(cpe_item["name"])
                result.append(cpe_item)
        yield result

    start = time.time()
    gen = gen_items()
    try:
        results = next(gen)
    except StopIteration:
        results = None
    if results:
        end = time.time()
        logger.debug("lookup_cpes_by_name() took %s seconds", end - start)
    return results


def lookup_cpe_item_by_name(name: str, cpe_items: List[dict]) -> Optional[dict]:
    """
    Function returns CPE item by name

    :param str name: CPE name
    :param List[dict] cpe_items: list of cpe-item dicts
    :return: CPE item
    :rtype: Optional[dict]
    """

    def gen_item():
        """
        Generator function returns CPE item by name

        """
        for cpe_item in cpe_items:
            if name == cpe_item["name"]:
                yield cpe_item

    start = time.time()
    # Generator
    gen = gen_item()
    try:
        item = next(gen)
    except StopIteration:
        item = None
    if item:
        name = item["name"]
        title = item["title"]
        references = item["references"]
        end = time.time()
        logger.debug("lookup_cpe_item_by_name() took %s seconds", end - start)
        return {
            "Name": name,
            "Title": title,
            "References": references,
        }
    return item


def software(cpe_items: List[dict], report_host: Element) -> List[dict]:
    """
    Function returns software inventory from Nessus host

    :param List[dict] cpe_items: the list of cpes
    :param Element report_host: report host element
    :return: inventory
    :rtype: List[dict]
    """
    start = time.time()
    cpes = set()
    for tag in report_host[0].iterfind("tag"):
        tag_name = tag.get("name")
        if re.findall("cpe", tag_name) and tag_name is not None:
            cpe = (tag.text).split("->")[0].strip()
            cpes.add(cpe)
    inventory = lookup_cpes_by_name(cpes, cpe_items)
    end = time.time()
    logger.debug("software() took %s seconds", end - start)

    return inventory


def validate_nessus_severity(severity: str) -> str:
    """
    Validate a Nessus severity

    :param str severity: The nessus severity
    :raises ValueError: If the tenableMinimumSeverityFilter severity is not valid
    :return: The validated severity
    :rtype: str
    """
    if severity.lower() in ["info", "low", "medium", "high", "critical"]:
        return severity
    if severity.lower == "moderate":
        return "medium"
    raise ValueError(
        "Invalid tenableMinimumSeverityFilter setting in the configuration. "
        + "Must be one of: low, medium, high, or critical"
    )
