#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2nd iteration to add functionality to upgrade application catalog information via API."""

import csv
import json
import sys
from datetime import datetime
from os import path
from pathlib import Path
from typing import Any, List, Optional, Union
from urllib.parse import urljoin

from requests import Response
from rich.progress import track

from regscale.core.app import create_logger
from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import error_and_exit

SECURITY_CONTROL = "security control"
logger = create_logger()
API_SECURITY_CONTROLS_ = "api/SecurityControls/"
API_CATALOGUES_ = "api/catalogues/"
master_catalog_list_url = "https://regscaleblob.blob.core.windows.net/catalogs/catalog_registry.json"


def display_menu() -> None:
    """
    Initial function called by the click command. Fires off functions to collect data for comparison and trigger updates

    :rtype: None
    """
    api = Api()
    catalog_number_to_update = select_installed_catalogs(api)
    update_sourcefile = get_update_file(api, catalog_number_to_update)
    new_version_catalog_data = load_updated_catalog(update_sourcefile)
    existing_catalog_data = load_existing_catalog(api, catalog_number_to_update)
    dryrun = confirm_actions(new_version_catalog_data, existing_catalog_data)
    process_catalog_update(
        api=api,
        new_version_catalog=new_version_catalog_data,
        existing_catalog=existing_catalog_data,
        dryrun=dryrun,
    )


def import_catalog(catalog_path: Path) -> Response:
    """
    Import a RegScale catalog from a json file.  This file must be formatted as a RegScale catalog

    :param Path catalog_path: Path to the catalog file to be imported
    :return: Response from API call
    :rtype: Response
    """
    api = Api()
    file_headers = {
        "Authorization": api.config["token"],
        "Accept": "application/json, text/plain, */*",
    }
    # increase the api timeout to 120 seconds
    if api.timeout < 120:
        api.timeout = 120
    # set the files up for the RegScale API Call
    with open(catalog_path, "rb") as file:
        files = [
            (
                "file",
                (
                    catalog_path.name,
                    file.read(),
                    "application/json",
                ),
            )
        ]
        response = api.post(
            urljoin(api.config["domain"], API_CATALOGUES_ + "/import"),
            headers=file_headers,
            files=files,
            data={},
        )
        if response.status_code == 401:
            error_and_exit(f"Invalid authorization token. Unable to proceed. {catalog_path.name}")
        elif response.status_code == 400 and response.text == "Catalog already exists":
            api.logger.warning(f"Skipping {catalog_path.name} as it is already installed.")
        elif not response.ok:
            error_and_exit(
                f"Unexpected response from server. Unable to upload {catalog_path.name}."
                f"\n{response.status_code}: {response.reason}\n{response.text}"
            )
    return response


def select_installed_catalogs(api: Api) -> int:
    """
    Fetches the list of currently installed catalogs on the target RegScale installation so user can select for update

    :param Api api: Api object for making requests to the target RegScale installation
    :return: catalog number on the target intallation that user has selected for update
    :rtype: int
    """
    response = api.get(
        urljoin(api.config["domain"], "api/catalogues/getList")
    )  # returns catalog IDs & titles on target system
    if response.status_code == 401:
        error_and_exit("Invalid authorization token. Unable to proceed.")
    elif not response.ok:
        error_and_exit("Unexpected response from server. Unable to proceed.")
    catalogs = json.loads(response.content)
    print("The following catalogs are currently available on your RegScale installation:\n")
    ids = sorted([x["id"] for x in catalogs])
    while True:
        for catalog in catalogs:
            print(str(catalog["id"]).rjust(10, " ") + ": " + catalog["title"])
        catalog_number_to_update = input(
            "\nEnter the # of the catalog you wish to update on your target system, or type STOP to exit: "
        )
        if catalog_number_to_update.isdigit() and int(catalog_number_to_update) in ids:
            return int(catalog_number_to_update)
        elif catalog_number_to_update.lower() == "stop":
            logger.info("Exiting program. Goodbye!")
        else:
            logger.warning("\nNot a valid catalog ID number. Please try again:\n")


def get_update_file(api: Api, catalog_number_to_update: int) -> Union[str, bytes]:
    """
    Retrieves the source file for the catalog update file source, whether online or by file on disk

    :param Api api: Api object for making requests to the target RegScale installation
    :param int catalog_number_to_update: The localized catalog integer ID to be updated
        on the local RegScale installation
    :return: catalog update source file as a string or bytes
    :rtype: Union[str, bytes]
    """
    response = api.get(urljoin(api.config["domain"], API_CATALOGUES_ + str(catalog_number_to_update)))
    uuid = json.loads(response.content)["uuid"]
    while True:
        update_sourcefile = input(
            "\nEnter the filepath and name of the new version of the catalog file you wish to use,\n or "
            "press ENTER to automatically pull the latest version from RegScale servers: "
        )
        if update_sourcefile.lower() == "stop":
            logger.info("Exiting program. Goodbye!")
            sys.exit(0)
        elif update_sourcefile == "":
            logger.info("Checking online for latest file version..")
            return find_update_online(api, uuid)
        elif path.isfile(update_sourcefile):
            logger.info("Located input file.")
            return read_update_from_disk(update_sourcefile)
        else:
            logger.warning("\nNot a valid source input. Type 'STOP' to exit, or make a valid entry.")


