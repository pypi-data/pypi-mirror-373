#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2nd iteration to add functionality to upgrade application catalog information via API."""

import csv
import json
import sys
from datetime import datetime
from os import path
from pathlib import Path
from typing import Any, Union, List, Type
from urllib.parse import urljoin

from requests import Response

from regscale.core.app import create_logger
from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import error_and_exit
from regscale.core.app.utils.catalog_utils.common import parentheses_to_dot
from regscale.core.utils.date import datetime_str
from regscale.models import regscale_models
from regscale.models.regscale_models.regscale_model import T

SECURITY_CONTROL = "security control"
logger = create_logger()
API_SECURITY_CONTROLS_ = "api/SecurityControls/"
API_CATALOGUES_ = "api/catalogues/"
master_catalog_list_url = "https://regscaleblob.blob.core.windows.net/catalogs/master_catalogue_list_final.json"


def display_menu(include_meta: bool = False):
    """
    Initial function called by the click command. Fires off functions to collect data for comparison and trigger updates

    :param bool include_meta: True if including metadata in the update checks, False if not
    """
    catalog_number_to_update = select_installed_catalogs()
    existing_catalog = load_existing_catalog(catalog_number_to_update)
    update_sourcefile = get_update_file(existing_catalog)
    if not update_sourcefile:
        error_and_exit("No valid source file found. Exiting program.")
    else:
        new_version_catalog_data = load_updated_catalog(update_sourcefile)
        if new_version_catalog_data:
            dryrun = confirm_actions(new_version_catalog_data, existing_catalog)
            process_catalog_update(
                new_version_catalog=new_version_catalog_data,
                existing_catalog=existing_catalog,
                dryrun=dryrun,
                include_meta=include_meta,
            )


def select_installed_catalogs() -> int:
    """
    Fetches the list of currently installed catalogs on the target RegScale installation so user can select for update

    :return: catalog number on the target installation that user has selected for update
    :rtype: int
    """
    catalogs = regscale_models.Catalog.get_list()
    if not catalogs:
        error_and_exit("No catalogs found in RegScale installation. Exiting program.")
    ids = [x.id for x in catalogs]

    while True:
        for catalog in catalogs:
            print(str(catalog.id).rjust(10, " ") + ": " + catalog.title)
        catalog_number_to_update = input(
            "\nEnter the # of the catalog you wish to update on your target system, or type STOP to exit: "
        )
        if catalog_number_to_update.isdigit() and int(catalog_number_to_update) in ids:
            return int(catalog_number_to_update)
        elif catalog_number_to_update.lower() == "stop":
            logger.info("Exiting program. Goodbye!")
            sys.exit(0)
        else:
            logger.warning("\nNot a valid catalog ID number. Please try again:\n")


def get_update_file(existing_catalog: regscale_models.Catalog) -> bytes:
    """
    Retrieves the source file for the catalog update file source, whether online or by file on disk

    :param regscale_models.Catalog existing_catalog: existing catalog object from target RegScale installation
    :return: catalog update source file as bytes
    :rtype: bytes
    """

    uuid = existing_catalog.uuid
    while True:
        update_sourcefile = input(
            "\nEnter the filepath and name of the new version of the catalog file you wish to use,\n or "
            "press ENTER to automatically pull the latest version from RegScale servers: "
        )
        if update_sourcefile.lower() == "stop":
            logger.info("Exiting program. Goodbye!")
            sys.exit(0)
        elif update_sourcefile == "" and uuid:
            logger.info("Checking online for latest file version..")
            return find_update_online(uuid)
        elif path.isfile(update_sourcefile):
            logger.info("Located input file.")
            return read_update_from_disk(update_sourcefile)
        else:
            logger.warning("\nNot a valid source input. Type 'STOP' to exit, or make a valid entry.")


