#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Upload files to RegScale."""
import logging
import xml.etree.ElementTree as ET
from typing import Optional, Union

from pathlib import Path

from regscale.core.app.api import Api
from regscale.models.regscale_models.file import File
from regscale.utils.b64conversion import decode_base64_to_bytesio, encode_file_to_base64

logger = logging.getLogger("regscale")


def file_upload(
    regscale_id: int,
    regscale_module: str,
    file_path: str,
    file_name: Optional[str] = None,
    **kwargs: dict,
) -> Optional[Union[list, dict]]:
    """Upload files to RegScale

    :param int regscale_id: RegScale ID
    :param str regscale_module: RegScale module
    :param str file_path: Path to file
    :param Optional[str] file_name: Optional name of file to upload
    :param dict **kwargs: Optional kwargs to pass to upload_file
    :return: Results of upload_file
    :rtype: Optional[Union[list, dict]]
    """
    file = Path(file_path)
    if file_name is None:
        file_name = file.name
    if not file.exists():
        logger.error(f"File {file_path} does not exist.")
        return
    if file.suffix == ".xml":
        return process_base64_in_xml(regscale_id, regscale_module, file_path, **kwargs)
    filestring = encode_file_to_base64(file_path)
    return upload_file(
        ssp_id=regscale_id,
        parent_module=regscale_module,
        file_path=file_path,
        filestring=filestring,
        filename=file_name,
        **kwargs,
    )


def upload_file(
    ssp_id: int,
    parent_module: str,
    file_path: str,
    filestring: str,
    filename: str,
    **kwargs: dict,
) -> Union[dict, bool]:
    """Upload file to RegScale

    :param int ssp_id: RegScale ID
    :param str parent_module: RegScale module
    :param str file_path: Path to file
    :param str filestring: Base64-encoded file
    :param str filename: Name of file to upload
    :param dict **kwargs: Optional kwargs to pass to upload_file
    :return: Results of upload_file, or False if upload fails
    :rtype: Union[dict, bool]
    """
    logger.info(f"Uploading {filename} to RegScale {parent_module} with ID {ssp_id}.")
    if "api" not in kwargs:
        api = Api()
        kwargs["api"] = api
    decoded_file = decode_base64_to_bytesio(filestring)
    try:
        results = File.upload_file_to_regscale(
            file_name=filename or file_path,
            parent_id=ssp_id,
            parent_module=parent_module,
            file_data=decoded_file.getvalue(),
            **kwargs,
        )
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return False
    logger.info(f"File {filename} uploaded successfully.")
    return results


def process_base64_in_xml(
    regscale_id: int,
    regscale_module: str,
    file_path: str,
    file_name: str = None,
    **kwargs: dict,
) -> list:
    """Process base64 in XML file

    :param int regscale_id: RegScale ID
    :param str regscale_module: RegScale module
    :param str file_path: Path to XML file
    :param str file_name: Optional name of file to upload
    :param dict **kwargs: Optional kwargs to pass to upload_file
    :return: Results of upload_file
    :rtype: list
    """
    results = []
    base64_tags = process_base64_tags_in_xml(file_path)
    for base64_tag in base64_tags:
        filename = base64_tag["filename"]
        filestring = base64_tag["base64"]
        logger.info(f"Uploading base64-tagged file {filename} to RegScale {regscale_module} with ID {regscale_id}.")
        result = upload_file(
            ssp_id=regscale_id,
            parent_module=regscale_module,
            file_path=filename,
            filestring=filestring,
            filename=filename,
            **kwargs,
        )
        results.append(result)
    logger.info(f"Uploading XML file {file_path} to RegScale {regscale_module} with ID {regscale_id}.")
    result = upload_file(
        ssp_id=regscale_id,
        parent_module=regscale_module,
        file_path=file_name or file_path,
        filestring=encode_file_to_base64(file_path),
        filename=file_name or file_path,
        **kwargs,
    )
    results.append(result)
    return results


def process_base64_tags_in_xml(xml_file: str) -> list[dict]:
    """Process base64 tags in XML file

    :param str xml_file: Path to XML file
    :return: List of dicts containing filename and base64 string
    :rtype: list[dict]
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    results = []
    for base64_tag in root.iter("base64"):
        filename = base64_tag.attrib["filename"]
        filestring = base64_tag.text.replace("\n", "")
        results.append({"filename": filename, "base64": filestring})
    return results