def find_update_online(api: Api, uuid: str) -> bytes:
    """
    Receives the UUID of the original catalog that is to be updated, and searches for a matching uuid from the master
    catalog list found on the anonymous read azure blob storage

    :param Api api: Api object for making requests to the target RegScale installation
    :param str uuid: uuid string from the original catalog, used to find a matching source for update
    :return: byte string of update source catalog file retrieved online from azure blob storage
    :rtype: bytes
    """
    response = api.get(url=master_catalog_list_url, headers={})
    master_catalogs = json.loads(response.text)
    for catalog in master_catalogs["catalogs"]:
        if catalog["uuid"] == uuid:
            logger.info("Found current version of catalog. Downloading now.")
            return api.get(catalog["downloadURL"], headers={}).content
    error_and_exit(
        "Problem locating a matching catalog. Please contact customer service or try downloading the current catalog "
        "file from our website: https://regscale.com/regulations/"
    )


def read_update_from_disk(update_sourcefile: str) -> bytes:
    """
    Reads the catalog update source file from disk

    :param str update_sourcefile: filepath of current catalog version if reading from disk instead of retrieving online
    :return: bytes of json file catalog contents
    :rtype: bytes
    """
    logger.info("Loading new version of catalog.")
    try:
        with open(update_sourcefile, "rb") as json_file:
            # Read the content of the JSON file & return
            return json_file.read()
    except Exception as e:
        error_and_exit(f"Error encountered when trying to read {update_sourcefile}. Unable to continue: {e}")


def load_updated_catalog(update_source: Union[str, bytes]) -> dict:
    """
    This function translates the json dict string of update catalog source file to a JSON dict. As of 10/31/2023, the
    catalogs are still possibly in two different formats, so there is additional logic to get to the same end either way

    :param Union[str, bytes] update_source: a byte string which has previously been either
     read from disk or retrieved by requests
    :return: The update source (current version catalog)
    :rtype: dict
    """
    updated_catalog = json.loads(update_source)
    logger.info("Loading new version of catalog.")
    try:
        if "securityControls" in updated_catalog:  # if current catalog format
            return updated_catalog
        # TODO: Go back and reformat all the legacy catalogs so I can get rid of this hacky stuff
        else:  # if this is old format of catalog
            new_format_updated_catalog = {}
            for key in updated_catalog["catalog"].keys():
                new_format_updated_catalog[key] = updated_catalog["catalog"][key]
            return new_format_updated_catalog
    except Exception as e:
        error_and_exit(f"Error encountered. Unable to continue: {e}")


def load_existing_catalog(api: Api, catalog_number_to_update: int) -> dict:
    """
    Loads the existing catalog in the database that is intended to be replaced, matching format of new catalog ingest

    :param Api api: Api object for making requests to the target RegScale installation
    :param int catalog_number_to_update: RegScale catalog ID to be updated in the local RegScale installation
    :return: Dict containing the entire catalog structure in same format as catalog import files
    :rtype: dict
    """
    # TODO: When get parameters/tests/cci by catalog API endpoint is created, should update this logic to speed up
    logger.info("Loading data from existing version of catalog on RegScale installation.")
    existing_catalog = api.get(urljoin(api.config["domain"], API_CATALOGUES_ + str(catalog_number_to_update))).json()
    # Controls
    # returns a list of abbreviated records
    controls = api.get(f"{api.config['domain']}/api/SecurityControls/getList/{catalog_number_to_update}").json()
    logger.info("Fetching %i security control(s) from RegScale...", len(controls))
    controls_list = []
    for control in track(
        controls,
        description=f"Fetching {len(controls)} security control(s) from RegScale...",
    ):
        # returns complete record
        control = api.get(urljoin(api.config["domain"], API_SECURITY_CONTROLS_ + str(control["id"]))).json()
        if "objectives" in control:  # currently is a bug where api get endpoint returning empty lists for these
            del control["objectives"]
        if "parameters" in control:
            del control["parameters"]
        if "tests" in control:
            del control["tests"]
        if "ccis" in control:
            del control["ccis"]
        controls_list.append(control)
    existing_catalog["securityControls"] = controls_list
    # Objectives
    existing_catalog["objectives"] = api.get(
        urljoin(
            api.config["domain"],
            f"api/controlObjectives/getByCatalog/{catalog_number_to_update}",
        )
    ).json()
    logger.info("Received %i objective(s) from RegScale...", len(existing_catalog["objectives"]))

    control_parameters: List[dict] = []
    control_test_plans: List[dict] = []
    control_cci: List[dict] = []
    logger.info(
        "Loading Parameters, Tests, and checking for CCIs for %s security control(s)...",
        len(existing_catalog["securityControls"]),
    )
    for control in track(
        existing_catalog["securityControls"],
        description=f"Loading Parameters, Tests, and checking for CCIs for "
        f"{len(existing_catalog['securityControls'])} security control(s)...",
    ):
        # Parameters
        more_parameters = api.get(
            urljoin(
                api.config["domain"],
                f"api/controlParameters/getByControl/{control['id']}",
            )
        ).json()
        control_parameters = control_parameters + more_parameters
        # Tests
        more_tests = api.get(
            urljoin(
                api.config["domain"],
                f"api/controlTestPlans/getByControl/{control['id']}",
            )
        ).json()
        control_test_plans = control_test_plans + more_tests
        # CCIs
        more_ccis = api.get(urljoin(api.config["domain"], f"api/cci/getByControl/{control['id']}")).json()
        control_cci = control_cci + more_ccis

    existing_catalog["parameters"] = control_parameters
    existing_catalog["tests"] = control_test_plans
    existing_catalog["ccis"] = control_cci

    return existing_catalog