def find_update_online(uuid: str) -> bytes:
    """
    Receives the UUID of the original catalog that is to be updated, and searches for a matching uuid from the master
    catalog list found on the anonymous read azure blob storage

    :param str uuid: uuid string from the original catalog, used to find a matching source for update
    :return: byte string of update source catalog file retrieved online from azure blob storage
    :rtype: bytes
    """
    api = Api()
    try:
        response = api.get(url=master_catalog_list_url, headers={})
        if response.status_code != 200:
            error_and_exit("Failed to fetch catalogs. Server responded with status code: " + str(response.status_code))
        master_catalogs = json.loads(response.text)
        for catalog in master_catalogs["catalogues"]:
            if catalog["metadata"]["uuid"] == uuid:
                logger.info("Found current version of catalog. Downloading now.")
                return api.get(catalog["link"], headers={}).content
        error_and_exit("Matching catalog not found for UUID: " + uuid)
    except Exception as e:
        error_and_exit("An error occurred while fetching the update online: " + str(e))


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
        else:  # if this is old format of catalog
            new_format_updated_catalog = {}
            catalog = updated_catalog.get("catalog", updated_catalog.get("catalogue"))
            for key in catalog.keys():
                new_format_updated_catalog[key] = catalog[key]

            return new_format_updated_catalog
    except Exception as e:
        error_and_exit(f"Error encountered. Unable to continue: {e}")


def load_existing_catalog(catalog_number_to_update: int) -> regscale_models.Catalog:
    """
    Loads the existing catalog in the database that is intended to be replaced, matching format of new catalog ingest

    :param int catalog_number_to_update: RegScale catalog ID to be updated in the local RegScale installation
    :return: Catalog object containing the entire catalog structure in same format as catalog import files
    :rtype: regscale_models.Catalog
    """
    existing_catalog = regscale_models.Catalog.get_object(catalog_number_to_update)
    if not existing_catalog:
        error_and_exit(f"Catalog {catalog_number_to_update} not found in RegScale installation. Exiting program.")

    logger.info("Loading data from existing version of catalog on RegScale installation.")
    security_controls: list[regscale_models.SecurityControl] = regscale_models.SecurityControl.get_all_by_parent(
        catalog_number_to_update, regscale_models.Catalog.get_module_string()
    )
    existing_catalog.securityControls = security_controls

    return existing_catalog


