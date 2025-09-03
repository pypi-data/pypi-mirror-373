#!/usr/bin/python
"""Script to parse a .xlsx file and load the inventory into RegScale as assets"""

import json
import os
import re
from datetime import datetime
from json import JSONDecodeError
from typing import Any, Dict, List, Optional, Union, Literal

import rich.progress

from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import create_logger, create_progress_object, check_file_path
from regscale.core.utils.date import date_str
from regscale.models import Asset, ImportValidater, Property

api = Api()
config = api.config
SOFTWARE_VENDOR = "Software/ Database Vendor"
SOFTWARE_NAME = "Software/ Database Name & Version"
PATCH_LEVEL = "Patch Level"
HARDWARE_MAKE = "Hardware Make/Model"
MAC_ADDRESS = "MAC Address"
OS_NAME = "OS Name and Version"
fmt = "%Y-%m-%d %H:%M:%S"
UNIQUE_ASSET_IDENTIFIER = "UNIQUE ASSET IDENTIFIER"
NETBIOS_NAME = "NetBIOS Name"
BASELINE_CONFIGURATION_NAME = "Baseline Configuration Name"
SERIAL_NUMBER = "Serial #/Asset Tag#"
DNS_NAME = "DNS Name or URL"
AUTHENTICATED_SCAN = "Authenticated Scan"
IN_LATEST_SCAN = "In Latest Scan"
IPV4_OR_IPV6_ADDRESS = "IPv4 or IPv6\nAddress"
ASSET_TYPE = "Asset Type"
VLAN_NETWORK_ID = "VLAN/\nNetwork ID"
FUNCTION = "Function"


def check_text(text: Optional[str] = None) -> str:
    """
    Check for NULL values and return empty string if NULL
    :param Optional[str] text: string to check if it is NULL, defaults to None
    :return: empty string if NULL, otherwise the string
    :rtype: str
    """
    return str(text or "")


def save_to_json(file_name: str, data: Any) -> None:
    """
    Save the data to a JSON file
    :param str file_name: name of the file to save
    :param Any data: data to save to the file
    :rtype: None
    """
    if not data:
        return
    if isinstance(data, list) and isinstance(data[0], Asset):
        lst = []
        for item in data:
            lst.append(item.dict())
        data = lst

    elif not isinstance(data, str):
        lst = []
        for key, value in data.items():
            lst.append(data[key]["asset"].dict())
        data = lst

    if file_name.endswith(".json"):
        file_name = file_name[:-5]
    with open(f"{file_name}.json", "w") as outfile:
        outfile.write(json.dumps(data, indent=4))


def map_str_to_bool(value: Optional[Union[bool, str]] = None) -> bool:
    """
    Map a string to a boolean value
    :param Optional[Union[bool, str]] value: string or bool value to map to a bool, defaults to False
    :return: boolean value
    :rtype: bool
    """
    import math

    if isinstance(value, bool):
        return value
    if isinstance(value, float) and math.isnan(value):
        return False
    if value.lower() in ["yes", "true"]:
        return True
    elif value.lower() in ["no", "false"]:
        return False
    else:
        return False


def determine_ip_address_version(ip_address: Optional[str] = None) -> Optional[str]:
    """
    Determine if the IP address is IPv4 or IPv6
    :param Optional[str] ip_address: IP address to check, defaults to None
    :return: Key for the IP address version in the asset object
    :rtype: Optional[str]
    """
    if not isinstance(ip_address, str) or not ip_address:
        return None
    ip_address = ip_address.strip()

    # IPv4 pattern - matches numbers 1-255 for first octet and 0-255 for remaining octets
    ipv4_pattern = (
        r"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])\."  # First octet: 1-255
        r"(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\."  # Second octet: 0-255
        r"(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\."  # Third octet: 0-255
        r"(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9]))$"  # Fourth octet: 0-255
    )

    # IPv6 pattern - handles all valid IPv6 formats including compressed notation
    ipv6_pattern = (
        r"^(?:"
        r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|"
        r"(?:[0-9a-fA-F]{1,4}:){1,7}:|"
        r"(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"
        r"(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|"
        r"(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|"
        r"(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|"
        r"(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|"
        r"[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|"
        r":(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|"
        r"fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]+|"
        r"::(?:ffff(?::0{1,4})?:)?(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)"
        r"\.(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)"
        r"\.(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)"
        r"\.(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)|"
        r"(?:[0-9a-fA-F]{1,4}:){1,4}:"
        r"(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)"
        r"\.(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)"
        r"\.(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)"
        r"\.(?:25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)"
        r")$"
    )

    # Check for IPv4
    try:
        if re.fullmatch(ipv4_pattern, ip_address):
            return "ipAddress"
        # Check for IPv6
        elif re.fullmatch(ipv6_pattern, ip_address):
            return "iPv6Address"
        else:
            return None
    except Exception:
        return None


