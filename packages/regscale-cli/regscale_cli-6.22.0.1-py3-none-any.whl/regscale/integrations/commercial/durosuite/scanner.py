#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RegScale DuroSuite Package

This module provides functionality for integrating DuroSuite with RegScale,
including syncing findings, assets, and performing scans.
"""
import enum
import logging
import re
import tempfile
import time
from typing import Optional, List, Dict, Tuple

import click
from rich.progress import Progress

from regscale.core.lazy_group import LazyGroup
from regscale.integrations.commercial.durosuite import api
from regscale.integrations.commercial.durosuite.variables import DuroSuiteVariables
from regscale.integrations.commercial.stigv2.stig_integration import StigIntegration
from regscale.models import regscale_ssp_id

logger = logging.getLogger("regscale")


class DuroSuiteOS(enum.IntEnum):
    """
    Enum for Operating Systems
    """

    UBUNTU_20 = 7
    PALO_ALTO = 8


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "scan": "regscale.integrations.commercial.durosuite.scanner.scan",
        "import_audit": "regscale.integrations.commercial.durosuite.scanner.cli_import_audit",
    },
    name="durosuite",
)
def durosuite():
    """
    DuroSuite Integrations
    """
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stderr
    )


@durosuite.command(name="scan")
@regscale_ssp_id()
@click.option(
    "--ansible_user",
    type=str,
    required=True,
    help="Remote user name for device connection",
)
@click.option(
    "--ansible_ssh_pass",
    type=str,
    required=True,
    help="Remote user password for device connection",
)
@click.option(
    "--ansible_become_pass",
    type=str,
    required=True,
    help="Password for privilege escalation",
)
@click.option(
    "--device_name",
    type=str,
    default="Ubuntu Server",
    help="Name of the device to scan",
)
@click.option(
    "--os_id",
    type=int,
    default=7,
    help="ID of the operating system",
)
@click.option(
    "--log_level",
    type=str,
    default="INFO",
    help="Log level for the scan",
)
def scan(
    regscale_ssp_id: int,
    ansible_user: str,
    ansible_ssh_pass: str,
    ansible_become_pass: str,
    device_name: str,
    os_id: int,
    log_level: str,
):
    """
    Scan DuroSuite.

    This function initiates a scan in DuroSuite and syncs the results to RegScale.
    """
    import logging
    import sys

    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stderr
    )

    # Call durosuite_scan with the provided arguments
    durosuite_scan(
        host=device_name,
        os_id=os_id,
        regscale_ssp_id=regscale_ssp_id,
        ansible_user=ansible_user,
        ansible_ssh_pass=ansible_ssh_pass,
        ansible_become_pass=ansible_become_pass,
    )


@durosuite.command(name="import_audit")
@regscale_ssp_id()
@click.option(
    "-a",
    "--audit_id",
    type=click.INT,
    help="The ID of the DuroSuite audit to import",
    prompt="Enter DuroSuite Audit ID",
    required=True,
)
def cli_import_audit(audit_id: int, regscale_ssp_id: int) -> None:
    """
    Import a specific DuroSuite audit and sync it to RegScale.

    This function imports a specific audit from DuroSuite and syncs it to RegScale.

    :param int audit_id: The ID of the DuroSuite audit to import.
    :param int regscale_ssp_id: RegScale System Security Plan ID.
    """
    import_audit(audit_id, regscale_ssp_id)


def get_or_create_group(ds: api.DuroSuite, os_id: int, group_name: str = None) -> api.Group:
    """
    Get an existing group for the OS or create a new one.

    :param api.DuroSuite ds: DuroSuite client
    :param int os_id: Operating system ID
    :param str group_name: Optional group name, will be generated if not provided
    :return: Group object
    :rtype: api.Group
    :raises ValueError: If group creation fails
    """
    groups = [group for group in ds.get_groups() if group.os_id == os_id]
    if any(groups):
        return groups[0]

    if not group_name:
        # Get OS name from supported systems
        os_list = ds.get_supported_operating_systems()
        os_name = next((os["operating_system"] for os in os_list if os["id"] == os_id), f"OS-{os_id}")
        group_name = f"{os_name} Group"

    # Set required variables based on OS
    variables = {}
    if os_id == 7:  # Ubuntu 20.XX
        variables = {
            "ansible_user": DuroSuiteVariables.duroSuiteUser,
            "ansible_ssh_pass": DuroSuiteVariables.duroSuitePassword,
            # "ansible_become_pass": "",
            # "remote_server_variable": "",
            # "require_disk_encryption": False,
            # "space_left_variable": 250000,
            # "time_zone_variable": "UTC",
        }

    response = ds.add_new_group({"group_name": group_name, "os_id": os_id, "variables": variables})
    if not response:
        raise ValueError(f"Failed to create group for OS {os_id}")

    # Get the newly created group
    groups = [group for group in ds.get_groups() if group.os_id == os_id]
    if not any(groups):
        raise ValueError(f"Group was created but not found for OS {os_id}")
    return groups[0]


def get_or_create_template(ds: api.DuroSuite, playbook_id: int, os_id: int, group_id: int) -> api.Template:
    """
    Get an existing template for the OS or create a new one.

    :param api.DuroSuite ds: DuroSuite client
    :param int playbook_id: ID of the playbook
    :param int os_id: Operating system ID
    :param int group_id: Group ID
    :return: Template object
    :rtype: api.Template
    :raises ValueError: If template creation fails
    """
    try:
        # Get templates for the group
        templates = ds.get_template_ids_by_group(group_id)

        # Look for an existing template that matches our criteria
        for template in templates:
            if template.os_id == os_id and template.playbook_id == playbook_id:
                return template

        # If no matching template exists, create a new one
        template_name = f"Template_{playbook_id}_{time.strftime('%Y%m%d_%H%M%S')}"
        template = ds.create_template(name=template_name, os_id=os_id, playbook_id=playbook_id, group_id=group_id)
        if template:
            return template

        raise ValueError("Failed to create template")
    except Exception as e:
        raise ValueError(f"Failed to create template: {e}")


def _get_device_vars_for_os(
    os_id: int, host: str, ansible_user: str, ansible_ssh_pass: str, ansible_become_pass: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Get device variables based on OS type.

    :param int os_id: Operating system ID
    :param str host: Host IP or hostname
    :param str ansible_user: Remote user name
    :param str ansible_ssh_pass: Remote user password
    :param Optional[str] ansible_become_pass: Privilege escalation password
    :return: List of device variables
    :rtype: List[Dict[str, str]]
    """
    if os_id == DuroSuiteOS.UBUNTU_20:
        return [
            {"var_name": "ansible_host", "var_value": host},
            {"var_name": "ansible_user", "var_value": ansible_user},
            {"var_name": "ansible_ssh_pass", "var_value": ansible_ssh_pass},
            {"var_name": "ansible_become_pass", "var_value": ansible_become_pass},
        ]
    elif os_id == DuroSuiteOS.PALO_ALTO:
        return [
            {"var_name": "ansible_host", "var_value": host},
            {"var_name": "pan_username", "var_value": ansible_user},
            {"var_name": "pan_password", "var_value": ansible_ssh_pass},
        ]
    return []