def confirm_actions(new_version_catalog: dict, existing_catalog: regscale_models.Catalog) -> bool:
    """
    Display title of existing catalog and update source for confirmation. Also determines if doing a dry run is true
    or false

    :param dict new_version_catalog: catalog used as update source
    :param regscale_models.Catalog existing_catalog: existing catalog pulled from target installation
    :return: True for do a dry run or false to NOT do a dry run (make updates for real)
    :rtype: bool
    """

    logger.info(
        f"Updating: {str(existing_catalog.id).rjust(8, ' ')} - {existing_catalog.title}"
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


def process_catalog_update(
    new_version_catalog: dict, existing_catalog: regscale_models.Catalog, dryrun: bool, include_meta: bool = False
) -> None:
    """
    Initiates catalog update checks and processing on each record type within the catalog.

    :param dict new_version_catalog: update source catalog
    :param regscale_models.Catalog existing_catalog: existing catalog to be updated, pulled from RegScale installation
    :param bool dryrun: True if a dry run (don't do updates for real, just report changes) or false (do updates)
    :param bool include_meta: True if including metadata in the update checks, False if not
    :rtype: None
    """
    output_filename = f"catalog_{existing_catalog.id}_updates_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
    track_changes: list[Any] = []

    # Normalize control ids
    for control in new_version_catalog["securityControls"]:
        control["controlId"] = parentheses_to_dot(control["controlId"])

    for control in existing_catalog.securityControls:
        control.controlId = parentheses_to_dot(control.controlId)

    check_controls(
        catalog_id=existing_catalog.id,
        existing_controls=existing_catalog.securityControls,
        new_controls=new_version_catalog["securityControls"],
        track_changes=track_changes,
        dryrun=dryrun,
    )
    if include_meta:
        check_catalog_metadata(
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
    catalog_id: int,
    existing_controls: list[regscale_models.SecurityControl],
    new_controls: list,
    track_changes: list,
    dryrun: bool,
) -> list:
    """
    Manages several function for checking which controls may need to be updated, archived, or created.

    :param int catalog_id: ID of the catalog being updated
    :param list[regscale_models.SecurityControl] existing_controls: existing security controls from target of catalog
    updates in RegScale installation
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
    for k, v in new_map.items():
        v["catalogueId"] = catalog_id
        v["archived"] = False
        v["isPublic"] = False

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
        "catalogueID",
        "controlId",
        "controlType",
        "tests",
        "objectives",
        "parameters",
        "ccis",
    }
    check_controls_do_updates(catalog_id, dryrun, existing_map, ignore_keys, new_map, track_changes, update_ids_set)

    # CREATE NEW
    archived: list[Any] = []  # don't upload a control if it's already in archived status
    check_controls_do_create(archived, create_ids_set, dryrun, existing_controls, new_map, track_changes)

    # PROCESS ARCHIVED
    check_controls_do_archived(archive_ids_set, dryrun, existing_map, track_changes)

    # The only purpose of this section is to keep a running list of controlIds that were archived. Later we want to make
    # sure that any child records inherit the archival status of their parent control.
    archived_controls = []
    for change in track_changes:
        if change["field"] == "archived" and change["new_value"] is True:
            archived_controls.append(existing_map[change["id"]].id)  # note id of control w/ archived updated to true

    for existing_control in existing_controls:
        # if existing_control.id in archived_controls or existing_control.controlId != "ac-3":
        #     continue
        # Update objectives
        existing_objectives: List[regscale_models.ControlObjective] = (
            regscale_models.ControlObjective.get_all_by_parent(
                existing_control.id, regscale_models.SecurityControl.get_module_string()
            )
        )
        new_objectives = new_map.get(existing_control.controlId, {}).get("objectives", [])
        for objective in new_objectives:
            objective["securityControlId"] = existing_control.id
            objective["archived"] = False
            objective["objectiveType"] = "statement"
        check_child_records(
            archived_controls=archived_controls,
            existing_records=existing_objectives,
            new_records=new_objectives,
            track_changes=track_changes,
            dryrun=dryrun,
            record_model=regscale_models.ControlObjective,
            record_id_field="name",
            existing_controls=existing_controls,
            new_controls=new_controls,
        )

        # Update parameters
        existing_parameters: list[regscale_models.ControlParameter] = (
            regscale_models.ControlParameter.get_all_by_parent(
                existing_control.id, regscale_models.SecurityControl.get_module_string()
            )
        )
        new_parameters = new_map.get(existing_control.controlId, {}).get("parameters", [])
        for parameter in new_parameters:
            parameter["securityControlId"] = existing_control.id
            parameter["archived"] = False
            parameter["isPublic"] = True
        check_child_records(
            archived_controls=archived_controls,
            existing_records=existing_parameters,
            new_records=new_parameters,
            track_changes=track_changes,
            dryrun=dryrun,
            record_model=regscale_models.ControlParameter,
            record_id_field="parameterId",
            existing_controls=existing_controls,
            new_controls=new_controls,
        )

        # Update tests
        existing_tests: List[regscale_models.ControlTest] = regscale_models.ControlTestPlan.get_all_by_parent(
            existing_control.id, regscale_models.SecurityControl.get_module_string()
        )
        new_tests = new_map.get(existing_control.controlId, {}).get("tests", [])
        for test in new_tests:
            test["securityControlId"] = existing_control.id
            test["archived"] = False
            test["isPublic"] = True
        check_child_records(
            archived_controls=archived_controls,
            existing_records=existing_tests,
            new_records=new_tests,
            track_changes=track_changes,
            dryrun=dryrun,
            record_model=regscale_models.ControlTestPlan,
            record_id_field="testId",
            existing_controls=existing_controls,
            new_controls=new_controls,
        )

        # Update CCIs
        existing_ccis: List[regscale_models.CCI] = regscale_models.CCI.get_all_by_parent(
            existing_control.id, regscale_models.SecurityControl.get_module_string()
        )
        new_ccis = new_map.get(existing_control.controlId, {}).get("ccis", [])
        for cci in new_ccis:
            cci["securityControlId"] = existing_control.id
            cci["archived"] = False
            cci["isPublic"] = True
            cci["publishDate"] = datetime_str(cci["publishDate"])
        check_child_records(
            archived_controls=archived_controls,
            existing_records=existing_ccis,
            new_records=new_ccis,
            track_changes=track_changes,
            dryrun=dryrun,
            record_model=regscale_models.CCI,
            record_id_field="name",
            existing_controls=existing_controls,
            new_controls=new_controls,
        )

    return archived_controls


def check_controls_do_archived(
    archive_ids_set: set,
    dryrun: bool,
    existing_map: dict,
    track_changes: list,
) -> None:
    """
    Function to archive controls that were found in the old catalog but not in the new catalog

    :param set archive_ids_set: set of IDs for records identified for
    :param bool dryrun: True for do a dryrun, false for not a dry run
    :param dict existing_map: hashmap of identifiers and complete records
    :param list track_changes: dict containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    if len(archive_ids_set) > 0:
        logger.debug(
            "Checking for security controls in the old version of catalog which do not exist in the new version."
        )
        for control_id in archive_ids_set:
            # if existing_map[control_id].archived is False:  # skip if already archived status
            archive_record(
                existing_record=existing_map[control_id],
                track_changes=track_changes,
                record_id=control_id,
                record_model=regscale_models.SecurityControl,
                justification="Control from old catalog no longer found in new catalog under {control_id}.",
            )
            if dryrun is False:  # but ONLY if this is NOT a dry run
                existing_map[control_id].archived = True
                logger.info(f"Archived Control #{existing_map[control_id].id}: {existing_map[control_id].controlId}")


def check_controls_do_create(
    archived: list,
    create_ids_set: set,
    dryrun: bool,
    existing_controls: list[regscale_models.SecurityControl],
    new_map: dict,
    track_changes: list,
) -> None:
    """
    Function to create new controls that were found in the new catalog but not in the old catalog

    :param list archived: list of control IDs that were archived
    :param set create_ids_set: set of IDs for records identified for creation
    :param bool dryrun: True for do a dryrun, false for not a dry run
    :param list[regscale_models.SecurityControl] existing_controls: list of existing controls
    :param dict new_map: hashmap of identifiers and complete records
    :param list track_changes: list containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    for control_id in create_ids_set:
        if new_map[control_id].get("archived", False) is True:
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
                    "record_model": regscale_models.SecurityControl.__name__,
                    "id": control_id,
                    "field": "",
                    "old_value": "",
                    "new_value": "",
                    "justification": "New Security Control found which does not exist in old catalog.",
                }
            )
            #
            if dryrun is False:  # only post updates if this is not a dry run
                new_control = regscale_models.SecurityControl(**new_map[control_id]).create()
                logger.info(f"Created Control {new_control.controlId} (ID# {new_control.id})")
                new_map[control_id]["id"] = new_control.id
                existing_controls.append(new_control)


def check_controls_do_updates(
    catalog_id: int,
    dryrun: bool,
    existing_map: dict,
    ignore_keys: set,
    new_map: dict,
    track_changes: list,
    update_ids_set: set,
) -> None:
    """
    Function to update existing controls that were found in both the old and new catalogs

    :param int catalog_id: ID of the catalog being updated
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
            record_model=regscale_models.SecurityControl,
            track_changes=track_changes,
        )
        if current_changes_count < len(track_changes):  # if any changes were recorded for this control
            if dryrun is False:  # but ONLY if this is NOT a dry run
                existing_map[control_id].catalogueId = catalog_id
                existing_map[control_id].save()