def determine_asset_category(inventory: dict, mapping: "ImportValidater.mapping") -> str:
    """
    Determine the asset category based on the inventory item
    :param dict inventory: inventory item to parse & determine the asset category
    :param ImportValidater.mapping mapping: Mapping object to use for mapping
    :return: asset category of Hardware, Software, or Unknown
    :rtype: str
    """
    software_fields = [
        check_text(mapping.get_value(inventory, SOFTWARE_VENDOR)),
        check_text(mapping.get_value(inventory, SOFTWARE_NAME)),
        check_text(mapping.get_value(inventory, PATCH_LEVEL)),
    ]
    hardware_fields = [
        check_text(mapping.get_value(inventory, HARDWARE_MAKE)),
        check_text(mapping.get_value(inventory, MAC_ADDRESS)),
        check_text(mapping.get_value(inventory, OS_NAME)),
    ]
    software_set = set(software_fields)
    hardware_set = set(hardware_fields)
    if len(hardware_set) > len(software_set):
        return "Hardware"
    if len(software_set) > len(hardware_set):
        return "Software"
    return "Unknown"


def map_inventory_to_asset(
    inventory: dict, parent_id: int, parent_module: str, mapping: "ImportValidater.mapping"
) -> Optional[Asset]:
    """
    Map the inventory to a RegScale asset
    :param dict inventory: inventory item to map to a RegScale asset
    :param int parent_id: RegScale Record ID to use as parentId
    :param str parent_module: RegScale Module to use as parentModule
    :param ImportValidater.mapping mapping: Mapping object to use for mapping
    :return: RegScale asset, if it has a unique identifier or DNS name
    :rtype: Optional[Asset]
    """
    # create a new asset
    asset_category = determine_asset_category(inventory, mapping)
    if asset_name := check_text(mapping.get_value(inventory, UNIQUE_ASSET_IDENTIFIER)) or check_text(
        mapping.get_value(inventory, DNS_NAME)
    ):
        new_asset = {
            "id": 0,
            "isPublic": True,
            "uuid": "",
            "name": asset_name,
            "otherTrackingNumber": "",
            "serialNumber": check_text(mapping.get_value(inventory, SERIAL_NUMBER)),
            "macAddress": check_text(mapping.get_value(inventory, MAC_ADDRESS)),
            "manufacturer": "",
            "model": check_text(mapping.get_value(inventory, HARDWARE_MAKE)),
            "assetOwnerId": config["userId"],
            "systemAdministratorId": None,
            "operatingSystem": "",
            "osVersion": check_text(mapping.get_value(inventory, OS_NAME)),
            "assetType": check_text(mapping.get_value(inventory, ASSET_TYPE) or "Unknown"),
            "location": check_text(mapping.get_value(inventory, "Location")),
            "cmmcAssetType": "",
            "cpu": 0,
            "ram": 0,
            "diskStorage": 0,
            "description": "",
            "endOfLifeDate": date_str(mapping.get_value(inventory, "End-of-Life ", "")),
            "purchaseDate": None,
            "status": "Active (On Network)",
            "wizId": "",
            "wizInfo": "",
            "notes": check_text(mapping.get_value(inventory, "Comments")),
            "softwareVendor": check_text(mapping.get_value(inventory, SOFTWARE_VENDOR)),
            "softwareVersion": check_text(mapping.get_value(inventory, SOFTWARE_NAME)),
            "softwareFunction": check_text(mapping.get_value(inventory, FUNCTION)),
            "patchLevel": check_text(mapping.get_value(inventory, PATCH_LEVEL)),
            "assetCategory": asset_category,
            "bVirtual": map_str_to_bool(mapping.get_value(inventory, "Virtual")),
            "bPublicFacing": map_str_to_bool(mapping.get_value(inventory, "Public")),
            "bAuthenticatedScan": map_str_to_bool(mapping.get_value(inventory, AUTHENTICATED_SCAN)),
            "bLatestScan": map_str_to_bool(mapping.get_value(inventory, IN_LATEST_SCAN)),
            "netBIOS": check_text(mapping.get_value(inventory, NETBIOS_NAME)),
            "baselineConfiguration": check_text(mapping.get_value(inventory, BASELINE_CONFIGURATION_NAME)),
            "fqdn": check_text(mapping.get_value(inventory, DNS_NAME)),
            "assetTagNumber": "",
            "vlanId": check_text(mapping.get_value(inventory, VLAN_NETWORK_ID)),
            "facilityId": None,
            "orgId": None,
            "parentId": parent_id,
            "parentModule": parent_module,
            "createdById": config["userId"],
            "dateCreated": datetime.now().strftime(fmt),
            "lastUpdatedById": config["userId"],
            "dateLastUpdated": datetime.now().strftime(fmt),
        }
    else:
        return None
    _update_ip_addresses(new_asset, inventory, mapping)
    if asset_category == "Hardware":
        new_asset["purpose"] = check_text(mapping.get_value(inventory, FUNCTION))
    elif asset_category == "Software":
        new_asset["softwareFunction"] = check_text(mapping.get_value(inventory, FUNCTION))
    return Asset(**new_asset)


