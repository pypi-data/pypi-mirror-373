#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Azure InTune Integration"""
import json
import logging
import re
from datetime import datetime, timedelta
from time import sleep
from typing import Iterator, Optional

import click
import requests
import rich.progress

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.api_handler import APIHandler
from regscale.core.app.utils.app_utils import create_progress_object, error_and_exit
from regscale.core.app.utils.regscale_utils import verify_provided_module
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding
from regscale.models import Asset, Sbom, regscale_id, regscale_models, regscale_module
from regscale.models.integration_models.sbom.cyclone_dx import CycloneDXJsonGenerator
from regscale.validation.record import validate_regscale_object


@click.group()
def intune():
    """Microsoft Azure InTune Integrations"""


@intune.command(name="sync_intune")
@regscale_id()
@regscale_module()
def sync_intune(regscale_id: int, regscale_module: str):
    """Sync Intune Alerts with RegScale Assets."""

    from regscale.integrations.commercial.azure.scanner import IntuneIntegration

    verify_provided_module(regscale_module)
    try:
        assert validate_regscale_object(parent_id=regscale_id, parent_module=regscale_module)
    except AssertionError:
        error_and_exit(
            "This RegScale object does not exist. Please check your RegScale Parent ID \
                     and Module."
        )
    access_token = get_access_token(config=Application().config)
    api = Api()

    with create_progress_object() as device_progress:
        device_task = device_progress.add_task("[#f68d1f]Fetching Device List...", total=1)
        software_task = device_progress.add_task("[#1f96f6]Updating Software List...")
        devices = get_device_list(api=api, access_token=access_token, device_progress=device_progress, task=device_task)
        device_progress.update(task_id=software_task, total=len(devices))
        for dev in devices:
            full_data = get_device_data_by_device(api=api, access_token=access_token, device_id=dev.get("id"))
            detected_apps = full_data.get("detectedApps")
            if detected_apps:
                dev["detectedApps"] = detected_apps
            device_progress.update(task_id=software_task, advance=1)

    if devices:
        in_scan = IntuneIntegration(plan_id=regscale_id)
        in_scan.sync_assets(
            plan_id=regscale_id,
            asset_num=len(devices),
            integration_assets=fetch_intune_assets(
                regscale_parent_id=regscale_id,
                regscale_module=regscale_module,
                devices=devices,
                access_token=access_token,
            ),
        )
        in_scan.sync_findings(
            plan_id=regscale_id,
            finding_count=len(devices),
            integration_findings=fetch_intune_findings(devices=devices),
        )
    else:
        click.echo("No devices found.")

    update_sbom(devices=devices, parent_id=regscale_id, parent_module=regscale_module)


def check_if_phone(device: dict) -> Optional[str]:
    """
    Check if the device is a phone or tablet

    :param dict device: The device dictionary
    :return: The device type
    :rtype: Optional[str]
    """

    if "iphone" in device["operatingSystem"].lower():
        return "Phone"
    if "android" in device["operatingSystem"].lower():
        return "Phone"
    if "ipad" in device["operatingSystem"].lower():
        return "Tablet"
    return None


def determine_asset_type(device: dict) -> str:
    """
    Determine the asset type

    :param dict device: The device dictionary
    :return: The asset type
    :rtype: str
    """
    asset_type = check_if_phone(device)
    if not asset_type:
        if device.get("operatingSystem", "").lower() in ["macmdm", "windows", "linux", "macOS"]:
            if device.get("model") and "vm" in device.get("model", "").lower():
                asset_type = "Virtual Machine"
            else:
                asset_type = "Laptop"
        else:
            asset_type = "Virtual Machine"
    return asset_type


def fetch_intune_assets(
    regscale_parent_id: int,
    regscale_module: str,
    devices: list[dict],
    access_token: str,
) -> Iterator[IntegrationAsset]:
    """
    Fetch InTune Assets

    :param int regscale_parent_id: RegScale Parent ID
    :param str regscale_module: RegScale Module
    :param list[dict] devices: The list of devices
    :param str access_token: The access token
    :yields: IntegrationAsset
    :rtype: Iterator[IntegrationAsset]
    """
    api = Api()
    logger = logging.getLogger("regscale")
    config = api.config

    context = {
        "regscale_parent_id": regscale_parent_id,
        "regscale_module": regscale_module,
        "api": api,
        "access_token": access_token,
        "config": config,
        "logger": logger,
    }

    for device in devices:
        try:
            asset = create_asset(device=device, context=context)
            if asset:
                yield asset
        except Exception as e:
            logger.error(f"Error creating asset for device {device.get('deviceName')}: {e}")


def fetch_intune_findings(devices: list[dict]) -> Iterator[IntegrationFinding]:
    """
    Fetch InTune Assets

    :param list[dict] devices: The list of devices
    :yields: IntegrationAsset
    :rtype: Iterator[IntegrationFinding]
    """
    logger = logging.getLogger("regscale")

    for device in devices:
        try:
            if asset := create_finding(device=device):
                yield asset
        except Exception as e:
            logger.error(f"Error creating asset for device {device.get('deviceName')}: {e}")


