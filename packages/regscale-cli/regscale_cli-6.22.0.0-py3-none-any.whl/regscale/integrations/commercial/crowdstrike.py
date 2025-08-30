#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CrowdStrike RegScale integration"""
import json
import os
import sys
from enum import Enum
from typing import Callable, Optional, Union, Dict
from urllib.parse import urljoin

import click
from falconpy import Incidents, Intel, OAuth2, UserManagement
from rich.console import Console
from rich.progress import track
from rich.table import Table

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    error_and_exit,
    format_data_to_html,
    get_current_datetime,
)
from regscale.core.app.utils.app_utils import remove_keys
from regscale.core.app.utils.regscale_utils import verify_provided_module
from regscale.models import regscale_id, regscale_module, regscale_models
from regscale.models.regscale_models import Catalog
from regscale.models.regscale_models import (
    ControlImplementation,
    ControlImplementationStatus,
)
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.incident import Incident

#####################################################################################################
#
# CrowdStrike API Documentation: https://dash.readme.com/to/crowdstrike-enterprise?redirect=%2Fcrowdstrike%2Fdocs

# Sync incidents from CrowdStrike EDR into RegScale

# Allow customer to set severity level of what level of alerts they want to sync, set via init.yaml

# Check to make sure alert does not already exist, if it does, update with latest info, if it doesn't, create a new one

# Ensure you can link back to the alert in CrowdStrike

# Get with Jim Townsend on access to a DEV environment or customer sandbox

#####################################################################################################

logger = create_logger()
console = Console()
project_dir = os.getcwd()


class Status(Enum):
    """Enum used to describe status values."""

    NEW = 20
    REOPENED = 25
    INPROGRESS = 30
    CLOSED = 40


class StatusColor(Enum):
    """Enum to describe colors used for status displays."""

    NEW = "[cornsilk1]"
    REOPENED = "[bright_yellow]"
    INPROGRESS = "[deep_sky_blue1]"
    CLOSED = "[bright_green]"


@click.group()
def crowdstrike():
    """[BETA] CrowdStrike Integration to load threat intelligence to RegScale."""


@crowdstrike.command(name="query_incidents")
@regscale_id(help="RegScale will create and update issues as children of this record.")
@regscale_module()
@click.option(
    "--filter",
    type=click.STRING,
    default=None,
    hide_input=False,
    required=False,
    help="Falcon Query Language(FQL) string.",
)
def query_incidents(regscale_id: int, regscale_module: str, filter: str, limit=500) -> None:
    """Query Incidents from CrowdStrike."""
    query_crowdstrike_incidents(regscale_id, regscale_module, filter, limit)


def determine_incident_level(fine_score: int) -> str:
    """
    Determine the incident level based on a fine_score

    :param int fine_score: The fine_score as an integer
    :return: The incident level as a string
    :rtype: str
    """
    # Convert fine_score to the displayed score
    displayed_score = fine_score / 10.0

    if displayed_score >= 10.0:
        return "S1 - High Severity"
    elif displayed_score >= 8.0:
        return "S1 - High Severity"
    elif displayed_score >= 6.0:
        return "S2 - Moderate Severity"
    elif displayed_score >= 4.0:
        return "S3 - Low Severity"
    elif displayed_score >= 2.0:
        return "S4 - Non-Incident"
    else:
        return "S5 - Uncategorized"


def map_status_to_phase(status_code: int) -> str:
    """Map a CrowdStrike status code to a RegScale phase

    :param int status_code: The status code from CrowdStrike as an integer.
    :return: The corresponding phase in RegScale as a string.
    :rtype: str
    """
    crowdstrike_to_regcale_mapping = {
        20: "Detection",
        25: "Analysis",
        30: "Containment",
        40: "Closed",
    }

    return crowdstrike_to_regcale_mapping.get(status_code, "Analysis")


def create_properties_for_incident(device_data: dict, regscale_id: int) -> None:
    """Create properties in RegScale based on the given device data dictionary

    :param dict device_data: The device data as a dictionary.
    :param int regscale_id: The parent ID of the incidents.
    :rtype: None
    """
    # Simulate RegScale API or database connection
    properties = []
    api = Api()
    domain = api.config.get("domain")
    url = urljoin(domain, "/api/properties/batchCreate")
    for key, value in device_data.items():
        # Skip list pieces
        if not isinstance(value, list):
            # Create property in RegScale (simulated)
            prop = {
                "isPublic": "true",
                "key": key,
                "value": value,
                "parentId": regscale_id,
                "parentModule": "incidents",
            }
            properties.append(prop)
    response = api.post(url=url, json=properties)
    if not response.ok:
        logger.error("Failed to create property.")