def _needs_device_update(
    device: api.Device, os_id: int, host: str, ansible_user: str, ansible_ssh_pass: str, ansible_become_pass: str
) -> Tuple[bool, List[Dict[str, str]]]:
    """
    Check if device needs variable updates.

    :param api.Device device: Device to check
    :param int os_id: Operating system ID
    :param str host: Host IP or hostname
    :param str ansible_user: Remote user name
    :param str ansible_ssh_pass: Remote user password
    :param str ansible_become_pass: Privilege escalation password
    :return: Tuple of (needs_update, vars_to_update)
    :rtype: Tuple[bool, List[Dict[str, str]]]
    """
    device_vars = {var.name: var.value for var in device.device_vars} if device.device_vars else {}

    if os_id == DuroSuiteOS.UBUNTU_20:
        if (
            device_vars.get("ansible_host") != host
            or device_vars.get("ansible_user") != ansible_user
            or device_vars.get("ansible_ssh_pass") != ansible_ssh_pass
            or device_vars.get("ansible_become_pass") != ansible_become_pass
        ):
            return True, _get_device_vars_for_os(os_id, host, ansible_user, ansible_ssh_pass, ansible_become_pass)
    elif os_id == DuroSuiteOS.PALO_ALTO:
        if (
            device_vars.get("ansible_host") != host
            or device_vars.get("pan_username") != ansible_user
            or device_vars.get("pan_password") != ansible_ssh_pass
        ):
            return True, _get_device_vars_for_os(os_id, host, ansible_user, ansible_ssh_pass)

    return False, []