def confirm_actions(new_version_catalog: dict, existing_catalog: dict) -> bool:
    """
    Display title of existing catalog and update source for confirmation. Also determines if doing a dry run is true
    or false

    :param dict new_version_catalog: catalog used as update source
    :param dict existing_catalog: existing catalog pulled from target installation
    :return: True for do a dry run or false to NOT do a dry run (make updates for real)
    :rtype: bool
    """

    logger.info(
        f"Updating: {str(existing_catalog['id']).rjust(8, ' ')} - {existing_catalog['title']}"
        f"\nWith:     {''.rjust(8, ' ')}     {new_version_catalog['title']} (Latest Version)"
    )

    logger.info(
        "It is possible to do a dry run. A dry run will report any changes found without updating the data in RegScale."
    )

    while True:
        proceed = input(
            "Would you like to proceed with updating your catalog? Enter 'Y' to proceed, 'N' to do a dry run, or 'STOP'"
            "to cancel this program: "
        )
        if proceed.lower() == "n":
            return True
        elif proceed.lower() == "y":
            return False
        elif proceed.lower() == "stop":
            logger.info("Ending Program.")
            sys.exit(0)
        else:
            logger.warning("Not a valid selection. Please try again.")


def process_catalog_update(api: Api, new_version_catalog: dict, existing_catalog: dict, dryrun: bool) -> None:
    """
    Initiates catalog update checks and processing on each record type within the catalog.

    :param Api api: Api object for making requests to the target RegScale installation
    :param dict new_version_catalog: update source catalog
    :param dict existing_catalog: existing catalog to be updated, pulled from RegScale installation
    :param bool dryrun: True if a dry run (don't do updates for real, just report changes) or false (do updates)
    :rtype: None
    """
    output_filename = f"catalog_{existing_catalog['id']}_updates_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
    track_changes = []
    archived_controls = check_controls(
        api=api,
        existing_controls=existing_catalog["securityControls"],
        new_controls=new_version_catalog["securityControls"],
        track_changes=track_changes,
        dryrun=dryrun,
    )
    if "objectives" in existing_catalog:
        check_child_records(
            api=api,
            archived_controls=archived_controls,
            existing_records=existing_catalog["objectives"],
            new_records=new_version_catalog["objectives"],
            track_changes=track_changes,
            dryrun=dryrun,
            record_type="objective",
            record_id_field="name",
            endpoint="api/ControlObjectives",
            existing_controls=existing_catalog["securityControls"],
            new_controls=new_version_catalog["securityControls"],
        )
    if "parameters" in existing_catalog:
        check_child_records(
            api=api,
            archived_controls=archived_controls,
            existing_records=existing_catalog["parameters"],
            new_records=new_version_catalog["parameters"],
            track_changes=track_changes,
            dryrun=dryrun,
            record_type="parameter",
            record_id_field="parameterId",
            endpoint="api/ControlParameters",
            existing_controls=existing_catalog["securityControls"],
            new_controls=new_version_catalog["securityControls"],
        )
    if "tests" in existing_catalog:
        check_child_records(
            api=api,
            archived_controls=archived_controls,
            existing_records=existing_catalog["tests"],
            new_records=new_version_catalog["tests"],
            track_changes=track_changes,
            dryrun=dryrun,
            record_type="test",
            record_id_field="testId",
            endpoint="api/ControlTestPlans",
            existing_controls=existing_catalog["securityControls"],
            new_controls=new_version_catalog["securityControls"],
        )
    # TODO: Dealing with empty lists of CCIs returned by API.
    # Need to improve this logic because What if the CCIs or other record type were
    # left off initial catalog and added later?
    if "ccis" in existing_catalog and len(existing_catalog["ccis"]) > 0:
        check_child_records(
            api=api,
            archived_controls=archived_controls,
            existing_records=existing_catalog["ccis"],
            new_records=new_version_catalog["ccis"],
            track_changes=track_changes,
            dryrun=dryrun,
            record_type="CCI",
            record_id_field="name",
            endpoint="api/cci/",
            existing_controls=existing_catalog["securityControls"],
            new_controls=new_version_catalog["securityControls"],
        )
    check_catalog_metadata(
        api=api,
        existing_catalog=existing_catalog,
        new_version_catalog=new_version_catalog,
        track_changes=track_changes,
        dryrun=dryrun,
    )
    if len(track_changes) > 0:
        write_outcomes_to_file(changes=track_changes, output_filename=output_filename)
    else:
        logger.info("No updates found at this time.")


def check_controls(
    api: Api,
    existing_controls: list,
    new_controls: list,
    track_changes: list,
    dryrun: bool,
) -> list:
    """
    Manages several function for checking which controls may need to be updated, archived, or created.

    :param Api api: Api object for making requests to the target RegScale installation
    :param list existing_controls: existing security controls from target of catalog updates in RegScale installation
    :param list new_controls: controls extracted from the update source catalog
    :param list track_changes: list containing a record of changes that were noted between old and new, for reporting
    :param bool dryrun: True if dry run (don't make changes to data just report changes) or False (make updates)
    :return: List of archived controls
    :rtype: list
    """

    logger.info("Checking for updates within Security Control fields.")
    (
        existing_map,
        new_map,
        archive_ids_set,
        create_ids_set,
        update_ids_set,
    ) = define_operations(id_key_name="controlId", old_records=existing_controls, new_records=new_controls)

    # PROCESS UPDATES
    # ignore localized system metadata & ids when comparing new and old
    ignore_keys = {
        "dateCreated",
        "createdBy",
        "createdById",
        "lastUpdatedBy",
        "lastUpdatedById",
        "dateLastUpdated",
        "uuid",
        "id",
        "tenantsId",
        # "catalogueID",
        "controlId",
        "controlType",
    }
    check_controls_do_updates(api, dryrun, existing_map, ignore_keys, new_map, track_changes, update_ids_set)

    # CREATE NEW
    archived = []  # don't upload a control if it's already in archived status
    check_controls_do_create(api, archived, create_ids_set, dryrun, existing_controls, new_map, track_changes)

    # PROCESS ARCHIVED
    check_controls_do_archived(api, archive_ids_set, dryrun, existing_map, track_changes)

    # The only purpose of this section is to keep a running list of controlIds that were archived. Later we want to make
    # sure that any child records inherit the archival status of their parent control.
    archived_controls = []
    for change in track_changes:
        if change["field"] == "archived" and change["new_value"] is True:
            archived_controls.append(existing_map[change["id"]]["id"])  # note id of control w/ archived updated to true
    return archived_controls