def get_existing_regscale_incidents(parent_id: int, parent_module: str) -> list[dict]:
    """Get existing RegScale incidents for the given parent ID and parent module

    :param int parent_id: The parent ID of the incidents.
    :param str parent_module: The parent module of the incidents.
    :return: The existing incidents as a list of dictionaries.
    :rtype: list[dict]
    """
    existing_incidents = Incident.get_all_by_parent(parent_id, parent_module)
    return [incident.dict() for incident in existing_incidents]


def incidents_exist(title: str, existing_incidents: list[dict]) -> bool:
    """Determine if an incident already exists in RegScale

    :param str title: The title of the incident.
    :param list[dict] existing_incidents: The existing incidents as a list of dictionaries.
    :return: If the incident already exists in RegScale
    :rtype: bool
    """
    if existing_incidents:
        for existing_incident in existing_incidents:
            if existing_incident["title"] == title:
                logger.info(f"Incident {existing_incident['title']} already exists in RegScale.")
                return True
    return False


def create_regscale_incidents(incidents: list[dict], regscale_id: int, regscale_module: str) -> None:
    """
    Create Incidents in RegScale based on given Falcon incidents.

    :param list[dict] incidents: List of Falcon Incident dictionaries
    :param int regscale_id: RegScale parent ID
    :param str regscale_module: RegScale parent module
    :rtype: None
    """

    app = Application()
    existing_incidents = get_existing_regscale_incidents(regscale_id, regscale_module)
    logger.info(f"Found {len(existing_incidents)} existing incidents.")
    user_id = app.config.get("userId")

    for incident in track(
        incidents,
        description="[#f8b737]Comparing Crowdstrike and RegScale incident(s)...",
    ):
        title = f"CrowdStrike incidentId: {incident['incident_id']}"

        if not incidents_exist(title, existing_incidents):
            regscale_incident = create_regscale_incident(incident, regscale_id, regscale_module, user_id)
            post_incident_and_associate_properties(regscale_incident, incident, user_id)


def create_regscale_incident(
    incident: dict,
    regscale_id: int,
    regscale_module: str,
    user_id: Optional[str] = None,
) -> Incident:
    """
    Creates a RegScale incident object from a Falcon incident

    :param dict incident: Falcon incident dictionary
    :param int regscale_id: RegScale parent ID
    :param str regscale_module: RegScale parent module
    :param Optional[str] user_id: User ID of the user performing the operation, defaults to None
    :return: RegScale incident object
    :rtype: Incident
    """
    severity = determine_incident_level(incident["fine_score"])
    source_cause = ", ".join(incident.get("techniques", "")) if incident else ""

    return Incident(
        title=f"CrowdStrike incidentId: {incident['incident_id']}",
        severity=severity,
        sourceCause=source_cause,
        category="CAT 6 - Investigation",
        phase=map_status_to_phase(incident["status"]),
        description=format_data_to_html(incident),  # Assuming this function formats the data to HTML
        detectionMethod="Intrusion Detection System",
        incidentPOCId=user_id,
        dateDetected=incident["created"],
        parentId=regscale_id if regscale_id is not None else None,
        parentModule=regscale_module if regscale_module is not None else None,
        lastUpdatedById=user_id,
        dateCreated=incident["created"],
        dateLastUpdated=get_current_datetime(),
        dateResolved=(
            incident["end"] if "end" in incident and map_status_to_phase(incident["status"]) == "Closed" else None
        ),
        createdById=user_id,
    )


def post_incident_and_associate_properties(
    regscale_incident: Incident, incident: dict, user_id: Optional[str] = None
) -> None:
    """
    Posts the incident to RegScale and associates related properties

    :param Incident regscale_incident: RegScale incident object
    :param dict incident: Falcon incident dictionary
    :param Optional[str] user_id: ID of the user performing the operation, defaults to None
    :rtype: None
    """
    response = Incident.post_incident(regscale_incident)
    if response.ok:
        incident_id = response.json()["id"]
        create_and_associate_incident_properties(incident, incident_id, user_id)
        logger.info(f"Created Incident: {regscale_incident.title} with ID: {incident_id}")
    else:
        response.raise_for_status()
        logger.error(f"Failed to create Incident: {regscale_incident.title} in RegScale.")