def _find_matching_device(
    devices: List[api.Device], device_name: str, os_id: int, group_id: int
) -> Optional[api.Device]:
    """
    Find a matching device from the list.

    :param List[api.Device] devices: List of devices to search
    :param str device_name: Name of the device to find
    :param int os_id: Operating system ID
    :param int group_id: Group ID
    :return: Matching device or None
    :rtype: Optional[api.Device]
    """
    for device in devices:
        if device.name == device_name and device.os_id == os_id and any(g.id == group_id for g in device.groups):
            return device
    return None


def get_or_create_device(
    ds: api.DuroSuite,
    device_name: str,
    os_id: int,
    group_id: int,
    host: str,
    ansible_user: str,
    ansible_ssh_pass: str,
    ansible_become_pass: str,
) -> api.Device:
    """
    Get an existing device or create a new one.

    :param api.DuroSuite ds: DuroSuite client
    :param str device_name: Name of the device
    :param int os_id: Operating system ID
    :param int group_id: Group ID
    :param str host: Host IP or hostname
    :param str ansible_user: Remote user name
    :param str ansible_ssh_pass: Remote user password
    :param str ansible_become_pass: Privilege escalation password
    :return: Device object
    :rtype: api.Device
    :raises ValueError: If device creation fails
    """
    # First try to find an existing device
    devices = ds.get_devices()
    if devices:
        if device := _find_matching_device(devices, device_name, os_id, group_id):
            # Check if device needs updates
            needs_update, vars_to_update = _needs_device_update(
                device, os_id, host, ansible_user, ansible_ssh_pass, ansible_become_pass
            )
            if needs_update:
                ds.update_device_vars(device.id, vars_to_update)
            return device

    # If no device exists, create a new one
    try:
        device_vars = _get_device_vars_for_os(os_id, host, ansible_user, ansible_ssh_pass, ansible_become_pass)
        device_data = {"name": device_name, "os_id": os_id, "group_id": group_id, "device_vars": device_vars}
        device = ds.add_new_device(device_data)
        if device:
            return device
    except Exception as e:
        logger.error(f"Failed to create device: {e}")
        raise ValueError(f"Failed to create device: {e}")

    raise ValueError("Failed to create device")


def get_stigs(ds: api.DuroSuite, os_id: int) -> list:
    """
    Get STIGs for the given OS.

    :param DuroSuite ds: DuroSuite API client.
    :param int os_id: ID of the operating system.

    :return: List of STIGs.
    :rtype: list
    """
    try:
        stigs = ds.get_stigs_by_os_id(os_id=os_id)
        return stigs
    except Exception as e:
        logger.error(f"Failed to get STIGs: {e}")
        raise ValueError(f"Failed to get STIGs: {e}")