def remove_duplicate_records(
    records: list,
    id_field: str,
    track_changes: list,
    dryrun: bool,
    record_model: Type[T],
) -> list:
    """
    Remove duplicate records from a list based on a specified id field.

    :param list records: List of record dictionaries.
    :param str id_field: The field name to identify unique records.
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :param bool dryrun: True for do a dryrun, false for not a dry run
    :param Type[T] record_model: Indicates if updating objectives, parameters, tests, or CCIs
    :return: A list of records with duplicates removed.
    :rtype: list
    """
    seen = set()
    unique_records = []
    for record in records:
        identifier = getattr(record, id_field)
        if identifier in seen:
            track_changes.append(
                {
                    "operation": "duplicate record found",
                    "record_model": record_model.__name__,
                    "id": record.id,
                    "field": id_field,
                    "old_value": getattr(record, id_field),
                    "new_value": None,
                    "justification": "Removing duplicate record found in catalog.",
                }
            )
            logger.warning(f"Duplicate record found with {id_field} {identifier}, removing ID: {record.id}.")
            if not dryrun:
                record.delete()
        else:
            seen.add(identifier)
            unique_records.append(record)

    return unique_records


def check_child_records(
    archived_controls: list,
    existing_records: list,
    new_records: list,
    track_changes: list,
    dryrun: bool,
    record_model: Type[T],
    record_id_field: str,
    existing_controls: list[regscale_models.SecurityControl],
    new_controls: list,
) -> None:
    """
    Check child records of controls for updates, archival, or new records

    :param list archived_controls: list of controls identified for archival
    :param list existing_records: list of dicts for existing records from regscale installation
    :param list new_records:  list of dicts for records of corresponding type from new source of updates
    :param list track_changes: list containing a record of changes that were noted between old and new, for reporting
    :param bool dryrun: True for yes a dry run False for no not a dry run (real updates)
    :param Type[T] record_model: Indicates if updating objectives, parameters, tests, or CCIs
    :param str record_id_field: name of id field appropriate for the record type
    :param list[regscale_models.SecurityControl] existing_controls: list of existing controls
    :param list new_controls:  list of new controls from update source
    :rtype: None
    """
    logger.debug(f"Now checking {record_model.__name__}s for existing data.")
    existing_records = remove_duplicate_records(existing_records, record_id_field, track_changes, dryrun, record_model)

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
        archived_controls,
        dryrun,
        existing_map,
        ignore_keys,
        new_map,
        record_model,
        track_changes,
        update_ids_set,
    )

    # PROCESS ARCHIVES
    check_child_do_archives(archive_ids_set, dryrun, existing_records, record_model, track_changes, record_id_field)

    # CREATE NEW
    check_child_do_create(
        create_ids_set,
        dryrun,
        existing_controls,
        new_controls,
        new_map,
        record_model,
        track_changes,
    )