def create_and_associate_incident_properties(incident: dict, incident_id: int, user_id: Optional[str] = None) -> None:
    """
    Creates and associates properties for a RegScale incident

    :param dict incident: Falcon incident dictionary
    :param int incident_id: ID of the RegScale incident
    :param Optional[str] user_id: ID of the user performing the operation, defaults to None
    :rtype: None
    """
    for host in incident.get("hosts", []):
        create_asset(data=host, parent_id=incident_id, parent_module="incidents", user_id=user_id)

    for tactic in incident.get("tactics", []):
        create_properties_for_incident({"tactic": tactic}, incident_id)

    for technique in incident.get("techniques", []):
        create_properties_for_incident({"technique": technique}, incident_id)

    for objective in incident.get("objectives", []):
        create_properties_for_incident({"objective": objective}, incident_id)

    for user in incident.get("users", []):
        create_properties_for_incident({"user": user}, incident_id)


def create_asset(data: dict, parent_id: int, parent_module: str, user_id: str) -> Dict:
    """
    Create an asset in RegScale

    :param dict data: The asset data as a dictionary
    :param int parent_id: The parent ID in RegScale
    :param str parent_module: The parent module in RegScale
    :param str user_id: The user ID in RegScale
    :return: Asset object as a dictionary
    :rtype: Dict
    """
    device_id = data.get("device_id", "")
    asset = Asset(
        parentId=parent_id,
        parentModule=parent_module,
        name=f'{data.get("hostname", device_id)} - {data.get("system_product_name", "Asset")}',
        description=data.get("product_type_desc", None),
        ipAddress=data.get("external_ip", None),
        macAddress=data.get("mac_address", None),
        manufacturer=data.get("bios_manufacturer", None),
        model=data.get("bios_version", None),
        serialNumber=data.get("serial-number", None),
        assetCategory=regscale_models.AssetCategory.Hardware,
        assetType="Desktop",
        fqdn=data.get("fqdn", None),
        notes=data.get("remarks", None),
        operatingSystem=data.get("os_version", None),
        osVersion=(
            f"{data.get('major_version', None)}.{data.get('minor_version', None)}"
            if data.get("major_version", None)
            else None
        ),
        netBIOS=data.get("netbios-name", None),
        iPv6Address=data.get("ipv6-address", None),
        ram=0,
        diskStorage=0,
        cpu=0,
        assetOwnerId=user_id,
        status="Active (On Network)",
        isPublic=True,
        dateCreated=get_current_datetime(),
        dateLastUpdated=get_current_datetime(),
    ).create()
    return asset.dict()


def query_crowdstrike_incidents(regscale_id: int, regscale_module: str, filter: str, limit: int = 500) -> None:
    """
    Query Incidents from CrowdStrike

    :param int regscale_id: RegScale parent ID
    :param str regscale_module: RegScale parent module
    :param str filter: Falcon Query Language Filter
    :param int limit: Record limit, 1-500, defaults to 500
    :rtype: None
    """
    incident_list = []
    avail = True
    offset = 500
    while avail:
        incidents = open_sdk().query_incidents(filter=filter, limit=limit, offset=offset)
        logger.info(f"Found {len(incidents['body']['resources'])} incidents.")
        if incidents["status_code"] != 200:
            error_and_exit(incidents["body"]["errors"][0])
        if not incidents["body"]["resources"]:
            avail = False
        else:
            offset += limit
            incident_list.extend(incidents["body"]["resources"])
    if incident_list:
        create_regscale_incidents(incident_list, regscale_id, regscale_module)


def open_sdk() -> Optional[Incidents]:
    """
    Function to create an instance of the Crowdstrike SDK

    :return: Incidents object
    :rtype: Optional[Incidents]
    """
    app = Application()
    falcon_client_id = app.config.get("crowdstrikeClientId")
    falcon_client_secret = app.config.get("crowdstrikeClientSecret")
    try:
        inc_object = Incidents(client_id=falcon_client_id, client_secret=falcon_client_secret)
        if inc_object is not None:
            logger.info("Successfully created Crowdstrike client.")
            return inc_object
        else:
            logger.error("Unable to create Crowdstrike object.")
    except AttributeError as aex:
        logger.error(aex)
        if str(aex) == """'str' object has no attribute 'authenticated'""":
            error_and_exit("Unable to Authenticate with CrowdStrike API. Please check your credentials.")


def users() -> UserManagement:
    """
    Create instances of our two Service Classes and returns them

    :return: UserManagement object
    :rtype: UserManagement
    """
    return UserManagement(auth_object=open_sdk())


def get_incident_ids(sdk: Incidents, filter_string: Optional[str]) -> list:
    """
    Retrieve all available incident IDs from Crowdstrike

    :param Incidents sdk: Crowdstrike SDK object
    :param Optional[str] filter_string: Filter string to use for query
    :raises General Error: If unable to retrieve incident IDs from Crowdstrike
    :return: List of incident IDs
    :rtype: list
    """
    params = {}
    if filter_string:
        params = {"filter": filter_string}
    incident_id_lookup = sdk.query_incidents(**params)
    if incident_id_lookup["status_code"] != 200:
        error_and_exit(incident_id_lookup["body"]["errors"][0])
    if not incident_id_lookup["body"]["resources"]:
        logger.warning("No incidents found.")

    return incident_id_lookup["body"]["resources"]