def _update_ip_addresses(asset: dict, inventory: dict, mapping: "ImportValidater.mapping") -> None:
    """
    Update the IPv4 and IPv6 address fields for the provided asset

    :param dict asset: Asset to update
    :param dict inventory: Inventory item to parse
    :param ImportValidater.mapping mapping: Mapping object to use for mapping
    :rtype: None
    """
    if ip_address_data := check_text(mapping.get_value(inventory, IPV4_OR_IPV6_ADDRESS)):
        v6_addresses = []
        v4_addresses = []
        for ip_address in [addr.strip() for addr in re.split(r"\s*[;,]\s*|\n", ip_address_data) if addr.strip()]:
            if ipaddress_key := determine_ip_address_version(ip_address):
                if ipaddress_key == "iPv6Address":
                    v6_addresses.append(ip_address)
                else:
                    v4_addresses.append(ip_address)
        asset["ipAddress"] = ", ".join(v4_addresses) if v4_addresses else None
        asset["iPv6Address"] = ", ".join(v6_addresses) if v6_addresses else None


def create_properties(data: dict, parent_id: int, parent_module: str, progress: rich.progress.Progress) -> bool:
    """
    Create a list of properties and upload them to RegScale for the provided asset
    :param dict data: Dictionary of data to parse and create properties from
    :param int parent_id: ID to create properties for
    :param str parent_module: Parent module to create properties for
    :param rich.progress.Progress progress: Progress object used for batch creation
    :return: If batch update was successful
    :rtype: bool
    """
    import numpy as np  # Optimize import performance

    properties: list = []
    for key, value in data.items():
        # skip the item if the key is id or contains unnamed
        if "unnamed" in key.lower():
            continue
        # see if the value is datetime
        elif isinstance(value, datetime):
            value = value.strftime("%b %d, %Y")
        # see if the value is a boolean
        elif isinstance(value, np.bool_):
            value = str(value).title()
        regscale_property = Property(
            createdById=config["userId"],
            lastUpdatedById=config["userId"],
            key=key,
            value=value,
            parentId=parent_id,
            parentModule=parent_module,
        )
        properties.append(regscale_property)
    new_props = Property.batch_create(properties, progress_context=progress, remove_progress=True)
    create_logger().debug(f"Created {len(new_props)}/{len(properties)} properties for asset #{parent_id}")
    return new_props is not None


def validate_columns(file_path: str, version: Literal["rev4", "rev5", "4", "5"], sheet_name: str) -> ImportValidater:
    """
    Validate the columns in the inventory

    :param str file_path: path to the inventory .xlsx file
    :param Literal["rev4", "rev5", "4", "5"] version: FedRAMP version to import
    :param str sheet_name: sheet name in the inventory .xlsx file to validate
    :return: Import validator to facilitate header validation and custom mappings
    :rtype: ImportValidater
    """
    if "5" in version:
        expected_cols = [
            UNIQUE_ASSET_IDENTIFIER,
            IPV4_OR_IPV6_ADDRESS,
            "Virtual",
            "Public",
            DNS_NAME,
            NETBIOS_NAME,
            MAC_ADDRESS,
            AUTHENTICATED_SCAN,
            BASELINE_CONFIGURATION_NAME,
            OS_NAME,
            "Location",
            ASSET_TYPE,
            HARDWARE_MAKE,
            IN_LATEST_SCAN,
            SOFTWARE_VENDOR,
            SOFTWARE_NAME,
            PATCH_LEVEL,
            "Diagram Label",
            "Comments",
            SERIAL_NUMBER,
            VLAN_NETWORK_ID,
            "System Administrator/ Owner",
            "Application Administrator/ Owner",
            FUNCTION,
        ]
        mapping_dir = os.path.join("./", "mappings", "fedramp_inventory_rev5")
    else:
        expected_cols = [
            UNIQUE_ASSET_IDENTIFIER,
            IPV4_OR_IPV6_ADDRESS,
            "Virtual",
            "Public",
            DNS_NAME,
            NETBIOS_NAME,
            MAC_ADDRESS,
            AUTHENTICATED_SCAN,
            BASELINE_CONFIGURATION_NAME,
            OS_NAME,
            "Location",
            ASSET_TYPE,
            HARDWARE_MAKE,
            IN_LATEST_SCAN,
            SOFTWARE_VENDOR,
            SOFTWARE_NAME,
            PATCH_LEVEL,
            FUNCTION,
            "Comments",
            SERIAL_NUMBER,
            VLAN_NETWORK_ID,
            "System Administrator/ Owner",
            "Application Administrator/ Owner",
        ]
        mapping_dir = os.path.join("./", "mappings", "fedramp_inventory_rev4")
    return ImportValidater(
        required_headers=expected_cols,
        file_path=file_path,
        mapping_file_path=mapping_dir,
        disable_mapping=False,
        worksheet_name=sheet_name,
        skip_rows=2,
    )