def check_child_do_create(
    create_ids_set: set,
    dryrun: bool,
    existing_controls: list[regscale_models.SecurityControl],
    new_controls: list,
    new_map: dict,
    record_model: Type[T],
    track_changes: list,
) -> None:
    """
    Function to create new child records that were found in the new catalog but not in the old catalog

    :param set create_ids_set: list of ids that were identified for creating a new record
    :param bool dryrun: True for yes a dry run False for no not a dry run (real updates)
    :param list[regscale_models.SecurityControl] existing_controls: list of dicts for existing controls from regscale installation
    :param list new_controls: list of dicts for controls of corresponding type from new source of updates
    :param dict new_map: hashmap of identifiers and records
    :param Type[T] record_model: Indicates if updating objectives, parameters, tests, or CCIs
    :param list track_changes: dict containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    if len(create_ids_set) > 0:
        logger.debug(
            f"Looking for {record_model.__name__}s in the new version of catalog which do not exist in the old "
            f"version. These would be created as new {record_model.__name__}s."
        )
        for identifier in create_ids_set:
            # Begin hacky solutions to mapping newly created child records to correct parents :(
            control_mapped = hacky_fix_for_catalog_data_structure(existing_controls, identifier, new_controls, new_map)
            # End of said hacky solution
            do_create(
                control_mapped,
                dryrun,
                identifier,
                new_map,
                record_model,
                track_changes,
            )


def do_create(
    control_mapped: bool,
    dryrun: bool,
    identifier: int,
    new_map: dict,
    record_model: Type[T],
    track_changes: list,
) -> None:
    """
    Function to create new child records that were found in the new catalog but not in the old catalog

    :param bool control_mapped: True if the control was mapped to a new control ID, False if not
    :param bool dryrun: True for yes a dry run False for no not a dry run (real updates)
    :param int identifier: the identifier of the record to be created
    :param dict new_map: hashmap of identifiers and records
    :param Type[T] record_model: The type of record being created, used for reporting
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    if control_mapped is True and new_map[identifier]["archived"] is False:
        track_changes.append(
            {
                "operation": "create new record",
                "record_model": record_model.__name__,
                "id": identifier,
                "field": "",
                "old_value": "",
                "new_value": "",
                "justification": f"New {record_model.__name__} found which did not exist in old catalog.",
            }
        )
        if dryrun is False:
            new_record = record_model(**new_map[identifier])
            new_record.create()
            logger.info(f"Created {record_model.__name__} {identifier} ID {new_record.id}")
    else:
        logger.warning(
            f"Skipped creating {record_model.__name__} {identifier}. Either record or it's parent control is archived."
        )