def get_incident_data(id_list: list, sdk: Incidents) -> list[dict]:
    """Retrieve incident details using the IDs provided

    :param list id_list: List of incident IDs from Crowdstrike
    :param Incidents sdk: Crowdstrike SDK object
    :raises General Error: If unable to retrieve incident details from Crowdstrike
    :return: List of incident details
    :rtype: list
    """
    incident_detail_lookup = sdk.get_incidents(ids=id_list)
    if incident_detail_lookup["status_code"] != 200:
        error_and_exit(incident_detail_lookup["body"]["errors"][0])
    return incident_detail_lookup["body"]["resources"]


def tagging(inc_id: str, tags: list, untag: bool = False) -> None:
    """Assign or remove all tags provided

    :param str inc_id: Incident ID to tag
    :param list tags: List of tags to assign
    :param bool untag: Flag to remove tags instead of assign, defaults to False
    :rtype: None
    """
    sdk = open_sdk()
    action = {"ids": get_incident_full_id(inc_id)}
    if untag:
        action["delete_tag"] = tags
    else:
        action["add_tag"] = tags
    change_result = sdk.perform_incident_action(**action)
    if change_result["status_code"] != 200:
        error_and_exit(change_result["body"]["errors"][0])


def get_user_detail(uuid: str) -> str:
    """Retrieve assigned to user information for tabular display

    :param str uuid: User ID to retrieve information for in CrowdStrike
    :return: User information
    :rtype: str
    """
    lookup_result = users.retrieve_user(ids=uuid)
    if lookup_result["status_code"] != 200:
        error_and_exit(lookup_result["body"]["errors"][0])
    user_info = lookup_result["body"]["resources"][0]
    first = user_info["firstName"]
    last = user_info["lastName"]
    uid = user_info["uid"]

    return f"{first} {last} ({uid})"


def get_incident_full_id(partial: str) -> Union[str, bool]:
    """
    Retrieve the full incident ID based off of the partial ID provided

    :param str partial: Partial incident ID to search for
    :raises General Error: If api call != 200
    :raises General Error: If unable to find incident ID
    :return: Full incident ID
    :rtype: Union[str, bool]
    """
    sdk = open_sdk()
    search_result = sdk.query_incidents()
    if search_result["status_code"] != 200:
        error_and_exit(search_result["body"]["errors"][0])
    found = False
    for inc in search_result["body"]["resources"]:
        incnum = inc.split(":")[2]
        if incnum == partial:
            found = inc
            break

    if not found:
        error_and_exit("Unable to find incident ID specified.")

    return found


def assignment(inc_id: str, assign_to: str = "", unassign: bool = False) -> None:
    """
    Assign the incident specified to the user specified

    :param str inc_id: Incident ID to assign
    :param str assign_to: User ID to assign incident to
    :param bool unassign: Flag to unassign incident, defaults to False
    :raises General Error: If API Call != 200
    :rtype: None
    """
    sdk = open_sdk()
    if unassign:
        change_result = sdk.perform_incident_action(ids=get_incident_full_id(inc_id), unassign=True)
        if change_result["status_code"] != 200:
            error_and_exit(change_result["body"]["errors"][0])
    else:
        lookup_result = users.retrieve_user_uuid(uid=assign_to)

        if lookup_result["status_code"] != 200:
            error_and_exit(lookup_result["body"]["errors"][0])
        change_result = sdk.perform_incident_action(
            ids=get_incident_full_id(inc_id),
            update_assigned_to_v2=lookup_result["body"]["resources"][0],
        )
        if change_result["status_code"] != 200:
            error_and_exit(change_result["body"]["errors"][0])


def status_information(inc_data: dict) -> str:
    """
    Parse status information for tabular display

    :param dict inc_data: Incident data to parse
    :return: Status information
    :rtype: str
    """
    inc_status = [
        f"{StatusColor[Status(inc_data['status']).name].value}"
        f"{Status(inc_data['status']).name.title().replace('Inp', 'InP')}[/]"
    ]
    tag_list = inc_data.get("tags", [])
    if tag_list:
        inc_status.append(" ")
        tag_list = [f"[magenta]{tg}[/]" for tg in tag_list]
        inc_status.extend(tag_list)

    return "\n".join(inc_status)


