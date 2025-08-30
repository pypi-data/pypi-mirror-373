#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command to bulk import scans by folder path."""
import csv
import hashlib
import json
import logging
import os
import re
import shutil
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from os import PathLike
from typing import Optional, Union

import click
import pandas as pd
from pathlib import Path

from regscale.core.app.utils.file_utils import download_from_s3, get_files_by_folder
from regscale.models.integration_models.flat_file_importer import FlatFileImporter

logger = logging.getLogger("regscale")

FINGERPRINT_FILE_PATH = "regscale/integrations/commercial/import_all/scan_file_fingerprints.json"
EXCLUDE_MAPPING = ["burp", "nessus"]  # Scan types that do not support custom mappings


@click.group(name="import_all")
def import_all():
    """
    Import scans, vulnerabilities and assets to RegScale from scan export files
    """


@import_all.command(name="run")
@FlatFileImporter.common_scanner_options(
    message="Folder path containing scan files to process to RegScale.",
    prompt="Folder path containing scan files",
    import_name="all",
)
def import_all(
    folder_path: PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: Path,
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: bool,
):
    """
    Import scans, vulnerabilities and assets to RegScale from scan export files
    """
    if s3_bucket:
        # Download files from S3 to folder_path
        download_from_s3(s3_bucket, s3_prefix, folder_path, aws_profile)

    import_all_scans(
        folder_path=folder_path,
        regscale_ssp_id=regscale_ssp_id,
        scan_date=scan_date,
        upload_file=upload_file,
    )


def import_all_scans(
    folder_path: PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: Optional[Path] = None,
    disable_mapping: bool = False,
    upload_file: Optional[bool] = True,
):
    """
    Imports all scan files from a specified folder and processes them according to their scan type.

    :param PathLike[str] folder_path: The path to the folder containing scan files.
    :param int regscale_ssp_id: The RegScale SSP ID to associate with the scans.
    :param datetime scan_date: The date of the scans.
    :param Path mappings_path: The path to a custom mappings file.
    :param bool disable_mapping: Flag to disable custom mapping prompts.
    :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing, defaults to True
    """
    from regscale.integrations.commercial.aqua.aqua import import_aqua
    from regscale.integrations.commercial.aws.cli import import_scans as import_aws
    from regscale.integrations.commercial.burp import import_burp
    from regscale.integrations.commercial.microsoft_defender.defender import import_alerts
    from regscale.integrations.commercial.ecr import import_ecr
    from regscale.integrations.commercial.grype.commands import import_scans as import_grype_scans
    from regscale.integrations.commercial.ibm import import_appscan
    from regscale.integrations.commercial.nexpose import import_nexpose
    from regscale.integrations.commercial.opentext.commands import import_scans as import_opentext_file
    from regscale.integrations.commercial.prisma import import_prisma
    from regscale.integrations.commercial.qualys import import_scans as import_qualys
    from regscale.integrations.commercial.snyk import import_snyk
    from regscale.integrations.commercial.tenablev2.commands import import_nessus
    from regscale.integrations.commercial.trivy import import_scans as import_trivy_scans
    from regscale.integrations.commercial.veracode import import_veracode
    from regscale.integrations.commercial.xray import import_xray

    import_functions = {
        "aqua": {"function": import_aqua, "custom_mapping": mappings_path},
        "aws": {"function": import_aws, "custom_mapping": mappings_path},
        "burp": {"function": import_burp, "custom_mapping": mappings_path},
        "defender": {"function": import_alerts, "custom_mapping": mappings_path},
        "ecr": {"function": import_ecr, "custom_mapping": mappings_path},
        "grype": {"function": import_grype_scans, "custom_mapping": mappings_path},
        "ibm": {"function": import_appscan, "custom_mapping": mappings_path},
        "nessus": {"function": import_nessus, "custom_mapping": mappings_path},
        "nexpose": {"function": import_nexpose, "custom_mapping": mappings_path},
        "opentext": {"function": import_opentext_file, "custom_mapping": mappings_path},
        "prisma": {"function": import_prisma, "custom_mapping": mappings_path},
        "qualys": {"function": import_qualys, "custom_mapping": mappings_path},
        "snyk": {"function": import_snyk, "custom_mapping": mappings_path},
        "trivy": {"function": import_trivy_scans, "custom_mapping": mappings_path},
        "veracode": {"function": import_veracode, "custom_mapping": mappings_path},
        "xray": {"function": import_xray, "custom_mapping": mappings_path},
    }

    scans = set_scans(
        get_files_by_folder(
            str(folder_path),
            exclude_non_scan_files=True,
            file_excludes=[".DS_Store", "~", ".zip", "mapping.json", ".md", ".burp", ".html"],
            directory_excludes=["processed"],
        ),
        load_fingerprints(FINGERPRINT_FILE_PATH),
    )
    move_files(scans, str(folder_path))

    scan_folders = {}
    for scan_type in set(scans.values()):
        scan_folder = os.path.join(folder_path, scan_type)
        scan_folders[scan_type] = scan_folder

    logger.debug(json.dumps(scan_folders, indent=2))

    imports_to_process = {}
    for scan_type, import_function in import_functions.items():
        if scan_type in scan_folders:
            imports_to_process[scan_type] = import_function

    # Ask for any custom mappings
    if input("Do you have any custom mapping files? (y/n): ").strip().lower() == "y" and not disable_mapping:
        imports_to_process = set_custom_mappings(imports_to_process)

    # Show user summary of what will be imported and ask for confirmation before starting imports
    scan_counts = {scan_type: list(scans.values()).count(scan_type) for scan_type in set(scans.values())}
    total_files = sum(scan_counts.values())
    for scan_type, count in scan_counts.items():
        print(f"{scan_type}: {count} files")
    if input(f"Do you want to proceed with processing {total_files} scan file(s)? (y/n): ").strip().lower() != "y":
        print("Aborting scan processing.")
    else:
        import_scans(imports_to_process, scan_folders, regscale_ssp_id, scan_date, upload_file)