def hacky_fix_for_catalog_data_structure(
    existing_controls: list[regscale_models.SecurityControl],
    identifier: Union[str, int],
    new_controls: list,
    new_map: dict,
) -> bool:
    """
    Function to map newly created controls to the previously existing controls

    :param list[regscale_models.SecurityControl] existing_controls:
    :param Union[str, int] identifier: Unique identifier for the record
    :param list new_controls: list of new controls
    :param dict new_map: dict containing ids and records
    :return: Whether the control was mapped to a new control ID
    :rtype: bool
    """
    control_mapped = False
    for control in new_controls:
        if not control.get("id"):
            # For hierarchical data, the controlId is the parent control's ID
            control_mapped = True
        elif control.get("id") == new_map[identifier].get("securityControlId"):
            control_match_field = control["controlId"]

            for old_control in existing_controls:
                if control_match_field == old_control["controlId"]:
                    new_map[identifier]["securityControlId"] = old_control.id
                    control_mapped = True
    return control_mapped


def check_child_do_archives(
    archive_ids_set: set,
    dryrun: bool,
    existing_records: List[T],
    record_model: Type[T],
    track_changes: list,
    record_id_field: str,
) -> None:
    """
    Function to archive child records that were found in the old catalog but not in the new catalog

    :param set archive_ids_set: set of records identified for archival
    :param bool dryrun: True for yes a dry run False for no not a dry run (real updates)
    :param List[T] existing_records: list of existing records
    :param Type[T] record_model: Indicates if updating objectives, parameters, tests, or CCIs
    :param list track_changes: dict containing a record of changes that were noted between old and new, for reporting
    :param str record_id_field: name of id field appropriate for the record type
    :rtype: None
    """
    if not archive_ids_set:
        return

    logger.debug(
        f"Checking for {record_model.__name__}s in the old version of catalog which do not exist in the new "
        f"version. These would be archived."
    )
    for record in existing_records:
        if getattr(record, "archived", False):
            continue
        if getattr(record, record_id_field) in archive_ids_set:
            archive_record(
                existing_record=record,
                track_changes=track_changes,
                record_id=getattr(record, record_id_field),
                record_model=record_model,
                justification=f"{record_model.__name__} from old catalog no longer found in new catalog.",
            )
            if not dryrun:
                record.archived = True
                logger.info(f"Archived {record_model.__name__} #{record.id}: {getattr(record, record_id_field)}")


def check_child_do_updates(
    archived_controls: list,
    dryrun: bool,
    existing_map: dict,
    ignore_keys: set,
    new_map: dict,
    record_model: Type[T],
    track_changes: list,
    update_ids_set: set,
) -> None:
    """
    Function to update existing child records that were found in both the old and new catalogs

    :param list archived_controls: list of archived controls
    :param bool dryrun: True for yes a dry run False for no not a dry run (real updates)
    :param dict existing_map: hashmap of identifiers and complete records for existing child records
    :param set ignore_keys: set of field keys to be ignored for purposes of comparison
    :param dict new_map: hashmap of identifier and complete records for new source of update data
    :param Type[T] record_model: Indicates if updating objectives, parameters, tests, or CCIs
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
            record_model=record_model,
            track_changes=track_changes,
        )
        # If the parent control was archived, should also archive all child objectives associated with that control
        handle_archived(archived_controls, existing_map, identifier, record_model, track_changes)
        #
        if current_changes_count < len(track_changes):  # if changes recorded for this objective
            if dryrun is False and existing_map[identifier].has_changed():
                existing_map[identifier].save()
                logger.info(f"Updated {record_model.__name__} #{existing_map[identifier].id}: {identifier}")


def handle_archived(
    archived_controls: list,
    existing_map: dict,
    identifier: Union[int, str],
    record_model: Type[T],
    track_changes: list,
) -> None:
    """
    Function to handle archiving of child records when original control is archived

    :param list archived_controls: list of archived controls
    :param dict existing_map: hashmap of identifiers and complete records for existing child records
    :param Union[int, str] identifier: unique identifier for the record
    :param Type[T] record_model: Indicates if updating objectives, parameters, tests, or CCIs
    :param list track_changes: list containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    for control_id in archived_controls:
        if existing_map[identifier].securityControlId == control_id and existing_map[identifier].archived is False:
            logger.info(f"Inheriting archived status of parent control for {record_model.__name__}: {identifier}")
            archive_record(
                existing_record=existing_map[identifier],
                track_changes=track_changes,
                record_id=identifier,
                record_model=record_model,
                justification="Archived because parent control was archived",
            )