def incident_information(inc_data: dict) -> str:
    """
    Parse incident overview information for tabular display

    :param dict inc_data: Incident data to parse
    :return: Incident overview information
    :rtype: str
    """
    inc_info = []
    inc_info.append(inc_data.get("name", ""))
    inc_info.append(f"[bold]{inc_data['incident_id'].split(':')[2]}[/]")
    inc_info.append(f"Start: {inc_data.get('start', 'Unknown').replace('T', ' ')}")
    inc_info.append(f"  End: {inc_data.get('end', 'Unknown').replace('T', ' ')}")
    if assigned := inc_data.get("assigned_to"):
        inc_info.append("\n[underline]Assignment[/]")
        inc_info.append(get_user_detail(assigned))
    if inc_data.get("description"):
        inc_info.append(" ")
        inc_info.append(chunk_long_description(inc_data["description"], 50))

    return "\n".join(inc_info)


def chunk_long_description(desc: str, col_width: int) -> str:
    """
    Chunk a long string by delimiting with CR based upon column length

    :param str desc: Description to parse
    :param int col_width: Column width to chunk by
    :return: Chunked description
    :rtype: str
    """
    desc_chunks = []
    chunk = ""
    for word in desc.split():
        new_chunk = f"{chunk}{word.strip()} "
        if len(new_chunk) >= col_width:
            desc_chunks.append(new_chunk)
            chunk = ""
        else:
            chunk = new_chunk

    delim = "\n"
    desc_chunks.append(chunk)

    return delim.join(desc_chunks)


def hosts_information(inc_data: dict) -> str:
    """
    Parse hosts information for tabular display

    :param dict inc_data: Incident data to parse
    :return: Host information
    :rtype: str
    """
    returned = ""
    if "hosts" in inc_data:
        host_str = []
        for host in inc_data["hosts"]:
            host_info = []
            host_info.append(
                f"<strong>{host.get('hostname', 'Unidentified')}</strong>"
                f" ({host.get('platform_name', 'Not available')})"
            )
            host_info.append(f"<span style='color:cyan'>{host.get('device_id', 'Not available')}</span>")
            host_info.append(f"  Int: {host.get('local_ip', 'Not available')}")
            host_info.append(f"  Ext: {host.get('external_ip', 'Not available')}")
            first = host.get("first_seen", "Unavailable").replace("T", " ").replace("Z", " ")
            host_info.append(f"First: {first}")
            last = host.get("last_seen", "Unavailable").replace("T", " ").replace("Z", " ")
            host_info.append(f" Last: {last}")
            host_str.append("\n".join(host_info))
        if host_str:
            returned = "\n".join(host_str)
        else:
            returned = "Unidentified"

    return returned


def show_incident_table(incident_listing: list) -> None:
    """
    Display all returned incidents in tabular fashion

    :param list incident_listing: List of incidents to parse and print to console
    :raises General Error: If incident_listing is empty
    :rtype: None
    """
    if not incident_listing:
        error_and_exit("No incidents found, code 404")
    table = Table(show_header=True, header_style="bold magenta", title="Incidents")
    headers = {
        "status": "[bold]Status[/] ",
        "incident": "[bold]Incident[/]",
        "hostname": "[bold]Host[/]",
        "tactics": "[bold]Tactics[/]",
        "techniques": "[bold]Techniques[/]",
        "objectives": "[bold]Objective[/]s",
    }
    for value in headers.values():
        table.add_column(value, justify="left")
    for inc in incident_listing:
        inc_detail = {"status": status_information(inc)}
        inc_detail["incident"] = incident_information(inc)
        inc_detail["hostname"] = hosts_information(inc)
        inc_detail["tactics"] = "\n".join(inc["tactics"])
        inc_detail["techniques"] = "\n".join(inc["techniques"])
        inc_detail["objectives"] = "\n".join(inc["objectives"])
        table.add_row(
            inc_detail["status"],
            inc_detail["incident"],
            inc_detail["hostname"],
            inc_detail["tactics"],
            inc_detail["techniques"],
            inc_detail["objectives"],
        )
    console.print(table)


def get_token() -> str:
    """
    Get the token for the CrowdStrike API

    :raises General Error: If unable to authenticate with CrowdStrike via API
    :return: CrowdStrike API token
    :rtype: str
    """
    app = Application()
    falcon_client_id = app.config.get("crowdstrikeClientId")
    falcon_client_secret = app.config.get("crowdstrikeClientSecret")
    falcon_url = app.config.get("crowdstrikeBaseUrl")

    if not falcon_client_id:
        falcon_client_id = click.prompt("Please provide your Falcon Client API Key", hide_input=True)
    if not falcon_client_secret:
        falcon_client_secret = click.prompt("Please provide your Falcon Client API Secret", hide_input=True)
    auth = OAuth2(
        client_id=falcon_client_id,
        client_secret=falcon_client_secret,
        base_url=falcon_url,
    )
    # Generate a token
    auth.token()
    if auth.token_status != 201:
        raise error_and_exit("Unable to authenticate with Crowdstrike!")
    return auth.token_value