def check_controls_do_archived(
    api: Api, archive_ids_set: set, dryrun: bool, existing_map: dict, track_changes: list
) -> None:
    """
    Function to archive controls that were found in the old catalog but not in the new catalog

    :param Api api: Api object for making requests to the target RegScale installation
    :param set archive_ids_set: set of IDs for records identified for archiving
    :param bool dryrun: True for do a dryrun, false for not a dry run
    :param dict existing_map: Contains the existing records in a hashmap of identifiers and complete records
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    if len(archive_ids_set) > 0:
        logger.info(
            "Checking for security controls in the old version of catalog which do not exist in the new version."
        )
        for control_id in archive_ids_set:
            handle_control_archiving(api, control_id, dryrun, existing_map, track_changes)


def handle_control_archiving(api: Api, control_id: int, dryrun: bool, existing_map: dict, track_changes: list) -> None:
    """
    Function to archive a control that was found in the old catalog but not in the new catalog

    :param Api api: Api object for making requests to the target RegScale installation
    :param int control_id: ID of the control to be archived
    :param bool dryrun: True for do a dryrun, false for not a dry run
    :param dict existing_map: Contains the existing records in a hashmap of identifiers and complete records
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    if existing_map[control_id]["archived"] is False:  # skip if already archived status
        archive_record(
            existing_record=existing_map[control_id],
            track_changes=track_changes,
            record_id=control_id,
            record_type=SECURITY_CONTROL,
            justification="Control from old catalog no longer found in new catalog.",
        )
        if not dryrun:  # but ONLY if this is NOT a dry run
            update_archived_status(api, control_id, existing_map)


def update_archived_status(api: Api, control_id: int, existing_map: dict) -> None:
    """
    Function to update the archived status of a control in the RegScale installation

    :param Api api: Api object for making requests to the target RegScale installation
    :param int control_id: ID of the control to be archived
    :param dict existing_map: Contains the existing records in a hashmap of identifiers and complete records
    :rtype: None
    """
    existing_map[control_id]["archived"] = True
    response = api.put(
        url=urljoin(
            api.config["domain"],
            API_SECURITY_CONTROLS_ + str(existing_map[control_id]["id"]),
        ),
        json=existing_map[control_id],
    )
    if not response.ok:
        logger.error(f"Response {response.status_code} - Trouble archiving with URL: {response.request.url}")
    else:
        logger.info(f'Archived Control #{existing_map[control_id]["id"]}: {existing_map[control_id]["controlId"]}')


