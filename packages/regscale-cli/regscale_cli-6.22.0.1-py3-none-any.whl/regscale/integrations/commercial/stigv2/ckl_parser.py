"""
This module is responsible for parsing STIG (Security Technical Implementation Guide) .ckl (Checklist) files.
It provides functionality to extract relevant information from .ckl files for further processing and analysis.
"""

import io
import logging
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any, Generator, Union

import lxml.etree as et
from lxml.etree import Element
from pydantic import BaseModel, ConfigDict

from regscale.core.utils import snakify

logger = logging.getLogger("regscale")


def stig_component_title(stig_title: str) -> str:
    """
    Extract the component title from the STIG title.

    :param str stig_title: The STIG title.
    :return: The component title.
    :rtype: str
    """
    return stig_title.replace("  ", " ").strip()  # Ensure no double spaces are present


def find_stig_files(directory: Path) -> List[Path]:
    """
    Finds all STIG (.ckl) files within the specified directory.

    :param Path directory: Path to the directory where STIG files are located.
    :return: A list of paths to STIG files.
    :rtype: List[Path]
    """
    if str(directory).startswith("s3://"):
        logger.info(f"Found S3 URI: {directory}")
        return [directory]

    if str(directory).endswith(".ckl"):
        logger.info(f"Found CKL file: {directory}")
        return [directory]

    logger.info(f"Searching for STIG files in {directory}")
    path = Path(directory)

    if not path.is_dir():
        logger.error(f"{directory} is not a valid directory")
        return []

    def is_hidden(filepath):
        return any(part.startswith(".") for part in filepath.parts)

    stig_files: list[Path] = [file for file in path.glob("**/*.ckl") if not is_hidden(file)]
    logger.info(f"Found {len(stig_files)} STIG file(s)")
    return stig_files


class Asset(BaseModel):
    """Data model for Asset with optional attributes."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=snakify)

    role: Optional[str] = None
    asset_type: Optional[str] = None
    host_name: Optional[str] = None
    host_ip: Optional[str] = None
    host_mac: Optional[str] = None
    host_fqdn: Optional[str] = None
    tech_area: Optional[str] = None
    target_key: Optional[str] = None
    web_or_database: Optional[bool] = None
    web_db_site: Optional[str] = None
    web_db_instance: Optional[str] = None


class STIGInfo(BaseModel):
    """Data model for STIG Information with optional and required attributes."""

    version: str
    classification: str
    customname: Optional[str] = None
    stigid: str
    description: Optional[str] = None
    filename: Optional[str] = None
    releaseinfo: str
    title: str
    uuid: str
    notice: str
    source: Optional[str] = None


class VulnStatus(Enum):
    """Enumeration for STIG vulnerability status."""

    OPEN = "OPEN"
    NOT_A_FINDING = "NOT A FINDING"
    NOT_APPLICABLE = "NOT APPLICABLE"
    COMPLETED = "COMPLETED"


class Vuln(BaseModel):
    """Data model for Vulnerability with optional and required attributes."""

    vuln_num: str
    severity: str
    group_title: str
    rule_id: str
    rule_ver: str
    rule_title: str
    check_content: Optional[str] = None
    fix_text: str
    check_content_ref: Optional[str] = None
    weight: str
    stigref: Optional[str] = None
    targetkey: Optional[str] = None
    stig_uuid: str
    vuln_discuss: Optional[str] = None
    ia_controls: Optional[str] = None
    class_: Optional[str] = None
    cci_ref: list[str] = []
    false_positives: Optional[str] = None
    false_negatives: Optional[str] = None
    documentable: Optional[str] = None
    mitigations: Optional[str] = None
    potential_impact: Optional[str] = None
    third_party_tools: Optional[str] = None
    mitigation_control: Optional[str] = None
    responsibility: Optional[str] = None
    security_override_guidance: Optional[str] = None
    legacy_id: Optional[str] = None
    status: Optional[str] = None
    finding_details: Optional[str] = None
    comments: Optional[str] = None
    severity_override: Optional[str] = None
    severity_justification: Optional[str] = None


class STIG(BaseModel):
    """Data model for STIG including STIG information and vulnerabilities."""

    baseline: str
    stig_info: STIGInfo
    vulns: List[Vuln] = []

    @property
    def component_title(self) -> str:
        """
        Extract the component title from the STIG title.

        :return: The component title.
        :rtype: str
        """
        return stig_component_title(self.stig_info.title)


class Checklist(BaseModel):
    """Data model for Checklist including Asset and STIGs."""

    assets: List[Asset] = []
    stigs: List[STIG] = []


def parse_element_to_dict(
    element: Element,
    key_tag: Optional[str] = None,
    value_tag: Optional[str] = None,
    list_fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    This function parses an XML element into a dictionary. It can operate in two modes:
    1. If key_tag and value_tag are provided, it searches for these specific tags within each child element
       to construct key-value pairs for the dictionary.
    2. If key_tag and value_tag are not provided, it converts all child elements of the given element
       directly to a dictionary with child tag names as keys and their text content as values.

    :param Element element: The XML element to parse.
    :param Optional[str] key_tag: Optional; the tag name that contains the key for key-value parsing mode.
    :param Optional[str] value_tag: Optional; the tag name that contains the value for key-value parsing mode.
    :param Optional[List[str]] list_fields: Optional; list of fields that are expected to have lists back.
    :return: A dictionary representation of the element.
    :rtype: Dict[str, Any]
    """
    if list_fields is None:
        list_fields = []

    if key_tag and value_tag:
        return _parse_key_value_pairs(element, key_tag, value_tag, list_fields)
    else:
        return _parse_direct_child_elements(element)