def import_scans(
    imports_to_process: dict, scan_folders: dict, regscale_ssp_id: int, scan_date: datetime, upload_file: bool
) -> None:
    """
    Imports scans by invoking specified processing functions for each scan type.
    :param dict imports_to_process: A dictionary where keys are scan types and values are dictionaries
       containing the processing function and custom mapping path.
       Example: {
           "scan_type_1": {
               "function": click_function_1,
               "custom_mapping": "path/to/custom_mapping_1"
           },
           "scan_type_2": {
               "function": click_function_2,
               "custom_mapping": None
           }
       }
    :param dict scan_folders: A dictionary where keys are scan types and values are folder paths
      containing the scans for each type.
      Example: {
          "scan_type_1": "path/to/scan_folder_1",
          "scan_type_2": "path/to/scan_folder_2"
      }
    :param int regscale_ssp_id: The RegScale SSP (System Security Plan) ID to associate with the scans.
    :param datetime scan_date: The date of the scans in 'YYYY-MM-DD' format.
    :param bool upload_file: Whether to upload the file to RegScale after processing
    :rtype: None
    """

    ctx = click.get_current_context()

    for scan_type, import_detail in imports_to_process.items():
        kwargs = {"folder_path": scan_folders[scan_type]}
        click_function = import_detail["function"]
        kwargs["scan_date"] = scan_date
        kwargs["regscale_ssp_id"] = regscale_ssp_id
        # make sure upload_file and mappings_path are passed if the function requires them
        for param in click_function.params:
            if param.name == "mappings_path":
                kwargs[param.name] = import_detail.get("custom_mapping") or Path.cwd() / "mappings" / scan_type
            elif param.name == "upload_file":
                kwargs[param.name] = upload_file
        ctx.invoke(
            click_function,
            **kwargs,
        )
        logger.info("Waiting before processing the next scan...")
        time.sleep(5)


def set_custom_mappings(imports_to_process: dict) -> dict:
    """
    Prompts the user to provide custom mapping files for each scan type in the given imports.
    :param dict imports_to_process: A dictionary where keys are scan types and values are dictionaries containing
        the processing function and custom mapping path.
    :return: The updated dictionary with custom mapping file paths added for each scan type, if provided by the user.
    :rtype: dict
    """

    for scan_type, import_detail in imports_to_process.items():
        if scan_type not in EXCLUDE_MAPPING:
            if input(f"Do you have a custom mapping file for {scan_type}? (y/n): ").strip().lower() == "y":
                import_detail["custom_mapping"] = input(f"Enter the mapping file path for {scan_type}: ").strip()
    return imports_to_process