def _wait_for_audit_completion(ds: api.DuroSuite, audit_id: int) -> None:
    """
    Wait for an audit to complete or fail.

    :param api.DuroSuite ds: DuroSuite client
    :param int audit_id: ID of the audit to monitor
    :raises ValueError: If audit fails or is cancelled
    :raises TimeoutError: If audit times out
    """
    max_retries = 30  # 5 minutes total
    retry_count = 0
    while retry_count < max_retries:
        audit_status = ds.get_audit_status(audit_id)
        if not audit_status:
            logger.error("Failed to get audit status")
            break

        status = audit_status.status.lower() if audit_status.status else "unknown"
        logger.info(f"Audit status: {status}")

        if status.startswith("complete"):
            logger.info("Audit completed successfully")
            return
        elif status.startswith("fail"):
            error_msg = audit_status.error_message or "Unknown error"
            logger.error(f"Audit failed: {error_msg}")
            raise ValueError(f"Audit failed: {error_msg}")
        elif status.startswith("cancel"):
            logger.error("Audit was cancelled")
            raise ValueError("Audit was cancelled")

        time.sleep(10)  # Wait 10 seconds before checking again
        retry_count += 1

    if retry_count >= max_retries:
        raise TimeoutError("Audit timed out")


def durosuite_scan(
    host: str,
    os_id: int,
    regscale_ssp_id: int,
    ansible_user: str,
    ansible_ssh_pass: str,
    ansible_become_pass: str,
    device_name: Optional[str] = None,
    progress: Optional[Progress] = None,
) -> None:
    """
    Perform a DuroSuite scan and import the results to RegScale.

    :param str host: Name of the device to scan
    :param int os_id: ID of the operating system
    :param int regscale_ssp_id: RegScale System Security Plan ID
    :param str ansible_user: Remote user name for device connection
    :param str ansible_ssh_pass: Remote user password for device connection
    :param str ansible_become_pass: Password for privilege escalation
    :param Optional[str] device_name: Optional name of the device
    :param Optional[Progress] progress: Optional progress object to use instead of creating a new one
    """
    # Get DuroSuite variables from init.yaml
    base_url = DuroSuiteVariables.duroSuiteURL
    username = DuroSuiteVariables.duroSuiteUser
    password = DuroSuiteVariables.duroSuitePassword

    # Determine if the host is an IP address or a FQDN
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        device_ip = host
    else:
        device_ip = None
        device_name = host

    # Initialize DuroSuite API client with DuroSuite API credentials
    ds = api.DuroSuite(base_url, username, password)

    try:
        # Initialize DuroSuite client
        ds.login(username, password)
        logger.debug("DuroSuite API client initialized")

        # Get or create group
        group = get_or_create_group(ds, os_id)
        if not group:
            logger.error("Failed to get or create group")
            raise ValueError("Failed to get or create group")

        logger.info(f"Using group: {group}")

        # Create device
        device = get_or_create_device(
            ds,
            host,
            os_id,
            group.id,
            host,
            ansible_user,
            ansible_ssh_pass,
            ansible_become_pass,
        )
        logger.info(f"Device created: {host}")

        # Get STIG
        stigs = get_stigs(ds, os_id)

        # Get or create template
        template = get_or_create_template(ds, stigs[0].id, os_id, group.id)
        if not template:
            logger.error("Failed to get or create template")
            raise ValueError("Failed to get or create template")
        logger.info(f"Template: {template}")

        # Start audit
        audit = ds.audit_device(device.id, group.id, stigs[0].id, template.id)
        if not audit:
            logger.error("Failed to start audit")
            raise ValueError("Failed to start audit")
        logger.info(f"Started audit: {audit}")

        # Wait for audit completion and import results
        try:
            _wait_for_audit_completion(ds, audit.audit_id)
            import_audit(
                audit.audit_id, regscale_ssp_id, progress=progress, device_name=device_name, device_ip=device_ip
            )
            logger.info(f"Successfully imported audit {audit.audit_id} to RegScale SSP {regscale_ssp_id}")
        except Exception as e:
            logger.error(f"Failed to import audit results: {e}")
            raise

    except Exception as e:
        logger.error(f"Failed to scan device: {e}")
        raise