def check_catalog_metadata(
    existing_catalog: regscale_models.Catalog,
    new_version_catalog: dict,
    track_changes: list,
    dryrun: bool,
) -> None:
    """
    Function to check catalog metadata for updates

    :param regscale_models.Catalog existing_catalog: catalog being targeted for updates, retrieved from regscale installation
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
        "metadata",
        "defaultName",
    }
    if existing_catalog.uuid:
        update_record(
            existing_record=existing_catalog,
            new_record=new_version_catalog,
            ignore_keys=ignore_keys,
            record_id=existing_catalog.uuid,
            record_model=regscale_models.Catalog,
            track_changes=track_changes,
        )
        if current_changes_count < len(track_changes):  # if changes recorded in this section
            if dryrun is False:  # ONLY if this is NOT a dry run
                existing_catalog.securityControls = []
                existing_catalog.save()
                logger.info(f"Updated catalog metadata for #{existing_catalog.id}: {existing_catalog.title}")


# -------------------------------------------------------------------------------------------------------------------- #
# Begin Utility Functions


def define_operations(
    id_key_name: str, old_records: List[T], new_records: list[dict]
) -> tuple[dict, dict, set, set, set]:
    """
    Uses set logic to identify which identifiers should be created, updated, or archived (soft delete).
    Works the same for all record types: control, objective, parameter, test, cci

    :param str id_key_name: name of the field that contains the unique identifier for the record type
    :param List[T] old_records: list of dicts for existing records from RegScale installation
    :param list[dict] new_records: list of dicts for records of corresponding type from new source of updates
    :return: existing_map, new_map, archive_ids_set, create_ids_set, update_ids_set
    :rtype: tuple[dict, dict, set, set, set]
    """
    existing_map = {getattr(d, id_key_name): d for d in old_records}
    existing_id_set = set(existing_map.keys())

    new_map = {d[id_key_name]: d for d in new_records}
    new_id_set = set(new_map.keys())
    archive_ids_set = existing_id_set - new_id_set  # archive objects found in old version of catalog but not in the new
    create_ids_set = new_id_set - existing_id_set  # create as new objects found in new but not old
    update_ids_set = existing_id_set & new_id_set  # update existing if found in both old and new

    return existing_map, new_map, archive_ids_set, create_ids_set, update_ids_set


def update_record(
    existing_record: T,
    new_record: dict,
    ignore_keys: set,
    record_id: Union[str, int],
    record_model: Type[T],
    track_changes: list,
) -> None:
    """
    Function to update existing RegScale records with new data

    :param T existing_record: Existing record from RegScale to be updated
    :param dict new_record: New record from update source to be used for updating existing record
    :param set ignore_keys: Keys to ignore when comparing old and new records
    :param Union[str, int] record_id: Record ID of the record being updated in RegScale
    :param Type[T] record_model: Type of record being updated
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    existing_keys = set([key for key in existing_record.dict().keys() if key not in ignore_keys])
    new_keys = set([key for key in new_record.keys() if key not in ignore_keys])
    #
    update_record_latest_field_data(
        existing_keys,
        existing_record,
        ignore_keys,
        new_keys,
        new_record,
        record_id,
        record_model,
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
        record_model,
        track_changes,
    )

    #
    update_record_fields_removed(
        existing_keys,
        existing_record,
        ignore_keys,
        new_keys,
        record_id,
        record_model,
        track_changes,
    )


def check_for_truncation(value: Any, char_limit: int = 100) -> Any:
    """
    Function to check if a string is too long to be stored in RegScale and will truncate it if so

    :param Any value: The value to be checked for truncation
    :param int char_limit: The character limit for the field in RegScale, defaults to 100
    :return: Truncated string if necessary, otherwise the original value
    :rtype: Any
    """
    if isinstance(value, str) and len(value) > char_limit:
        return f"{value[:char_limit]}... [truncated]"
    else:
        return value