def _parse_key_value_pairs(element: Element, key_tag: str, value_tag: str, list_fields: List[str]) -> Dict[str, Any]:
    """
    Parse key-value pairs from XML element based on provided key and value tags.

    :param Element element: The XML element to parse.
    :param str key_tag: The tag name that contains the key for key-value parsing mode.
    :param str value_tag: The tag name that contains the value for key-value parsing mode.
    :param List[str] list_fields: List of fields that are expected to have lists back.
    :return: A dictionary of parsed key-value pairs.
    :rtype: Dict[str, Any]
    """
    parsed_data: dict[str, Any] = {}
    for child in element.findall(f".//{key_tag}"):
        key = child.text
        value_element = child.find(f"../{value_tag}")
        value = getattr(value_element, "text", None)
        if key:
            key = snakify(key)
            if key in list_fields:
                parsed_data.setdefault(key, []).append(value) if value else None
            else:
                parsed_data[key] = value
    return parsed_data


def _parse_direct_child_elements(element: Element) -> Dict[str, Any]:
    """
    Parse direct child elements of an XML element into a dictionary.

    :param Element element: The XML element to parse.
    :return: A dictionary of direct child elements.
    :rtype: Dict[str, Any]
    """
    result = {}
    for child in element:
        key = snakify(child.tag)
        # Use empty string for None to ensure the field is included
        value = child.text if child.text is not None else ""
        result[key] = value
    return result


def parse_checklist(file_path: Union[str, Path]) -> Checklist:
    """
    Main function to parse a checklist from an XML file or S3 object using lxml for parsing.

    :param Union[str, Path] file_path: The path to the XML file or S3 object.
    :raises ValueError: If the ASSET element is not found in the XML
    :return: Checklist object
    :rtype: Checklist
    """
    try:
        import boto3

        if isinstance(file_path, str) and file_path.startswith("s3://"):
            # Handle S3 path
            s3_parts = file_path[5:].split("/", 1)
            bucket = s3_parts[0]
            key = s3_parts[1]

            s3 = boto3.client("s3")
            response = s3.get_object(Bucket=bucket, Key=key)
            content = response["Body"].read()

            tree = et.parse(io.BytesIO(content))
            root = tree.getroot()
            file_name = key.split("/")[-1]
        else:
            # Handle local file path
            xml_path = Path(file_path)
            tree = et.parse(xml_path)
            root = tree.getroot()
            file_name = xml_path.name

        # Parse the Assets
        asset_elem = root.find("ASSET")
        if asset_elem is None:
            raise ValueError("ASSET element not found in XML.")
        assets = [Asset(**parse_element_to_dict(asset_elem))]

        stigs = [
            STIG(
                baseline=file_name.split(".")[0].split("-")[0].strip(),
                stig_info=STIGInfo(**parse_element_to_dict(istig_elem, key_tag="SID_NAME", value_tag="SID_DATA")),
                vulns=[
                    Vuln(
                        **parse_element_to_dict(
                            vuln_elem,
                            key_tag="VULN_ATTRIBUTE",
                            value_tag="ATTRIBUTE_DATA",
                            list_fields=[
                                "cci_ref",
                            ],
                        ),
                        status=vuln_elem.findtext("STATUS"),
                        finding_details=vuln_elem.findtext("FINDING_DETAILS"),
                        comments=vuln_elem.findtext("COMMENTS"),
                        severity_override=vuln_elem.findtext("SEVERITY_OVERRIDE"),
                        severity_justification=vuln_elem.findtext("SEVERITY_JUSTIFICATION"),
                    )
                    for vuln_elem in istig_elem.findall("VULN")
                ],
            )
            for istig_elem in root.findall(".//iSTIG")
            if istig_elem.find("STIG_INFO") is not None
        ]

        return Checklist(assets=assets, stigs=stigs)
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {e}")
        raise e


def get_components_from_checklist(
    checklist: Checklist,
) -> Generator[dict[str, str], None, None]:
    """
    Extract the component titles from the checklist using a generator expression.

    :param Checklist checklist: The checklist object.
    :return: A generator of component titles.
    :rtype: Generator[dict[str, str], None, None]
    """
    return ({stig.stig_info.stigid: stig_component_title(stig.stig_info.title)} for stig in checklist.stigs)


def get_all_components_from_checklists(checklists: List[Checklist]) -> dict[str, str]:
    """
    Extract the component titles from a list of checklists using a generator expression.

    :param List[Checklist] checklists: The list of checklist objects.
    :return: A dictionary of unique component titles.
    :rtype: dict[str, str]
    """
    components: dict[str, str] = {}
    for checklist in checklists:
        # Collect all components from the generator into a single dictionary
        components.update({k: v for d in get_components_from_checklist(checklist) for k, v in d.items()})
    return components


def get_all_assets_from_checklists(checklists: List[Checklist]) -> List[Asset]:
    """
    Extract the assets from a list of checklists.

    :param List[Checklist] checklists: The list of checklist objects.
    :return: A list of unique assets.
    :rtype: List[Asset]
    """
    assets = set()
    for checklist in checklists:
        assets.update(checklist.assets)
    return list(assets)