def create_finding(device: dict) -> Optional[IntegrationFinding]:
    """
    Create an asset from the device dictionary

    :param dict device: The device dictionary
    :return: The finding
    :rtype: Optional[IntegrationFinding]
    """

    compliance = device.get("complianceState") == "compliant"
    if not compliance:
        # Create a finding
        control_labels = []
        title = ""
        category = ""
        plugin_name = "Intune compliance"
        severity = regscale_models.IssueSeverity.High
        description = "Intune Compliance Failure"
        status = regscale_models.IssueStatus.Open
        asset_id = device.get("azureADDeviceId")
        return IntegrationFinding(
            control_labels=control_labels,
            title=title,
            category=category,
            plugin_name=plugin_name,
            severity=severity,
            description=description,
            status=status,
            asset_identifier=asset_id,
        )
    return None


def create_asset(device: dict, context: dict) -> Optional[IntegrationAsset]:
    """
    Create an asset from the device dictionary

    :param dict device: The device dictionary
    :param dict context: The context dictionary containing regscale_parent_id, regscale_module, config, and logger
    :return: The asset
    :rtype: Optional[IntegrationAsset]
    """
    regscale_parent_id = context["regscale_parent_id"]
    regscale_module = context["regscale_module"]
    config = context["config"]
    logger = context["logger"]

    software_list = [
        {"name": app.get("displayName"), "version": app.get("version")} for app in device.get("detectedApps", [])
    ]

    compliance = device.get("complianceState") == "compliant"
    if device.get("lastSyncDateTime"):
        last_sign_in = datetime.strptime(device["lastSyncDateTime"], "%Y-%m-%dT%H:%M:%SZ")
        status = "Active (On-Network)" if determine_if_recent(last_sign_in) or compliance else "Off-Network"
    else:
        status = "Off-Network"
    asset_type = determine_asset_type(device)
    ips = device.get("hardwareInformation", {}).get("wiredIPv4Addresses", [])

    try:
        return IntegrationAsset(
            name=device.get("deviceName"),
            other_tracking_number=device.get("azureADDeviceId"),
            azure_identifier=device.get("azureADDeviceId"),
            identifier=device.get("azureADDeviceId"),
            parent_id=regscale_parent_id,
            parent_module=regscale_module,
            manufacturer=device.get("manufacturer"),
            model=device["model"],
            operating_system=device.get("operatingSystem"),
            asset_owner_id=config["userId"],
            asset_type=asset_type if asset_type else "Other",
            asset_category=regscale_models.AssetCategory.Hardware,
            status=status,
            notes=f"<p>isCompliant: <strong>{compliance}</strong><br>isEncrypted: "
            + f"<strong>{device['isEncrypted']}</strong><br>isRooted: <strong>"
            + f"{device['jailBroken']}</strong><br>lastSyncDateTime: <strong>"
            + f"{device['lastSyncDateTime']}</strong>",
            mac_address=convert_str_to_mac(device.get("wiFiMacAddress") or device.get("ethernetMacAddress")),
            serial_number=device.get("serialNumber") or device.get("hardwareInformation", {}).get("serialNumber"),
            os_version=device.get("osVersion"),
            software_inventory=software_list,
            ip_address=", ".join(ips),
        )
    except KeyError as e:
        logger.error(f"Error creating asset: {e}")
    return None


def get_access_token(config: dict) -> str:
    """
    Authenticate and return an access token.

    :param dict config: The configuration dictionary
    :return: The access token
    :rtype: str
    """
    import msal

    authority = f"https://login.microsoftonline.com/{config.get('azureCloudTenantId')}"
    scope = ["https://graph.microsoft.com/.default"]

    app = msal.ConfidentialClientApplication(
        client_id=config.get("azureCloudClientId"),
        client_credential=config.get("azureCloudSecret"),
        authority=authority,
    )
    result = app.acquire_token_for_client(scopes=scope)

    if "access_token" in result:
        return result["access_token"]

    error_and_exit(f"Error acquiring token: {result.get('error')}")


def get_device_list(
    api: Api, access_token: str, device_progress: rich.progress.Progress, task: rich.progress.TaskID
) -> list[dict]:
    """
    Retrieve device data from Microsoft Intune.

    :param Api api: The API object
    :param str access_token: The access token
    :param rich.progress.Progress job_progress: The job progress object
    :param rich.progress.TaskID task: The task ID
    :return: The device data
    :rtype: list[dict]
    """
    url = "https://graph.microsoft.com/beta/deviceManagement/managedDevices?$expand=detectedApps"
    headers = {"Authorization": f"Bearer {access_token}"}
    devices = []

    # Pagination to retrieve all devices
    while url:
        response = backoff_retry(api=api, url=url, headers=headers)
        count = response.json().get("@odata.count")
        if count:
            device_progress.update(task_id=task, total=count)
        if response.status_code == 200:
            data = response.json()
            devices.extend(data["value"])
            device_progress.update(task_id=task, advance=len(response.json().get("value", [])))
            url = data.get("@odata.nextLink")  # Check for pagination
        else:
            error_and_exit(f"Error retrieving device data: {response.status_code}\n{response.text}")

    return devices