@crowdstrike.command(name="sync_incidents")
@regscale_id(help="RegScale will create and update incidents as children of this record.")
@regscale_module()
def sync_incidents(regscale_id: int, regscale_module: str):
    """Sync Incidents and Assets from CrowdStrike to RegScale."""
    sync_incidents_to_regscale(regscale_id, regscale_module)


def sync_incidents_to_regscale(regscale_id: int, regscale_module: str) -> None:
    """
    Sync Incidents and Assets from CrowdStrike to RegScale

    :param int regscale_id: RegScale record ID
    :param str regscale_module: RegScale Module
    :rtype: None
    """
    verify_provided_module(regscale_module)
    sdk = open_sdk()
    incident_id_list = get_incident_ids(filter_string=None, sdk=sdk)
    if not incident_id_list:
        error_and_exit("No incidents found!")
    incidents = get_incident_data(id_list=incident_id_list, sdk=sdk)
    logger.info(f"Found {len(incidents)} incidents to sync.")
    create_regscale_incidents(incidents=incidents, regscale_id=regscale_id, regscale_module=regscale_module)


def get_intel() -> Intel:
    """
    Get the Intel SDK object

    :return: Intel SDK object
    :rtype: Intel
    """
    app = Application()
    client_id = app.config.get("crowdstrikeClientId")
    client_secret = app.config.get("crowdstrikeClientSecret")
    intel = Intel(
        client_id=client_id,
        client_secret=client_secret,
    )
    return intel


def get_vulnerability_ids(intel, limit=100) -> list:
    """Fetch ID's from CrowdStrike for Intel Model

    :param Intel intel: The Intel SDK object
    :param int limit: The number of records to fetch from CrowdStrike, defaults to 100
    :raises General Error: If errors are returned from CrowdStrike
    :raises Exception: If unable to fetch ID's from CrowdStrike
    :return: List of vulnerability ID's
    :rtype: list
    """
    try:
        id_lookup = intel.query_vulnerabilities(limit=limit)
        if "errors" in id_lookup["body"]:
            error_and_exit(id_lookup["body"]["errors"])
        number_of_records = len(id_lookup["body"]["resources"])
        if number_of_records == 0:
            logger.info(f"Found {number_of_records} Records.")
            sys.exit(0)
        return id_lookup["body"]["resources"]
    except Exception as e:
        error_and_exit(f"Error: {e}")


def get_vulnerabilities_by_id(ids: list, intel: Intel) -> list[dict]:
    """
    Retrieve record details using the IDs provided

    :param list ids: The IDs of the records to retrieve
    :param Intel intel: The Intel SDK object
    :return: A list of dictionaries containing the record details
    :rtype: list[dict]
    """
    detail_lookup = intel.get_vulnerabilities(ids=ids)
    if detail_lookup["status_code"] != 200:
        error_and_exit(detail_lookup["body"]["errors"][0])
    return detail_lookup["body"]["resources"]


# FIXME: this will pull the data from the CrowdStrike API but need to figure out what the data looks like before we can map it
# @crowdstrike.command(name="fetch_vulnerabilities")
# @regscale_id(help="RegScale will create vulnerabilities as children of this record.")
# @regscale_module()
# @click.option("--limit", "-l", default=100, help="Limit the number of records")
# def sync_vulnerabilities(regscale_id: int, regscale_module: str, limit: int) -> None:
#     """
#     Fetch all vulnerabilities from CrowdStrike.
#     :param int regscale_id: The ID of the RegScale record.
#     :param str regscale_module: The module of the RegScale record.
#     :param int limit: The number of records to fetch.
#     """
#     _sync_vulnerabilities(regscale_id=regscale_id, regscale_module=regscale_module, limit=limit)
#
#
# def _sync_vulnerabilities(regscale_id: int, regscale_module: str, limit) -> None:
#     """
#     Fetch all vulnerabilities from CrowdStrike.
#     :param int regscale_id: The ID of the RegScale record.
#     :param str regscale_module: The module of the RegScale record.
#     :param int limit: The number of records to fetch.
#     """
#     intel = get_intel()
#     ids = get_vulnerability_ids(intel=intel, limit=limit)
#     data = get_vulnerabilities_by_id(ids=ids, intel=intel)
#     logger.info(json.dumps(data, indent=4))