def set_scans(file_list: list, fingerprints: dict) -> dict:
    """
    Set scans for a list of files based on their fingerprints.
    This function takes a list of file paths and a dictionary of fingerprints,
    and returns a dictionary mapping each file path to its corresponding scan type.
    If a file's fingerprint is not found in the provided fingerprints, it adds the
    fingerprint and reloads the fingerprints from the fingerprint file path.

    :param list file_list: A list of file paths to be scanned.
    :param dict fingerprints: A dictionary where keys are file hashes and values are scan types.
    :return: A dictionary mapping file paths to their corresponding scan types.
    :rtype: dict
    """

    scans = {}
    for file_path in file_list:
        file_hash = get_fingerprint_hash(file_path)
        scan_type = fingerprints.get(file_hash)
        if scan_type is None or not scan_type:
            add_fingerprint(file_hash, file_path)
            fingerprints = load_fingerprints(FINGERPRINT_FILE_PATH)
            scan_type = fingerprints.get(file_hash)
        if scan_type:
            scans[file_path] = scan_type
    return scans


def move_files(scans: dict, folder_path: str):
    """
    Moves files to designated folders based on their scan type.

    :param dict scans: A dictionary where keys are file paths and values are scan types.
    :param str folder_path: The base folder path where files will be moved.
    """

    for file_path, scan_type in scans.items():
        scan_folder = os.path.join(folder_path, scan_type)
        if not os.path.exists(scan_folder):
            os.makedirs(scan_folder)
        destination_path = os.path.join(scan_folder, os.path.basename(file_path))
        shutil.move(file_path, destination_path)