def update_record_fields_removed(
    existing_keys: set,
    existing_record: T,
    ignore_keys: set,
    new_keys: set,
    record_id: Union[int, str],
    record_model: Type[T],
    track_changes: list,
) -> None:
    """
    Function to update existing RegScale records with new data

    :param set existing_keys: Set of keys for the existing record
    :param T existing_record: Existing record from RegScale to be updated
    :param set ignore_keys: Set of keys to ignore when comparing old and new records
    :param set new_keys: Set of keys for the new record
    :param Union[int, str] record_id: Record ID of the record being updated in RegScale
    :param Type[T] record_model: Type of record being updated
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    for key in (existing_keys - new_keys) - ignore_keys:  # fields that were in old version but not new are set to null
        if getattr(existing_record, key) not in ["", None]:  # would ignore if it field already empty
            track_changes.append(
                {
                    "operation": "update",
                    "record_model": record_model.__name__,
                    "id": record_id,
                    "field": key,
                    "old_value": check_for_truncation(getattr(existing_record, key)),
                    "new_value": "",
                    "justification": "field no longer exists in new version",
                }
            )
            setattr(existing_record, key, None)


def update_record_new_fields(
    existing_keys: set,
    existing_record: T,
    ignore_keys: set,
    new_keys: set,
    new_record: dict,
    record_id: Union[int, str],
    record_model: Type[T],
    track_changes: list,
) -> None:
    """
    Function to update existing RegScale records with new data

    :param set existing_keys: Set of keys for the existing record
    :param T existing_record: Existing record from RegScale to be updated
    :param set ignore_keys: Set of keys to ignore when comparing old and new records
    :param set new_keys: Set of keys for the new record
    :param dict new_record: New record from update source to be used for updating existing record
    :param Union[int, str] record_id: Record ID of the record being updated in RegScale
    :param Type[T] record_model: Type of record being updated
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    for key in (new_keys - existing_keys) - ignore_keys:  # are any new fields present that were not in the old version?
        # ----
        track_changes.append(
            {
                "operation": "update",
                "record_model": record_model.__name__,
                "id": record_id,
                "field": key,
                "old_value": "",
                "new_value": check_for_truncation(new_record[key]),
                "justification": f"new field added to this {record_model.__name__} in latest version",
            }
        )  # if so record the change
        if hasattr(existing_record, key):
            setattr(existing_record, key, new_record.get(key))
        # update the existing version of record with field and data from update source


def update_record_latest_field_data(
    existing_keys: set,
    existing_record: T,
    ignore_keys: set,
    new_keys: set,
    new_record: dict,
    record_id: Union[int, str],
    record_model: Type[T],
    track_changes: list,
) -> None:
    """
    Function to update existing RegScale records with new data

    :param set existing_keys: Set of keys for the existing record
    :param T existing_record: Existing record from RegScale to be updated
    :param set ignore_keys: Set of keys to ignore when comparing old and new records
    :param set new_keys: Set of keys for the new record
    :param dict new_record: New record from update source to be used for updating existing record
    :param Union[int, str] record_id: Record ID of the record being updated in RegScale
    :param Type[T] record_model: Type of record being updated
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :rtype: None
    """
    for key in (existing_keys & new_keys) - ignore_keys:  # where same keys in both, check each field for new data
        if (
            getattr(existing_record, key) != new_record[key]
        ):  # if current version data different the new version data for a field
            track_changes.append(
                {
                    "operation": "archive" if key == "archived" else "update",
                    "record_model": record_model.__name__,
                    "id": record_id,
                    "field": key,
                    "old_value": check_for_truncation(getattr(existing_record, key)),
                    "new_value": check_for_truncation(new_record[key]),
                    "justification": "field data has changed",
                }
            )  # then record change
            setattr(existing_record, key, new_record[key])  # and overwrite existing with new data for this field


def archive_record(
    existing_record: T,
    track_changes: list,
    record_id: Union[int, str],
    record_model: Type[T],
    justification: str,
) -> None:
    """
    Function to archive a record

    :param T existing_record: Record to be archived
    :param list track_changes: List containing a record of changes that were noted between old and new, for reporting
    :param Union[int, str] record_id: Record ID of the record being archived in RegScale
    :param Type[T] record_model: Type of record being archived
    :param str justification: Justification for archiving the record
    :rtype: None
    """
    existing_record.archived = True
    track_changes.append(
        {
            "operation": "archive",
            "record_model": record_model.__name__,
            "id": record_id,
            "field": "archived",
            "old_value": False,
            "new_value": True,
            "justification": justification,
        }
    )
    existing_record.delete()


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
            "record_model",
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
        elif not response.ok:
            error_and_exit(f"Unexpected response from server. Unable to upload {catalog_path.name}.")
    return response