def load_compliance_data(framework_file: str) -> dict:
    """
    Load compliance data for the given framework from the package resources

    :param str framework_file: The framework to load the compliance data for
    :return: The compliance data as a dictionary
    :rtype: dict
    """
    from importlib.resources import open_text

    with open_text("regscale.integrations.commercial.mappings", f"{framework_file}.json") as f:
        return json.load(f)


def sync_compliance(ssp_id: int, catalog_id: int, framework: str) -> None:
    """
    Sync compliance data from CrowdStrike to RegScale

    :param int ssp_id: The ID of the SSP record
    :param int catalog_id: The ID of the catalog to use for the sync
    :param str framework: The framework to use for the sync
    :rtype: None
    """
    catalog = Catalog.get_with_all_details(catalog_id=catalog_id)
    if framework == "NIST800-53R5":
        compliance_data = load_compliance_data("nist_800_53_r5_controls")
    elif framework == "CSF":
        compliance_data = load_compliance_data("csf_controls")
    else:
        logger.warning(f"Invalid framework: {framework}")
        return

    logger.info(f"Loading: {framework}")
    logger.info(f"Mapping file loaded items mapped: {len(compliance_data)}")
    cat_controls = catalog.get("controls", None)
    if not cat_controls:
        logger.error(f"No controls found for catalog {catalog_id}")
        return
    full_controls = {}
    partial_controls = {}
    for control in cat_controls:
        compliance_control = compliance_data.get(control.get("controlId"), None)

        if compliance_control and compliance_control.get("support") in [
            "Full",
            "Partial",
        ]:
            notes = [f"<p>{note}</p>" for note in compliance_control.get("notes", [])]
            if compliance_control.get("support") == "Full":
                control["implementation"] = "\n".join(notes)
                full_controls[control.get("controlId").lower()] = control
            elif compliance_control.get("support") == "Partial":
                control["implementation"] = "\n".join(notes)
                partial_controls[control.get("controlId").lower()] = control
    logger.info(f"found fully implemented controls len: {len(full_controls)}")
    logger.info(f"found partial implemented controls len: {len(partial_controls)}")
    create_control_implementations(
        cat_controls,
        parent_id=ssp_id,
        parent_module="securityplans",
        existing_implementation_dict=ControlImplementation.get_existing_control_implementations(parent_id=ssp_id),
        full_controls=full_controls,
        partial_controls=partial_controls,
        failing_controls={},
    )


@crowdstrike.command(name="sync_compliance")
@click.option("--ssp_id", "-s", type=click.INT, required=True, help="The ID of the SSP record.")
@click.option(
    "--catalog_id",
    "-c",
    type=click.INT,
    required=True,
    help="The ID of the catalog to use for the sync.",
)
@click.option(
    "--framework",
    "-f",
    type=click.Choice(["CSF", "NIST800-53R5"], case_sensitive=False),
    help="Choose either CSF or NIST800-53R5",
)
def run_compliance_sync(
    ssp_id: int,
    catalog_id: int,
    framework: str,
) -> None:
    """Run a compliance sync from CrowdStrike to RegScale."""
    sync_compliance(ssp_id=ssp_id, catalog_id=catalog_id, framework=framework)


def create_control_implementations(
    controls: list,
    parent_id: int,
    parent_module: str,
    existing_implementation_dict: dict,
    full_controls: dict,
    partial_controls: dict,
    failing_controls: dict,
) -> None:
    """
    Creates and updates control implementations based on given controls

    :param list controls: List of control details
    :param int parent_id: Identifier for the parent control
    :param str parent_module: Name of the parent module
    :param dict existing_implementation_dict: Dictionary of existing implementations
    :param dict full_controls: Dictionary of fully implemented controls
    :param dict partial_controls: Dictionary of partially implemented controls
    :param dict failing_controls: Dictionary of failing controls
    :rtype: None
    """
    app = Application()
    user_id = app.config.get("userId")

    to_create, to_update = process_controls(
        controls,
        parent_id,
        parent_module,
        existing_implementation_dict,
        full_controls,
        partial_controls,
        failing_controls,
        user_id,
    )

    post_batch_if_needed(app, to_create, ControlImplementation.post_batch_implementation)
    put_batch_if_needed(app, to_update, ControlImplementation.put_batch_implementation)