def check_controls_do_create(
    api: Api,
    archived: list,
    create_ids_set: set,
    dryrun: bool,
    existing_controls: list,
    new_map: dict,
    track_changes: list,
) -> None:
    """
    Function to create new controls that were found in the new catalog but not in the old catalog

    :param Api api: Api object for making requests to the target RegScale installation
    :param list archived: list of control IDs that were archived
    :param set create_ids_set: set of IDs for records identified for creation
    :param bool dryrun: True for do a dryrun, false for not a dry run
    :param list existing_controls: list of existing controls
    :param dict new_map: hashmap of identifiers and complete records
    :param list track_changes: list containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    for control_id in create_ids_set:
        if new_map[control_id]["archived"] is True:
            archived.append(control_id)
    for control_id in archived:
        create_ids_set.remove(control_id)
    if len(create_ids_set) > 0:
        logger.info(
            f"Found the following security controls in the new version of catalog which do not exist in the old "
            f"version. These will be created as new controls: {create_ids_set} "
        )
        for control_id in create_ids_set:
            track_changes.append(
                {
                    "operation": "create new record",
                    "record_type": SECURITY_CONTROL,
                    "id": control_id,
                    "field": "",
                    "old_value": "",
                    "new_value": "",
                    "justification": "New Security Control found which does not exist in old catalog.",
                }
            )
            #
            if dryrun is False:  # only post updates if this is not a dry run
                new_map[control_id]["catalogueID"] = existing_controls[0]["catalogueID"]
                response = api.post(
                    url=urljoin(api.config["domain"], API_SECURITY_CONTROLS_),
                    json=new_map[control_id],
                )
                if not response.ok:
                    logger.error(f"Response {response.status_code} - Trouble posting to URL: {response.request.url}")
                else:
                    response_id = json.loads(response.content)["id"]
                    logger.info(f'Created Control {new_map[control_id]["controlId"]} (ID# {response_id})')
                    new_map[control_id]["id"] = response_id
                    existing_controls.append(new_map[control_id])


def check_controls_do_updates(
    api: Api,
    dryrun: bool,
    existing_map: dict,
    ignore_keys: set,
    new_map: dict,
    track_changes: list,
    update_ids_set: set,
) -> None:
    """
    Function to update existing controls that were found in both the old and new catalogs

    :param Api api: Api object for making requests to the target RegScale installation
    :param bool dryrun: True for do a dryrun, false for not a dry run
    :param dict existing_map: Contains the existing records in a hashmap of identifiers and complete records
    :param set ignore_keys: set of keys to ignore when comparing old and new records
    :param dict new_map: Contains the new records in a hashmap of identifiers and complete records
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :param set update_ids_set: Set of IDs for records identified for update
    :rtype: None
    """
    for control_id in update_ids_set:
        current_changes_count = len(track_changes)  # note size of track changes before updates
        update_record(
            existing_record=existing_map[control_id],
            new_record=new_map[control_id],
            ignore_keys=ignore_keys,
            record_id=control_id,
            record_type=SECURITY_CONTROL,
            track_changes=track_changes,
        )
        if current_changes_count < len(track_changes):  # if any changes were recorded for this control
            if dryrun is False:  # but ONLY if this is NOT a dry run
                response = api.put(
                    url=urljoin(
                        api.config["domain"],
                        API_SECURITY_CONTROLS_ + str(existing_map[control_id]["id"]),
                    ),
                    json=existing_map[control_id],
                )
                if not response.ok:
                    logger.error(
                        f"Response {response.status_code} -(276) Trouble updating to URL: {response.request.url}"
                    )
                else:
                    logger.info(
                        f'Updated Control #{existing_map[control_id]["id"]}: {existing_map[control_id]["controlId"]}'
                    )


def check_child_records(
    api: Api,
    archived_controls: list,
    existing_records: list,
    new_records: list,
    track_changes: list,
    dryrun: bool,
    record_type: str,
    record_id_field: str,
    endpoint: str,
    existing_controls: list,
    new_controls: list,
) -> None:
    """
    Check child records of controls for updates, archivals, or new records

    :param Api api: Api object for making requests to the target RegScale installation
    :param list archived_controls: list of controls identified for archival
    :param list existing_records: list of dicts for existing records from regscale installation
    :param list new_records:  list of dicts for records of corresponding type from new source of updates
    :param list track_changes: list containing a record of changes that were noted between old and new, for reporting
    :param bool dryrun: True for yes a dry run False for no not a dry run (real updates)
    :param str record_type: Indicates if updating objectives, parameters, tests, or CCIs
    :param str record_id_field: name of id field appropriate for the record type
    :param str endpoint: the API endpoint associated with this record type
    :param list existing_controls: list of existing controls
    :param list new_controls:  list of new controls from update source
    :rtype: None
    """
    logger.info(f"Now checking {record_type}s for new data.")
    (
        existing_map,
        new_map,
        archive_ids_set,
        create_ids_set,
        update_ids_set,
    ) = define_operations(
        id_key_name=record_id_field,
        old_records=existing_records,
        new_records=new_records,
    )

    # PROCESS UPDATES
    # ignore localized system metadata & ids when comparing new and old
    ignore_keys = {
        "dateCreated",
        "createdBy",
        "createdById",
        "lastUpdatedBy",
        "lastUpdatedById",
        "dateLastUpdated",
        "uuid",
        "id",
        "tenantsId",
        "securityControlId",
        record_id_field,
    }
    check_child_do_updates(
        api,
        archived_controls,
        dryrun,
        endpoint,
        existing_map,
        ignore_keys,
        new_map,
        record_type,
        track_changes,
        update_ids_set,
    )

    # PROCESS ARCHIVES
    check_child_do_archives(api, archive_ids_set, dryrun, endpoint, existing_map, record_type, track_changes)

    # CREATE NEW
    check_child_do_create(
        api,
        create_ids_set,
        dryrun,
        endpoint,
        existing_controls,
        new_controls,
        new_map,
        record_type,
        track_changes,
    )


def check_child_do_create(
    api: Api,
    create_ids_set: set,
    dryrun: bool,
    endpoint: str,
    existing_controls: list,
    new_controls: list,
    new_map: dict,
    record_type: str,
    track_changes: list,
) -> None:
    """
    Function to create new child records that were found in the new catalog but not in the old catalog

    :param Api api: Api object for making requests to the target RegScale installation
    :param set create_ids_set: list of ids that were identified for creating a new record
    :param bool dryrun: True for yes a dry run False for no not a dry run (real updates)
    :param str endpoint: the API endpoint associated with this record type
    :param list existing_controls: list of dicts for existing controls from regscale installation
    :param list new_controls: list of dicts for controls of corresponding type from new source of updates
    :param dict new_map: hashmap of identifiers and records
    :param str record_type: Indicates if updating objectives, parameters, tests, or CCIs
    :param list track_changes: dict containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    if len(create_ids_set) > 0:
        logger.info(
            f"Looking for {record_type}s in the new version of catalog which do not exist in the old "
            f"version. These would be created as new {record_type}s."
        )
        for identifier in create_ids_set:
            # Begin hacky solutions to mapping newly created child records to correct parents :(
            control_mapped = hacky_fix_for_catalog_data_structure(existing_controls, identifier, new_controls, new_map)
            # End of said hacky solution
            do_create(
                api,
                control_mapped,
                dryrun,
                endpoint,
                identifier,
                new_map,
                record_type,
                track_changes,
            )