def upload(
    inventory: str,
    record_id: int,
    module: str,
    version: Literal["rev4", "rev5", "4", "5"],
    sheet_name: str = "Inventory",
) -> None:
    """
    Main function to parse the inventory and load into RegScale
    :param str inventory: path to the inventory .xlsx file
    :param int record_id: RegScale Record ID to update
    :param str module: RegScale Module for the provided ID
    :param Literal["rev4", "rev5", "4", "5"] version: FedRAMP version to import
    :param str sheet_name: sheet name in the inventory .xlsx file to parse, defaults to "Inventory"
    :rtype: None
    """
    from regscale.exceptions.validation_exception import ValidationException

    logger = create_logger()

    try:
        import_validator = validate_columns(inventory, version, sheet_name)
        df = import_validator.data
    except FileNotFoundError:
        logger.error(f"[red]File not found: {inventory}")
        return
    except (ValueError, ValidationException) as e:
        logger.error(
            "There is an issue with the file: %s, please check the file and try again. Error: %s. Skipping...",
            inventory,
            e,
        )
        return

    # convert into dictionary
    inventory_json = df.to_json(orient="records")
    inventory_list = df.to_dict(orient="records")

    # save locally
    save_to_json("inventory.json", inventory_json)
    logger.info(f"[yellow]{len(inventory_list)} total inventory item(s) saved to inventory.json")

    # process the inventory
    inventory: Dict[int, Dict[str, Asset]] = {}
    existing_assets = Asset.get_all_by_parent(parent_id=record_id, parent_module=module)
    already_inserted: List[Asset] = []
    job_progress = create_progress_object()
    with job_progress as progress:
        process_task = progress.add_task("Processing inventory...", total=len(inventory_list))
        for inv in range(len(inventory_list)):
            asset = map_inventory_to_asset(inventory_list[inv], record_id, module, import_validator.mapping)
            if not asset:
                progress.update(process_task, advance=1)
                logger.warning(
                    f"[yellow]Skipping {inventory_list[inv]}, unable to determine Asset name from"
                    f" {UNIQUE_ASSET_IDENTIFIER} and {DNS_NAME}."
                )
                continue
            if asset not in existing_assets:
                inventory[inv] = {}
                inventory[inv]["asset"] = asset
                inventory[inv]["raw_data"] = inventory_list[inv]  # noqa
            else:
                already_inserted.append(asset)
            progress.update(process_task, advance=1)
    # reindex dict
    reindexed_dict = {new_index: inventory[old_index] for new_index, old_index in enumerate(inventory)}
    # print new objectives
    save_to_json("regscale-inventory", reindexed_dict)

    if not reindexed_dict:
        logger.warning("[yellow]No new inventory items to load, exiting...")
        return
    logger.info(
        f"[yellow]{len(reindexed_dict)} total inventory item(s) ready to load ({len(already_inserted)} "
        f"already exist(s)) Saved to regscale-inventory.json"
    )
    # loop through each asset in the inventory list
    processed = []
    failed = []
    with job_progress as progress:
        loading_task = progress.add_task("Loading inventory into RegScale...", total=len(reindexed_dict))
        for inv in reindexed_dict.values():
            try:
                res_data = inv["asset"].create()  # noqa
                processed.append(res_data)
                if not create_properties(inv["raw_data"], res_data["id"], "assets", progress):  # noqa
                    logger.error(
                        f"[red]Failed to create properties for asset #{res_data['id']}: {inv['asset']['name']}"  # noqa
                    )
            except JSONDecodeError:
                failed.append(inv)
                continue
            progress.update(loading_task, advance=1)

    if failed:
        save_to_json("failed-inventory", failed)
        logger.error(f"[red]{len(failed)} total inventory item(s) failed to load. Saved to failed-inventory.json")
    # print new objectives
    save_to_json("processed-inventory", processed)
    logger.info(
        f"[yellow]{len(processed)} total RegScale inventory successfully uploaded. Saved to processed-inventory.json"
    )