def process_controls(
    controls: list,
    parent_id: int,
    parent_module: str,
    existing_implementation_dict: dict,
    full_controls: dict,
    partial_controls: dict,
    failing_controls: dict,
    user_id: Optional[str] = None,
) -> tuple[list, list]:
    """
    Processes each control for creation or update

    :param list controls: List of control details
    :param int parent_id: Identifier for the parent control
    :param str parent_module: Name of the parent module
    :param dict existing_implementation_dict: Dictionary of existing implementations
    :param dict full_controls: Dictionary of fully implemented controls
    :param dict partial_controls: Dictionary of partially implemented controls
    :param dict failing_controls: Dictionary of failing controls
    :param Optional[str] user_id: ID of the user performing the operation, defaults to None
    :return: Tuple containing lists of controls to create and update
    :rtype: tuple[list, list]
    """
    to_create = []
    to_update = []

    for control in controls:
        lower_case_control_id = control["controlId"].lower()
        status = check_implementation(full_controls, partial_controls, failing_controls, lower_case_control_id)

        if control["controlId"] not in existing_implementation_dict:
            cim = create_new_control_implementation(control, parent_id, parent_module, status, user_id)
            to_create.append(cim)
        else:
            update_existing_control_implementation(control, existing_implementation_dict, status, to_update, user_id)

    return to_create, to_update


def create_new_control_implementation(
    control: dict,
    parent_id: int,
    parent_module: str,
    status: str,
    user_id: Optional[str] = None,
) -> ControlImplementation:
    """
    Creates a new control implementation object

    :param dict control: Control details
    :param int parent_id: Identifier for the parent control
    :param str parent_module: Name of the parent module
    :param str status: Status of the control implementation
    :param Optional[str] user_id: ID of the user performing the operation, defaults to None
    :return: New control implementation object
    :rtype: ControlImplementation
    """
    cim = ControlImplementation(
        controlOwnerId=user_id,
        dateLastAssessed=get_current_datetime(),
        status=status,
        controlID=control["id"],
        parentId=parent_id,
        parentModule=parent_module,
        createdById=user_id,
        dateCreated=get_current_datetime(),
        lastUpdatedById=user_id,
        dateLastUpdated=get_current_datetime(),
    ).dict()
    cim["controlSource"] = "Baseline"
    return cim


def update_existing_control_implementation(
    control: dict,
    existing_implementation_dict: dict,
    status: str,
    to_update: list,
    user_id: Optional[str] = None,
):
    """
    Updates an existing control implementation

    :param dict control: Control details
    :param dict existing_implementation_dict: Dictionary of existing implementations
    :param str status: Status of the control implementation
    :param list to_update: List of controls to update
    :param Optional[str] user_id: ID of the user performing the operation, defaults to None
    """
    existing_imp = existing_implementation_dict[control["controlId"]]
    existing_imp.update(
        {
            "implementation": control.get("implementation"),
            "status": status,
            "dateLastAssessed": get_current_datetime(),
            "lastUpdatedById": user_id,
            "dateLastUpdated": get_current_datetime(),
        }
    )

    remove_keys(existing_imp, ["createdBy", "systemRole", "controlOwner", "lastUpdatedBy"])

    if existing_imp not in to_update:
        to_update.append(existing_imp)


def post_batch_if_needed(
    app: Application,
    to_create: list,
    post_function: Callable[[Application, list], None],
) -> None:
    """
    Posts a batch of new implementations if the list is not empty

    :param Application app: RegScale CLI application object
    :param list to_create: List of new implementations to post
    :param Callable[[Application, list], None] post_function: The function to call for posting the batch
    :rtype: None
    """
    if to_create:
        post_function(app, to_create)


def put_batch_if_needed(app: Application, to_update: list, put_function: Callable[[Application, list], None]) -> None:
    """
    Puts a batch of updated implementations if the list is not empty

    :param Application app: RegScale CLI application object
    :param list to_update: List of implementations to update
    :param Callable[[Application, list], None] put_function: The function to call for putting the batch
    :rtype: None
    """
    if to_update:
        put_function(app, to_update)


def check_implementation(
    full_controls: dict,
    partial_controls: dict,
    failing_controls: dict,
    control_id: str,
) -> str:
    """
    Checks the status of a control implementation

    :param dict full_controls: Dictionary of passing controls
    :param dict partial_controls: Dictionary of partially implemented controls
    :param dict failing_controls: Dictionary of failing control implementations
    :param str control_id: control id
    :return: status of control implementation
    :rtype: str
    """
    if control_id in full_controls.keys():
        logger.debug(f"Found fully implemented control: {control_id}")
        return ControlImplementationStatus.FullyImplemented.value
    elif control_id in partial_controls.keys():
        logger.debug(f"Found partially implemented control: {control_id}")
        return ControlImplementationStatus.PartiallyImplemented.value
    elif control_id in failing_controls.keys():
        logger.debug(f"Found failing control: {control_id}")
        return ControlImplementationStatus.InRemediation.value
    else:
        logger.debug(f"Found not implemented control: {control_id}")
        return ControlImplementationStatus.NotImplemented.value