def get_device_data_by_device(api: Api, access_token: str, device_id: str) -> dict:
    """
    Retrieve device data from Microsoft Intune.

    :param Api api: The API object
    :param str access_token: The access token
    :param str device_id: The device ID
    :return: The device data
    :rtype: dict
    """
    url = f"https://graph.microsoft.com/beta/deviceManagement/managedDevices/{device_id}?$expand=detectedApps"
    headers = {"Authorization": f"Bearer {access_token}"}

    # Pagination to retrieve all devices
    response = backoff_retry(api=api, url=url, headers=headers)
    data = {}
    if response.status_code == 200:
        data = response.json()
    else:
        error_and_exit(f"Error retrieving device data: {response.status_code}\n{response.text}")
    return data


def update_sbom_for_device(args: tuple):
    """
    Update the SBOM for a device

    :args: tuple containing the asset ID, device dictionary, progress object, and task ID
    :rtype: None
    :return: None
    """
    regscale_version, fix_version, asset_id, device, progress_object, progress_task, logger = args
    components = []
    generator = CycloneDXJsonGenerator(device=device, logger=logger)
    for app in device.get("detectedApps", []):
        display_name = app.get("displayName")
        version = app.get("version") or "Unknown"
        app_type = "application"
        if display_name:
            component = {
                "type": app_type,
                "name": display_name,
                "version": version,
            }
            components.append(component)
    sbom = Sbom(
        tool=device.get("deviceName"),
        parentId=asset_id,
        parentModule="assets",
        name=device.get("deviceName"),
        standardVersion=device.get("osVersion"),
        results=json.dumps(generator.generate_sbom(components=components)),
        sbomStandard="CycloneDX",
    )
    if regscale_version >= fix_version:
        sbom.create_or_update()
    else:
        # Create if not exist
        sbom.get_or_create()

    # sbom.create_or_update()
    progress_object.update(task_id=progress_task, advance=len(device.get("detectedApps", [])))


def update_sbom(devices: list[dict], parent_id: int, parent_module: str):
    """
    Update the SBOM for devices

    :param list[dict] devices: The list of devices
    :param int parent_id: The parent ID
    :param str parent_module: The parent module
    :rtype: None
    :return: None
    """
    app = Application()
    existing_assets = Asset.get_all_by_parent(parent_id=parent_id, parent_module=parent_module)
    regscale_version = APIHandler().regscale_version
    fix_version = "6.9.0.4"
    if not re.match(r"^\d+\.\d+(\.\d+){0,2}$", regscale_version) or regscale_version < fix_version:
        app.logger.warning(
            "SBOM functionality is limited and unable to update SBOM, please update to the latest "
            "RegScale version to resolve."
        )
        return

    with create_progress_object() as sbom_progress:
        total_applications = sum(len(device.get("detectedApps", [])) for device in devices)
        sbom_task = sbom_progress.add_task("[#00ff00]Updating SBOM(s) in RegScale...", total=total_applications)
        for device in devices:
            matching_asset: Optional[Asset] = next(
                (asset for asset in existing_assets if asset.azureIdentifier == device.get("azureADDeviceId")), None
            )
            if matching_asset:
                app.thread_manager.submit_task(
                    func=update_sbom_for_device,
                    args=(
                        regscale_version,
                        fix_version,
                        matching_asset.id,
                        device,
                        sbom_progress,
                        sbom_task,
                        app.logger,
                    ),
                )
        _ = app.thread_manager.execute_and_verify()


def determine_if_recent(date: datetime, days: int = 7) -> bool:
    """
    Determine if a date is recent

    :param datetime date: The date to check
    :param int days: The number of days to consider recent
    :return: True if the date is recent, False otherwise
    :rtype: bool
    """
    # Using three days ago as the threshold
    days_ago = datetime.now() - timedelta(days=days)
    return date >= days_ago


def convert_str_to_mac(mac: str):
    """
    Convert a string to a MAC address

    :param str mac: The MAC address string
    :return: The MAC address
    :rtype: str
    """
    if mac:
        mac = mac.replace(":", "").replace("-", "").replace(".", "").replace(" ", "").upper()
        return ":".join(mac[i : i + 2] for i in range(0, 12, 2))
    return None


def backoff_retry(api: Api, url: str, headers: dict, max_retries: int = 5, backoff_factor: int = 2):
    """
    Perform a GET request with exponential backoff retry on HTTP 429.

    :param Api api: The API object
    :param str url: The URL to request
    :param dict headers: The request headers
    :param int max_retries: The maximum number of retries
    :param int backoff_factor: The backoff factor (multiplier for the delay)
    :return: The response object
    :rtype: requests.Response
    """
    retries = 0
    response = requests.Response()
    while retries < max_retries:
        response = api.get(url, headers=headers)
        if response.status_code == 429:
            retries += 1
            sleep_time = backoff_factor**retries
            print(f"Rate limited. Retrying in {sleep_time} seconds...")
            sleep(sleep_time)
        else:
            return response
    response.raise_for_status()
    return response