def do_create(
    api: Api,
    control_mapped: bool,
    dryrun: bool,
    endpoint: str,
    identifier: int,
    new_map: dict,
    record_type: str,
    track_changes: list,
) -> None:
    """
    Function to create new child records that were found in the new catalog but not in the old catalog

    :param Api api: Api object for making requests to the target RegScale installation
    :param bool control_mapped: True if the control was mapped to a new control ID, False if not
    :param bool dryrun: True for yes a dry run False for no not a dry run (real updates)
    :param str endpoint: the API endpoint associated with this record type
    :param int identifier: the identifier of the record to be created
    :param dict new_map: hashmap of identifiers and records
    :param str record_type: The type of record being created, used for reporting
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    if control_mapped is True and new_map[identifier]["archived"] is False:
        track_changes.append(
            {
                "operation": "create new record",
                "record_type": record_type,
                "id": identifier,
                "field": "",
                "old_value": "",
                "new_value": "",
                "justification": f"New {record_type} found which did not exist in old catalog.",
            }
        )
        if dryrun is False:
            response = api.post(url=urljoin(api.config["domain"], endpoint), json=new_map[identifier])
            if not response.ok:
                logger.error(f"{response.status_code} - Trouble creating new record with: {response.request.url}")
            else:
                logger.info(f'Created {record_type} {identifier} ID {json.loads(response.content)["id"]})')
    else:
        logger.warning(
            f"Skipped creating {record_type} {identifier}. Either record or it's parent control is archived."
        )


def hacky_fix_for_catalog_data_structure(
    existing_controls: list,
    identifier: Union[str, int],
    new_controls: list,
    new_map: dict,
) -> bool:
    """
    Function to map newly created controls to the previously existing controls

    :param list existing_controls:
    :param Union[str, int] identifier: Unique identifier for the record
    :param list new_controls: list of new controls
    :param dict new_map: dict containing ids and records
    :return: Whether the control was mapped to a new control ID
    :rtype: bool
    """
    control_mapped = False
    for control in new_controls:
        if control["id"] == new_map[identifier]["securityControlId"]:
            control_match_field = control["controlId"]

            for old_control in existing_controls:
                if control_match_field == old_control["controlId"]:
                    new_map[identifier]["securityControlId"] = old_control["id"]
                    control_mapped = True
    return control_mapped


def check_child_do_archives(
    api: Api,
    archive_ids_set: set,
    dryrun: bool,
    endpoint: str,
    existing_map: dict,
    record_type: str,
    track_changes: list,
) -> None:
    """
    Function to archive child records that were found in the old catalog but not in the new catalog

    :param Api api: Api object for making requests to the target RegScale installation
    :param set archive_ids_set: set of IDs for records identified for archiving
    :param bool dryrun: True for do a dryrun, false for not a dry run
    :param str endpoint: the API endpoint associated with this record type
    :param dict existing_map: Contains the existing records in a hashmap of identifiers and complete records
    :param str record_type: Indicates if updating objectives, parameters, tests, or CCIs
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    if len(archive_ids_set) > 0:
        logger.info(
            f"Checking for {record_type}s in the old version of catalog which do not exist in the new "
            f"version. These would be archived."
        )
        for identifier in archive_ids_set:
            handle_archive_records(api, identifier, dryrun, endpoint, existing_map, record_type, track_changes)


def handle_archive_records(
    api: Api, identifier: int, dryrun: bool, endpoint: str, existing_map: dict, record_type: str, track_changes: list
) -> None:
    """
    Function to archive child records that were found in the old catalog but not in the new catalog

    :param Api api: Api object for making requests to the target RegScale installation
    :param int identifier: ID of the record to be archived
    :param bool dryrun: True for do a dryrun, false for not a dry run
    :param str endpoint: the API endpoint associated with this record type
    :param dict existing_map: Contains the existing records in a hashmap of identifiers and complete records
    :param str record_type: Indicates if updating objectives, parameters, tests, or CCIs
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    if existing_map[identifier]["archived"] is False:  # skip if already archived status
        archive_record(
            existing_record=existing_map[identifier],
            track_changes=track_changes,
            record_id=identifier,
            record_type=record_type,
            justification=f"{record_type} from old catalog no longer found in new catalog.",
        )
        if not dryrun:  # but ONLY if this is NOT a dry run
            update_archive_status(api, identifier, endpoint, existing_map, record_type)


def update_archive_status(api: Api, identifier: int, endpoint: str, existing_map: dict, record_type: str) -> None:
    """
    Function to update the archived status of a child record in the RegScale installation

    :param Api api: Api object for making requests to the target RegScale installation
    :param int identifier: ID of the record to be archived
    :param str endpoint: the API endpoint associated with this record type
    :param dict existing_map: Contains the existing records in a hashmap of identifiers and complete records
    :param str record_type: Indicates if updating objectives, parameters, tests, or CCIs
    :rtype: None

    """

    existing_map[identifier]["archived"] = True
    response = api.put(
        url=urljoin(
            api.config["domain"],
            endpoint + str(existing_map[identifier]["id"]),
        ),
        json=existing_map[identifier],
    )
    if not response.ok:
        logger.error(f"Response {response.status_code} - Trouble archiving with URL: {response.request.url}")
    else:
        logger.info(f'Archived {record_type} #{existing_map[identifier]["id"]}: {identifier}')


def check_child_do_updates(
    api: Api,
    archived_controls: list,
    dryrun: bool,
    endpoint: str,
    existing_map: dict,
    ignore_keys: set,
    new_map: dict,
    record_type: str,
    track_changes: list,
    update_ids_set: set,
) -> None:
    """
    Function to update existing child records that were found in both the old and new catalogs

    :param Api api: Api object for making requests to the target RegScale installation
    :param list archived_controls: list of archived controls
    :param bool dryrun: True for yes a dry run False for no not a dry run (real updates)
    :param str endpoint: the API endpoint associated with this record type
    :param dict existing_map: hashmap of identifiers and complete records for existing child records
    :param set ignore_keys: set of field keys to be ignored for purposes of comparison
    :param dict new_map: hashmap of identifier and complete records for new source of update data
    :param str record_type: Indicates if updating objectives, parameters, tests, or CCIs
    :param list track_changes: list containing a record of changes that were noted between old and new, for reporting
    :param set update_ids_set: set of ids to be updated
    :rtype: None
    """
    for identifier in update_ids_set:
        current_changes_count = len(track_changes)
        update_record(
            existing_record=existing_map[identifier],
            new_record=new_map[identifier],
            ignore_keys=ignore_keys,
            record_id=identifier,
            record_type=record_type,
            track_changes=track_changes,
        )
        # If the parent control was archived, should also archive all child objectives associated with that control
        handle_archived(archived_controls, existing_map, identifier, record_type, track_changes)
        #
        if current_changes_count < len(track_changes):  # if changes recorded for this objective
            if dryrun is False:  # but ONLY if this is NOT a dry run
                response = api.put(
                    url=urljoin(
                        api.config["domain"],
                        f"{endpoint}/{existing_map[identifier]['id']}",
                    ),
                    json=existing_map[identifier],
                )
                if not response.ok:
                    logger.error(f"Response {response.status_code} - Trouble updating to URL: {response.request.url}")
                else:
                    logger.info(f'Updated {record_type} #{existing_map[identifier]["id"]}: {identifier}')


def handle_archived(
    archived_controls: list,
    existing_map: dict,
    identifier: Union[int, str],
    record_type: str,
    track_changes: list,
) -> None:
    """
    Function to handle archiving of child records when original control is archived

    :param list archived_controls: list of archived controls
    :param dict existing_map: hashmap of identifiers and complete records for existing child records
    :param Union[int, str] identifier: unique identifier for the record
    :param str record_type: Indicates if updating objectives, parameters, tests, or CCIs
    :param list track_changes: list containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    for control_id in archived_controls:
        if (
            existing_map[identifier]["securityControlId"] == control_id
            and existing_map[identifier]["archived"] is False
        ):
            logger.info(f"Inheriting archived status of parent control for {record_type}: {identifier}")
            archive_record(
                existing_record=existing_map[identifier],
                track_changes=track_changes,
                record_id=identifier,
                record_type=record_type,
                justification="Archived because parent control was archived",
            )