def _wait_for_audit_completion_and_checklist(ds: api.DuroSuite, audit_id: int) -> str:
    """
    Wait for audit completion and retrieve the checklist file.

    :param api.DuroSuite ds: DuroSuite client
    :param int audit_id: The ID of the audit
    :return: The checklist file content
    :rtype: str
    :raises TimeoutError: If waiting for checklist times out
    """
    # Wait for the audit to complete
    finished = False
    while not finished:
        response = ds.get_audit_record(audit_id=audit_id)
        if response:
            logger.info(f"Audit Status for {audit_id}: {response['status']}")
            if response["status"].lower() == "complete":
                finished = True
        time.sleep(5)

    # Retrieve the checklist file
    checklist_file: Optional[str] = None
    attempts = 0
    max_attempts = 12  # 1 minute total wait time
    while not checklist_file and attempts < max_attempts:
        logger.info(f"Waiting for checklist file for {audit_id}")
        checklist_file = ds.get_checklist_file_by_audit_id(audit_id)
        time.sleep(5)
        attempts += 1

    if not checklist_file:
        raise TimeoutError(f"Timed out waiting for checklist file for audit {audit_id}")

    return checklist_file


def _update_xml_element(asset: "ET.Element", element_name: str, value: str) -> None:
    """
    Update or create an XML element with the given value.

    :param ET.Element asset: The asset element to update
    :param str element_name: Name of the element to update
    :param str value: Value to set
    """
    element = asset.find(element_name)
    if element is not None:
        if not element.text:
            element.text = value
    else:
        element = ET.SubElement(asset, element_name)
        element.text = value


def _update_checklist_device_info(checklist_content: str, device_name: Optional[str], device_ip: Optional[str]) -> str:
    """
    Update the checklist XML with device information.

    :param str checklist_content: Original checklist content
    :param Optional[str] device_name: Device name to add
    :param Optional[str] device_ip: Device IP to add
    :return: Updated checklist content
    :rtype: str
    """
    if not (device_name or device_ip):
        return checklist_content

    import xml.etree.ElementTree as ET

    root = ET.fromstring(checklist_content)
    asset = root.find(".//ASSET")

    if asset is not None:
        if device_name:
            _update_xml_element(asset, "HOST_NAME", device_name)

        if device_ip:
            _update_xml_element(asset, "HOST_IP", device_ip)
            # If no FQDN is set, generate one from the IP
            _update_xml_element(asset, "HOST_FQDN", device_ip)

    return ET.tostring(root, encoding="unicode")


def import_audit(
    audit_id: int,
    regscale_ssp_id: int,
    progress: Optional[Progress] = None,
    device_name: Optional[str] = None,
    device_ip: Optional[str] = None,
) -> None:
    """
    Import a DuroSuite audit and sync it to RegScale.

    :param int audit_id: The ID of the audit to import.
    :param int regscale_ssp_id: The ID of the RegScale SSP.
    :param Optional[Progress] progress: Optional progress object to use instead of creating a new one
    :param Optional[str] device_name: The name of the device
    :param Optional[str] device_ip: The IP address of the device
    """
    # Get DuroSuite credentials from init.yaml
    base_url = DuroSuiteVariables.duroSuiteURL
    username = DuroSuiteVariables.duroSuiteUser
    password = DuroSuiteVariables.duroSuitePassword

    ds = api.DuroSuite(base_url, username, password)

    try:
        # Wait for audit completion and get checklist
        checklist_content = _wait_for_audit_completion_and_checklist(ds, audit_id)

        # Update checklist with device information if provided
        checklist_content = _update_checklist_device_info(checklist_content, device_name, device_ip)

        logger.info(f"Processed checklist file for audit {audit_id}")

        # Process the checklist file
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".ckl", delete=True) as tmp_file:
            tmp_file.write(checklist_content)
            tmp_file_path = tmp_file.name

            # Sync the assets and findings
            StigIntegration.sync_assets(plan_id=regscale_ssp_id, path=tmp_file_path, progress=progress)  # type: ignore
            StigIntegration.sync_findings(plan_id=regscale_ssp_id, path=tmp_file_path, progress=progress)  # type: ignore

    except Exception as e:
        logger.error(f"Failed to import audit: {e}")
        raise