def fingerprint_csv(file_path: str) -> str:
    """
    Generates a SHA-256 fingerprint of the CSV file headers.
    This function reads the headers of a CSV file, sorts them, and then
    generates a SHA-256 hash of the concatenated header string.

    :param str file_path: The path to the CSV file.
    :return: The SHA-256 hash of the sorted CSV headers.
    :rtype: str
    """

    with open(file_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        headers_str = ",".join(sorted(headers))
        return hashlib.sha256(headers_str.encode()).hexdigest()


def fingerprint_json(file_path: str) -> str:
    """
    Generates a SHA-256 fingerprint of the JSON file's keys.
    This function reads a JSON file from the given file path, extracts the keys from the JSON data,
    and generates a SHA-256 hash of the keys.

    :param str file_path: The path to the JSON file.
    :return: The SHA-256 hash of the JSON keys.
    :rtype: str
    """

    with open(file_path) as f:
        keys = []
        data = json.load(f)
        if isinstance(data, list) and data:
            keys = list_keys(data[0])
        elif isinstance(data, dict):
            keys = list_keys(data)
        keys_str = str(keys)
    return hashlib.sha256(keys_str.encode()).hexdigest()


def list_keys(d: Union[dict, list], parent_key: Optional[str] = "") -> list:
    """
    Recursively lists all keys in a nested dictionary or list structure.

    :param Union[dict, list] d: The dictionary or list to traverse.
    :param Optional[str] parent_key: The base key to prepend to each key.
    :return: A list of keys (or indices) found in the nested structure.
    :rtype: list
    """

    keys = []
    if isinstance(d, dict):
        for k, v in d.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            if "findings[1]" in full_key:
                break
            keys.append(k)
            keys.extend(list_keys(v, full_key))
    elif isinstance(d, list):
        for i, item in enumerate(d):
            full_key = f"{parent_key}[{i}]"
            if "findings[1]" in full_key:
                break
            keys.append(i)
            keys.extend(list_keys(item, full_key))
    return keys


def fingerprint_xml(file_path: str) -> str:
    """
    Generates a SHA-256 fingerprint for the root element of an XML file.

    :param str file_path: The path to the XML file.
    :return: The SHA-256 hash of the root element of the XML file.
    :rtype: str
    """
    pattern = r" at 0x[0-9a-fA-F]+"
    tree = ET.parse(file_path)
    root_element = re.sub(pattern, "", str(tree.getroot()))
    return hashlib.sha256(root_element.encode()).hexdigest()


def fingerprint_xlsx(file_path: str) -> str:
    """
    Generates a SHA-256 fingerprint for the headers of an Excel file.
    This function reads an Excel file from the given file path, extracts the headers,
    sorts them, concatenates them into a single string, and then computes the SHA-256
    hash of that string.

    :param str file_path: The path to the Excel file.
    :return: The SHA-256 hash of the sorted headers.
    :rtype: str
    """

    df = pd.read_excel(file_path)
    headers = df.columns.tolist()
    headers_str = ",".join(sorted(headers))
    return hashlib.sha256(headers_str.encode()).hexdigest()


def get_fingerprint_hash(file_path: str) -> str:
    """
    Generate a fingerprint hash for a given file based on its extension.
    Supported file extensions:
        - .csv: Calls the fingerprint_csv function.
        - .json: Calls the fingerprint_json function.
        - .xml, .nessus: Calls the fingerprint_xml function.
        - .xlsx: Calls the fingerprint_xlsx function.

    :param str file_path: The path to the file for which the fingerprint hash is to be generated.
    :return: The fingerprint hash of the file if the file extension is supported, otherwise None.
    :rtype: str
    """

    file_hash = None
    if file_path.endswith(".csv"):
        file_hash = fingerprint_csv(file_path)
    elif file_path.endswith(".json"):
        file_hash = fingerprint_json(file_path)
    elif file_path.endswith(".xml") or file_path.endswith(".nessus"):
        file_hash = fingerprint_xml(file_path)
    elif file_path.endswith(".xlsx"):
        file_hash = fingerprint_xlsx(file_path)

    return file_hash or ""


def add_fingerprint(file_hash: str, file_path: str) -> None:
    """
    Adds a fingerprint entry for a given file hash and file path.
    This function prompts the user to select a scan type from a list of supported scans
    and associates the selected scan type with the provided file hash. The updated
    fingerprints are then saved to the fingerprint file.

    :param str file_hash: The hash of the file to add a fingerprint for.
    :param str file_path: The path of the file to add a fingerprint for.
    :rtype: None
    """

    supported_scans = [
        "SKIP FILE",
        "aws",
        "aqua",
        "burp",
        "defender",
        "ecr",
        "grype",
        "ibm",
        "nessus",
        "nexpose",
        "opentext",
        "prisma",
        "qualys",
        "snyk",
        "trivy",
        "veracode",
        "xray",
    ]
    fingerprints = load_fingerprints(FINGERPRINT_FILE_PATH)

    for i, scan in enumerate(supported_scans, 1):
        print(f"{i}. {scan}")
    choice = int(input(f"Enter the scan type number for file {file_path}: "))
    if 2 <= choice <= len(supported_scans):
        scan_type = supported_scans[choice - 1]
    elif choice == 1:
        print("Skipping file.")
        return
    else:
        print("Invalid choice. Skipping file.")
        return
    fingerprints[file_hash] = scan_type
    with open(FINGERPRINT_FILE_PATH, "w") as f:
        json.dump(fingerprints, f, indent=2)


def load_fingerprints(fingerprint_file_path: str) -> dict:
    """
    Load fingerprints from a JSON file.
    This function reads a JSON file containing fingerprints and returns them as a dictionary.
    If the file does not exist, it will load the default fingerprints file from the RegScale CLI Package.

    :param str fingerprint_file_path: The path to the JSON file containing fingerprints.
    :return: A dictionary containing the fingerprints if the file exists, otherwise an empty dictionary.
    :rtype: dict
    """
    if os.path.exists(fingerprint_file_path):
        with open(fingerprint_file_path, "r") as f:
            fingerprints = json.load(f)
        return fingerprints
    else:
        import importlib.resources as pkg_resources

        with pkg_resources.open_text(
            "regscale.integrations.commercial.import_all", "scan_file_fingerprints.json"
        ) as file:
            fingerprints = json.load(file)
        return fingerprints