def check_catalog_metadata(
    api: Api,
    existing_catalog: dict,
    new_version_catalog: dict,
    track_changes: list,
    dryrun: bool,
) -> None:
    """
    Function to check catalog metadata for updates

    :param Api api: Api object for making requests to the target RegScale installation
    :param dict existing_catalog: catalog being targeted for updates, retrieved from regscale installation
    :param dict new_version_catalog: catalog being
    :param list track_changes: dict containing a record of changes that were noted between old and new, for reporting
    :param bool dryrun: True for yes a dry run False for no not a dry run (real updates)
    :rtype: None
    """
    current_changes_count = len(track_changes)
    # ignore localized system metadata, PIDs, + child records handled elsewhere. archived doesn't apply to catalog
    ignore_keys = {
        "dateCreated",
        "createdBy",
        "createdById",
        "lastUpdatedById",
        "lastUpdatedBy",
        "dateLastUpdated",
        "tenantsId",
        "uuid",
        "id",
        "securityControls",
        "objectives",
        "tests",
        "parameters",
        "ccis",
        "archived",
    }
    update_record(
        existing_record=existing_catalog,
        new_record=new_version_catalog,
        ignore_keys=ignore_keys,
        record_id=existing_catalog["uuid"],
        record_type="catalog",
        track_changes=track_changes,
    )
    if current_changes_count < len(track_changes):  # if changes recorded in this section
        del existing_catalog["securityControls"]
        del existing_catalog["parameters"]
        del existing_catalog["objectives"]
        del existing_catalog["tests"]
        if dryrun is False:  # ONLY if this is NOT a dry run
            response = api.put(
                url=urljoin(api.config["domain"], API_CATALOGUES_ + str(existing_catalog["id"])),
                json=existing_catalog,
            )
            if not response.ok:
                logger.error(f"Response {response.status_code} - 424 Trouble updating catalog: {response.request.url}")
            else:
                logger.info(f'Updated catalog metadata for #{existing_catalog["id"]}: {existing_catalog["title"]}')


# -------------------------------------------------------------------------------------------------------------------- #
# Begin Utility Functions


def define_operations(
    id_key_name: str, old_records: list[dict], new_records: list[dict]
) -> tuple[dict, dict, set, set, set]:
    """
    Uses set logic to identify which identifiers should be created, updated, or archived (soft delete).
    Works the same for all record types: control, objective, parameter, test, cci

    :param str id_key_name: name of the field that contains the unique identifier for the record type
    :param list[dict] old_records: list of dicts for existing records from RegScale installation
    :param list[dict] new_records: list of dicts for records of corresponding type from new source of updates
    :return: existing_map, new_map, archive_ids_set, create_ids_set, update_ids_set
    :rtype: tuple[dict, dict, set, set, set]
    """
    existing_map = {d[id_key_name]: d for d in old_records}
    existing_id_set = set(existing_map.keys())

    new_map = {d[id_key_name]: d for d in new_records}
    new_id_set = set(new_map.keys())
    archive_ids_set = existing_id_set - new_id_set  # archive objects found in old version of catalog but not in the new
    create_ids_set = new_id_set - existing_id_set  # create as new objects found in new but not old
    update_ids_set = existing_id_set & new_id_set  # update existing if found in both old and new

    return existing_map, new_map, archive_ids_set, create_ids_set, update_ids_set


def update_record(
    existing_record: dict,
    new_record: dict,
    ignore_keys: set,
    record_id: int,
    record_type: str,
    track_changes: list,
) -> None:
    """
    Function to update existing RegScale records with new data

    :param dict existing_record: Existing record from RegScale to be updated
    :param dict new_record: New record from update source to be used for updating existing record
    :param set ignore_keys: Keys to ignore when comparing old and new records
    :param int record_id: Record ID of the record being updated in RegScale
    :param str record_type: Type of record being updated
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    existing_keys = set(existing_record.keys())
    new_keys = set(new_record.keys())
    #
    update_record_latest_field_data(
        existing_keys,
        existing_record,
        ignore_keys,
        new_keys,
        new_record,
        record_id,
        record_type,
        track_changes,
    )

    #
    update_record_new_fields(
        existing_keys,
        existing_record,
        ignore_keys,
        new_keys,
        new_record,
        record_id,
        record_type,
        track_changes,
    )

    #
    update_record_fields_removed(
        existing_keys,
        existing_record,
        ignore_keys,
        new_keys,
        record_id,
        record_type,
        track_changes,
    )


def check_for_truncation(value: Any, char_limit: Optional[int] = 100) -> Any:
    """
    Function to check if a string is too long to be stored in RegScale and will truncate it if so

    :param Any value: The value to be checked for truncation
    :param Optional[int] char_limit: The character limit for the field in RegScale, defaults to 100
    :return: Truncated string if necessary, otherwise the original value
    :rtype: Any
    """
    if isinstance(value, str) and len(value) > char_limit:
        return f"{value[:char_limit]}... [truncated]"
    else:
        return value


def update_record_fields_removed(
    existing_keys: set,
    existing_record: dict,
    ignore_keys: set,
    new_keys: set,
    record_id: int,
    record_type: str,
    track_changes: list,
) -> None:
    """
    Function to update existing RegScale records with new data

    :param set existing_keys: Set of keys for the existing record
    :param dict existing_record: Existing record from RegScale to be updated
    :param set ignore_keys: Set of keys to ignore when comparing old and new records
    :param set new_keys: Set of keys for the new record
    :param int record_id: Record ID of the record being updated in RegScale
    :param str record_type: Type of record being updated
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    for key in (existing_keys - new_keys) - ignore_keys:  # fields that were in old version but not new are set to null
        if existing_record[key] != "" and existing_record[key] is not None:  # would ignore if it field already empty
            track_changes.append(
                {
                    "operation": "update",
                    "record_type": record_type,
                    "id": record_id,
                    "field": key,
                    "old_value": check_for_truncation(existing_record[key]),
                    "new_value": "",
                    "justification": "field no longer exists in new version",
                }
            )
            existing_record[key] = None


def update_record_new_fields(
    existing_keys: set,
    existing_record: dict,
    ignore_keys: set,
    new_keys: set,
    new_record: dict,
    record_id: int,
    record_type: str,
    track_changes: list,
) -> None:
    """
    Function to update existing RegScale records with new data

    :param set existing_keys: Set of keys for the existing record
    :param dict existing_record: Existing record from RegScale to be updated
    :param set ignore_keys: Set of keys to ignore when comparing old and new records
    :param set new_keys: Set of keys for the new record
    :param dict new_record: New record from update source to be used for updating existing record
    :param int record_id: Record ID of the record being updated in RegScale
    :param str record_type: Type of record being updated
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    for key in (new_keys - existing_keys) - ignore_keys:  # are any new fields present that were not in the old version?
        # ----
        track_changes.append(
            {
                "operation": "update",
                "record_type": record_type,
                "id": record_id,
                "field": key,
                "old_value": "",
                "new_value": check_for_truncation(new_record[key]),
                "justification": f"new field added to this {record_type} in latest version",
            }
        )  # if so record the change
        existing_record[key] = new_record[
            key
        ]  # update the existing version of record with field and data from update source


def update_record_latest_field_data(
    existing_keys: set,
    existing_record: dict,
    ignore_keys: set,
    new_keys: set,
    new_record: dict,
    record_id: int,
    record_type: str,
    track_changes: list,
) -> None:
    """
    Function to update existing RegScale records with new data

    :param set existing_keys: Set of keys for the existing record
    :param dict existing_record: Existing record from RegScale to be updated
    :param set ignore_keys: Set of keys to ignore when comparing old and new records
    :param set new_keys: Set of keys for the new record
    :param dict new_record: New record from update source to be used for updating existing record
    :param int record_id: Record ID of the record being updated in RegScale
    :param str record_type: Type of record being updated
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    for key in (existing_keys & new_keys) - ignore_keys:  # where same keys in both, check each field for new data
        if (
            existing_record[key] != new_record[key]
        ):  # if current version data different the new version data for a field
            track_changes.append(
                {
                    "operation": "archive" if key == "archived" else "update",
                    "record_type": record_type,
                    "id": record_id,
                    "field": key,
                    "old_value": check_for_truncation(existing_record[key]),
                    "new_value": check_for_truncation(new_record[key]),
                    "justification": "field data has changed",
                }
            )  # then record change
            existing_record[key] = new_record[key]  # and overwrite existing with new data for this field


def archive_record(
    existing_record: dict,
    track_changes: list,
    record_id: int,
    record_type: str,
    justification: str,
) -> None:
    """
    Function to archive a record

    :param dict existing_record: Record to be archived
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :param int record_id: Record ID of the record being archived in RegScale
    :param str record_type: Type of record being archived
    :param str justification: Justification for archiving the record
    :rtype: None
    """
    existing_record["archived"] = True
    track_changes.append(
        {
            "operation": "archive",
            "record_type": record_type,
            "id": record_id,
            "field": "archived",
            "old_value": False,
            "new_value": True,
            "justification": justification,
        }
    )


def write_outcomes_to_file(changes: list, output_filename: str) -> None:
    """
    Function to write out the changes to a CSV file

    :param list changes: List of changes to be written to file
    :param str output_filename: Name of the file to be written to
    :rtype: None
    """
    logger.info(f"\nWriting change report to file: {output_filename}")
    with open(output_filename, "w", newline="") as csvfile:
        fieldnames = [
            "operation",
            "record_type",
            "id",
            "field",
            "old_value",
            "new_value",
            "justification",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for change in changes:
            writer.writerow(change)
