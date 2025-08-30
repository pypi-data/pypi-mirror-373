#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integration of ServiceNow into RegScale CLI tool"""

# standard python imports
import datetime
import json
import os
import sys
from concurrent.futures import CancelledError, ThreadPoolExecutor, as_completed
from json import JSONDecodeError
from threading import Lock
from typing import List, Optional, Tuple, Union, Literal
from urllib.parse import urljoin

import click
import requests
from pathlib import Path
from rich.progress import track

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.api_handler import APIUpdateError
from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    create_progress_object,
    compute_hashes_in_directory,
    error_and_exit,
    save_data_to,
    get_current_datetime,
)
from regscale.core.app.utils.regscale_utils import verify_provided_module
from regscale.models import Change, Data, File, Issue, regscale_id, regscale_module
from regscale.utils.threading.threadhandler import create_threads, thread_assignment

job_progress = create_progress_object()
logger = create_logger()
APP_JSON = "application/json"
HEADERS = {"Content-Type": APP_JSON, "Accept": APP_JSON}
INCIDENT_TABLE = "api/now/table/incident"
update_counter = []
update_objects = []
new_regscale_objects = []
updated_regscale_objects = []


class ServiceNowConfig:
    """
    ServiceNow configuration class
    """

    reg_config: dict
    url: str
    user: str
    pwd: str
    reg_api: "Api" = Api()
    api: "Api" = Api()
    custom_fields: dict = {}
    incident_type: str = "Low"
    incident_group: str = "Service Desk"
    urgency_map = {
        "High": "1",
        "Medium": "2",
        "Low": "3",
    }

    def __init__(self, reg_config: dict, incident_type: str = "Low", incident_group: str = "Service Desk"):
        self.reg_config = reg_config
        self.url = reg_config.get("snowUrl")
        self.user = reg_config.get("snowUserName")
        self.pwd = reg_config.get("snowPassword")
        self.api.auth = (self.user, self.pwd)
        self.custom_fields = reg_config.get("serviceNow", {}).get("customFields", {})
        self.incident_type = self.urgency_map.get(incident_type, "Low")
        self.incident_group = incident_group
        self.check_servicenow_config()

    def check_servicenow_config(self) -> None:
        """
        Check if ServiceNow configuration is complete and not the defaults

        :return: None
        """
        fields = {"snowUrl": "url", "snowUserName": "user", "snowPassword": "pwd"}
        missing_keys = []
        for key, field in fields.items():
            if value := getattr(self, field):
                if value == self.api.app.template.get(key):
                    missing_keys.append(key)
        if missing_keys:
            error_and_exit(
                f"ServiceNow configuration is incomplete. Missing values for the following key(s): {', '.join(missing_keys)}",
            )


# Create group to handle ServiceNow integration
@click.group()
def servicenow():
    """Auto-assigns incidents in ServiceNow for remediation."""
    check_license()


####################################################################################################
#
# PROCESS ISSUES TO ServiceNow
# ServiceNow REST API Docs:
# https://docs.servicenow.com/bundle/xanadu-application-development/page/build/custom-application/concept/build-applications.html
# Use the REST API Explorer in ServiceNow to select table, get URL, and select which fields to
# populate
#
####################################################################################################
@servicenow.command()
@regscale_id()
@regscale_module()
@click.option(
    "--snow_assignment_group",
    type=click.STRING,
    help="RegScale will sync the issues for the record to this ServiceNow assignment group.",
    prompt="Enter the name of the project in ServiceNow",
    required=True,
)
@click.option(
    "--snow_incident_type",
    type=click.STRING,
    help="Enter the ServiceNow incident type to use when creating new issues from RegScale.",
    prompt="Enter the ServiceNow incident type",
    required=True,
)
def issues(
    regscale_id: int,
    regscale_module: str,
    snow_assignment_group: str,
    snow_incident_type: str,
):
    """Process issues to ServiceNow."""
    sync_snow_to_regscale(
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        snow_assignment_group=snow_assignment_group,
        snow_incident_type=snow_incident_type,
    )


@servicenow.command(name="issues_and_attachments")
@regscale_id()
@regscale_module()
@click.option(
    "--snow_assignment_group",
    "-g",
    type=click.STRING,
    help="RegScale will sync the issues for the record to this ServiceNow assignment group.",
    prompt="ServiceNow assignment group",
    required=True,
)
@click.option(
    "--snow_incident_type",
    "-t",
    type=click.Choice(["High", "Medium", "Low"], case_sensitive=False),
    help="Enter the ServiceNow incident type to use when creating new issues from RegScale.",
    prompt="ServiceNow incident type",
    required=True,
)
@click.option(
    "--sync_attachments",
    "-a",
    type=click.BOOL,
    help=(
        "Whether RegScale will sync the attachments for the issue "
        "in the provided ServiceNow assignment group and vice versa. Defaults to True."
    ),
    required=False,
    default=True,
)
@click.option(
    "--sync_all_incidents",
    "-all",
    type=click.BOOL,
    help=(
        "Whether to Sync all incidents from ServiceNow and RegScale issues for the "
        "provided regscale_id and regscale_module."
    ),
    required=False,
    default=True,
)
def issues_and_attachments(
    regscale_id: int,
    regscale_module: str,
    snow_assignment_group: str,
    snow_incident_type: str,
    sync_attachments: bool = True,
    sync_all_incidents: bool = True,
):
    """Process issues to ServiceNow."""
    sync_snow_and_regscale(
        parent_id=regscale_id,
        parent_module=regscale_module,
        snow_assignment_group=snow_assignment_group,
        snow_incident_type=snow_incident_type.title(),
        sync_attachments=sync_attachments,
        sync_all_incidents=sync_all_incidents,
    )


@servicenow.command(name="sync_work_notes")
@regscale_id(required=False)
@regscale_module(required=False)
def sync_work_notes(regscale_id: int, regscale_module: str):
    """Sync work notes from ServiceNow to existing issues in RegScale. Use regscale_id and regscale_module to sync work notes to specific issues."""
    if not regscale_id and not regscale_module:
        sync_notes_to_regscale()
    elif regscale_id and regscale_module:
        sync_notes_to_regscale(regscale_id=regscale_id, regscale_module=regscale_module)
    else:
        error_and_exit("Please provide both --regscale_id and --regscale_module to sync work notes.")


def get_issues_data(reg_api: Api, url_issues: str) -> List[dict]:
    """
    Fetch the full issue list from RegScale

    :param Api reg_api: RegScale API object
    :param str url_issues: URL for RegScale issues
    :return: List of issues
    :rtype: List[dict]
    """
    logger.info("Fetching full issue list from RegScale.")
    issue_response = reg_api.get(url_issues)
    result = []
    if issue_response.status_code == 204:
        logger.warning("No existing issues for this RegScale record.")
    else:
        try:
            result = issue_response.json()
        except JSONDecodeError as rex:
            error_and_exit(f"Unable to fetch issues from RegScale.\\n{rex}")
    return result


def create_snow_incident(
    snow_config: ServiceNowConfig,
    incident_url: str,
    snow_incident: dict,
    tag: dict,
    custom_fields: Optional[dict] = None,
) -> dict:
    """
    Create a new incident in ServiceNow

    :param ServiceNowConfig snow_config: ServiceNow configuration as a dictionary
    :param str incident_url: URL for ServiceNow incidents
    :param dict snow_incident: Incident data
    :param dict tag: ServiceNow tag to add to new incident
    :param Optional[dict] custom_fields: Custom fields to add to the incident, defaults to None
    :return: Incident response
    :rtype: dict
    """
    if custom_fields is None:
        custom_fields = {}
    result = {}
    snow_api = snow_config.api
    try:
        response = snow_api.post(
            url=incident_url,
            headers=HEADERS,
            json={**snow_incident, **custom_fields},
        )
        if not response.raise_for_status():
            result = response.json()
            if tag:
                new_incident = result["result"]
                payload = {
                    "label": tag["sys_id"],
                    "read": "yes",
                    "table": "incident",
                    "table_key": new_incident["sys_id"],
                    "title": f"Incident - {new_incident['number']}",
                    "id_type": "incident",
                    "id_display": new_incident["number"],
                    "viewable_by": "everyone",
                }
                tag_url = urljoin(snow_config.url, "/api/now/table/label_entry")
                res = snow_api.post(tag_url, headers=HEADERS, json=payload)
                if res.ok:
                    logger.debug("Tag %s added to incident %s", tag["name"], new_incident["sys_id"])
                else:
                    logger.warning("Unable to add tag %s to incident %s", tag["name"], new_incident["sys_id"])
    except requests.exceptions.RequestException as ex:
        if custom_fields:
            logger.error(
                "Unable to create incident %s in ServiceNow. Retrying without custom fields %s...\n%s",
                snow_incident,
                custom_fields,
                ex,
            )
            return create_snow_incident(snow_config, incident_url, snow_incident, tag)
        logger.error("Unable to create incident %s in ServiceNow...\n%s", snow_incident, ex)
    return result


def sync_snow_to_regscale(
    regscale_id: int,
    regscale_module: str,
    snow_assignment_group: str,
    snow_incident_type: str,
) -> None:
    """
    Sync issues from ServiceNow to RegScale via API
    :param int regscale_id: ID # of record in RegScale to associate issues with
    :param str regscale_module: RegScale module to associate issues with
    :param str snow_assignment_group: Snow assignment group to filter for
    :param str snow_incident_type: Snow incident type to filter for
    :rtype: None
    """
    # initialize variables
    app = Application()
    reg_api = Api()
    verify_provided_module(regscale_module)
    config = app.config

    # Group related variables into a dictionary
    snow_config = ServiceNowConfig(reg_config=config)

    url_issues = urljoin(
        config["domain"],
        f"api/issues/getAllByParent/{str(regscale_id)}/{str(regscale_module).lower()}",
    )

    if issues_data := get_issues_data(reg_api, url_issues):
        check_file_path("artifacts")
        save_data_to(
            file=Path("./artifacts/existingRecordIssues.json"),
            data=issues_data,
        )
        logger.info(
            "Writing out RegScale issue list for Record # %s to the artifacts folder "
            + "(see existingRecordIssues.json).",
            regscale_id,
        )
        logger.info(
            "%s existing issues retrieved for processing from RegScale.",
            len(issues_data),
        )

        int_new, int_skipped = process_issues(
            issues_data,
            snow_config,
            snow_assignment_group,
            snow_incident_type,
        )

        logger.info(
            "%i new issue incidents opened in ServiceNow and %i issues already exist and were skipped.",
            int_new,
            int_skipped,
        )
    else:
        logger.warning("No issues found for this record in RegScale. No issues were processed.")


def create_snow_assignment_group(snow_assignment_group: str, snow_config: ServiceNowConfig) -> None:
    """
    Create a new assignment group in ServiceNow or if one already exists,
    a 403 is returned from SNOW.

    :param str snow_assignment_group: ServiceNow assignment group
    :param ServiceNowConfig snow_config: ServiceNow configuration
    :rtype: None
    """
    # Create a service now assignment group. The api will not allow me create dups
    snow_api = snow_config.api
    payload = {
        "name": snow_assignment_group,
        "description": "An automatically generated Service Now assignment group from RegScale.",
        "active": True,
    }
    url = urljoin(snow_config.url, "api/now/table/sys_user_group")
    response = snow_api.post(
        url=url,
        headers=HEADERS,
        json=payload,
    )
    if response.status_code == 201:
        logger.info("ServiceNow Assignment Group %s created.", snow_assignment_group)
    elif response.status_code == 403:
        # I expect a 403 for a duplicate code already found
        logger.debug("ServiceNow Assignment Group %s already exists.", snow_assignment_group)
    elif response.status_code == 401:
        error_and_exit("Unauthorized to create ServiceNow Assignment Group. Please check your ServiceNow credentials.")
    else:
        error_and_exit(
            f"Unable to create ServiceNow Assignment Group {snow_assignment_group}. "
            f"Status code: {response.status_code}"
        )


def get_service_now_incidents(snow_config: ServiceNowConfig, query: str) -> List[dict]:
    """
    Get all incidents from ServiceNow

    :param dict snow_config: ServiceNow configuration
    :param str query: Query string
    :return: List of incidents
    :rtype: List[dict]
    """
    snow_api = snow_config.api
    incident_url = urljoin(snow_config.url, INCIDENT_TABLE)
    offset = 0
    limit = 500
    data = []

    while True:
        result, offset = query_service_now(
            api=snow_api,
            snow_url=incident_url,
            offset=offset,
            limit=limit,
            query=query,
        )
        data += result
        if not result:
            break

    return data


def process_issues(
    issues_data: List[dict],
    snow_config: ServiceNowConfig,
    snow_assignment_group: str,
    snow_incident_type: str,
) -> Tuple[int, int]:
    """
    Process issues and create new incidents in ServiceNow

    :param List[dict] issues_data: List of issues
    :param ServiceNowConfig snow_config: ServiceNow configuration
    :param str snow_assignment_group: ServiceNow assignment group
    :param str snow_incident_type: ServiceNow incident type
    :return: Number of new incidents created, plus number of skipped incidents
    :rtype: Tuple[int, int]
    """
    config = snow_config.reg_config
    int_new = 0
    int_skipped = 0
    # Need a lock for int_new
    lock = Lock()
    # Make sure the assignment group exists
    create_snow_assignment_group(snow_assignment_group, snow_config)

    with job_progress:
        with ThreadPoolExecutor(max_workers=10) as executor:
            if issues_data:
                task = job_progress.add_task(
                    f"[#f8b737]Syncing {len(issues_data)} RegScale issues to ServiceNow",
                    total=len(issues_data),
                )

            futures = [
                executor.submit(
                    create_incident,
                    iss,
                    snow_config,
                    snow_assignment_group,
                    snow_incident_type,
                    config,
                    {},
                    {},
                    False,
                )
                for iss in issues_data
            ]
            for future in as_completed(futures):
                try:
                    snow_response = future.result()
                    with lock:
                        if snow_response:
                            iss = snow_response["originalIssue"]
                            int_new += 1
                            logger.debug(snow_response)
                            logger.info(
                                "SNOW Incident ID %s created.",
                                snow_response["result"]["sys_id"],
                            )
                            iss["serviceNowId"] = snow_response["result"]["sys_id"]
                            try:
                                Issue(**iss).save()
                            except APIUpdateError as ex:
                                logger.error(
                                    "Unable to update issue in RegScale: %s\n%s",
                                    iss,
                                    ex,
                                )
                        else:
                            int_skipped += 1
                        job_progress.update(task, advance=1)
                except CancelledError as e:
                    logger.error("Future was cancelled: %s", e)

    return int_new, int_skipped


def create_incident(
    iss: dict,
    snow_config: ServiceNowConfig,
    snow_assignment_group: str,
    snow_incident_type: str,
    config: dict,
    tag: dict,
    attachments: dict,
    add_attachments: bool = False,
) -> Optional[dict]:
    """
    Create a new incident in ServiceNow

    :param dict iss: Issue data
    :param ServiceNowConfig snow_config: ServiceNow configuration
    :param str snow_assignment_group: ServiceNow assignment group
    :param str snow_incident_type: ServiceNow incident type
    :param dict config: Application config
    :param dict tag: ServiceNow tag to add to new incidents
    :param dict attachments: Dict of attachments from RegScale and ServiceNow
    :param bool add_attachments: Sync attachments from RegScale to ServiceNow, defaults to False
    :return: Response dataset from ServiceNow or None
    :rtype: Optional[dict]
    """
    response = None
    if iss.get("serviceNowId", "") != "" and iss.get("serviceNowId") is not None:
        return response

    snow_incident = map_regscale_to_snow_incident(
        regscale_issue=iss,
        snow_assignment_group=snow_assignment_group,
        snow_incident_type=snow_incident_type,
        config=config,
    )
    incident_url = urljoin(snow_config.url, INCIDENT_TABLE)
    if response := create_snow_incident(
        snow_config=snow_config,
        incident_url=incident_url,
        snow_incident=snow_incident,
        tag=tag,
        custom_fields=snow_config.custom_fields,  # type: ignore
    ):
        response["originalIssue"] = iss
        if add_attachments and attachments:
            compare_files_for_dupes_and_upload(
                snow_issue=response["result"],
                regscale_issue=iss,
                snow_config=snow_config,
                attachments=attachments,
            )
    return response


def map_regscale_to_snow_incident(
    regscale_issue: Union[dict, Issue],
    snow_assignment_group: str,
    snow_incident_type: str,
    config: dict,
) -> dict:
    """
    Map RegScale issue to ServiceNow incident

    :param Union[dict, Issue] regscale_issue: RegScale issue to map to ServiceNow incident
    :param str snow_assignment_group: ServiceNow assignment group
    :param str snow_incident_type: ServiceNow incident type
    :param dict config: RegScale CLI Application configuration
    :return: ServiceNow incident data
    :rtype: dict
    """
    if isinstance(regscale_issue, Issue):
        regscale_issue = regscale_issue.model_dump()
    snow_incident = {
        "description": regscale_issue["description"],
        "short_description": regscale_issue["title"],
        "assignment_group": snow_assignment_group,
        "due_date": regscale_issue["dueDate"],
        "comments": f"RegScale Issue #{regscale_issue['id']} - {config['domain']}/form/issues/{regscale_issue['id']}",
        "state": "New",
        "urgency": snow_incident_type,
    }
    # update state and closed_at if the RegScale issue is closed
    if regscale_issue["status"] == "Closed":
        snow_incident["state"] = "Closed"
        snow_incident["closed_at"] = regscale_issue["dateCompleted"]
    return snow_incident


def sync_snow_and_regscale(
    parent_id: int,
    parent_module: str,
    snow_assignment_group: str,
    snow_incident_type: Literal["High", "Medium", "Low"],
    sync_attachments: bool = True,
    sync_all_incidents: bool = True,
) -> None:
    """
    Sync issues, bidirectionally, from ServiceNow into RegScale as issues

    :param int parent_id: ID # from RegScale to associate issues with
    :param str parent_module: RegScale module to associate issues with
    :param str snow_assignment_group: Assignment Group Name of the project in ServiceNow
    :param str snow_incident_type: Type of issues to sync from ServiceNow
    :param bool sync_attachments: Whether to sync attachments in RegScale & ServiceNow, defaults to True
    :param bool sync_all_incidents: Whether to sync all incidents from ServiceNow and RegScale issues
    :rtype: None
    """
    app = check_license()
    api = Api()
    config = app.config
    snow_config = ServiceNowConfig(
        reg_config=config, incident_type=snow_incident_type, incident_group=snow_assignment_group
    )

    # see if provided RegScale Module is an accepted option
    verify_provided_module(parent_module)
    # Make sure the assignment group exists
    create_snow_assignment_group(snow_assignment_group, snow_config)
    query = "&sysparm_display_value=true"
    tag = get_or_create_snow_tag(snow_config=snow_config, tag_name=f"regscale-{parent_module}-{parent_id}")
    if sync_all_incidents:
        incidents = get_service_now_incidents(snow_config=snow_config, query=query)
    else:
        incidents = get_snow_incidents(snow_config=snow_config, query=query, tag=tag)

    (
        regscale_issues,
        regscale_attachments,
    ) = Issue.fetch_issues_and_attachments_by_parent(
        parent_id=parent_id,
        parent_module=parent_module,
        fetch_attachments=sync_attachments,
    )
    snow_attachments = get_snow_attachment_metadata(snow_config)
    attachments = {
        "regscale": regscale_attachments or {},
        "snow": snow_attachments or {},
    }

    if regscale_issues:
        # sync RegScale issues to SNOW
        if issues_to_update := sync_regscale_to_snow(
            regscale_issues=regscale_issues,
            snow_config=snow_config,
            config=config,
            attachments=attachments,
            tag=tag,
            sync_attachments=sync_attachments,
        ):
            with job_progress:
                # create task to update RegScale issues
                updating_issues = job_progress.add_task(
                    f"[#f8b737]Updating {len(issues_to_update)} RegScale issue(s) from ServiceNow...",
                    total=len(issues_to_update),
                )
                # create threads to analyze ServiceNow incidents and RegScale issues
                create_threads(
                    process=update_regscale_issues,
                    args=(
                        issues_to_update,
                        api,
                        updating_issues,
                    ),
                    thread_count=len(issues_to_update),
                )
                # output the final result
                logger.info(
                    "%i/%i issue(s) updated in RegScale.",
                    len(issues_to_update),
                    len(update_counter),
                )
    else:
        logger.info("No issues need to be updated in RegScale.")

    if incidents:
        sync_snow_incidents_to_regscale_issues(
            incidents=incidents,
            regscale_issues=regscale_issues,
            sync_attachments=sync_attachments,
            attachments=attachments,
            app=app,
            snow_config=snow_config,
            parent_id=parent_id,
            parent_module=parent_module,
        )
    else:
        logger.info("No incidents need to be analyzed from ServiceNow.")


def get_or_create_snow_tag(snow_config: ServiceNowConfig, tag_name: str) -> dict:
    """
    Check if a tag exists in ServiceNow, if not, create it

    :param ServiceNowConfig snow_config: ServiceNow configuration
    :param str tag_name: Desired name of the tag
    :return: List of tags
    :rtype: List[str]
    """
    snow_api = snow_config.api
    tags_url = urljoin(snow_config.url, "api/now/table/label")

    offset = 0
    limit = 500
    data = []

    while True:
        result, offset = query_service_now(
            api=snow_api,
            snow_url=tags_url,
            offset=offset,
            limit=limit,
            query=f"&sysparm_query=name={tag_name}",
        )
        data += result
        if not result:
            break

    if data:
        return data[0]
    return create_snow_tag(snow_config=snow_config, tag_name=tag_name)


def create_snow_tag(snow_config: ServiceNowConfig, tag_name: str) -> Optional[dict]:
    """
    Create a new assignment group in ServiceNow or if one already exists,
    a 403 is returned from SNOW.

    :param ServiceNowConfig snow_config: ServiceNow configuration dictionary
    :param str tag_name: ServiceNow tag name
    :return: Created tag or None
    :rtype: Optional[dict]
    """
    # Create a service now tag. The api will not allow duplicates
    snow_api = snow_config.api
    payload = {
        "name": tag_name,
        "max_entries": 100000,  # arbitrary number, just needs to be large to avoid limit issues
        "global": False,
        "active": True,
        "sys_class_name": "tag",
        "type": "Standard",
        "viewable_by": "everyone",
    }
    url = urljoin(snow_config.url, "api/now/table/label")
    response = snow_api.post(
        url=url,
        headers=HEADERS,
        json=payload,
    )
    if response.status_code == 201:
        logger.info("ServiceNow Tag %s created.", tag_name)
        return response.json()["result"]
    elif response.status_code == 403:
        # I expect a 403 for a duplicate code already found
        logger.debug("ServiceNow Tag %s already exists.", tag_name)
    elif response.status_code == 401:
        error_and_exit("Unauthorized to create ServiceNow Tag. Please check your ServiceNow credentials.")
    else:
        error_and_exit(f"Unable to create ServiceNow Tag {tag_name}. Status code: {response.status_code}")


def update_regscale_issues(args: Tuple, thread: int) -> None:
    """
    Function to compare ServiceNow incidents and RegScale issues

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """
    # set up local variables from the passed args
    (
        regscale_issues,
        app,
        task,
    ) = args
    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(regscale_issues))
    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        # set the issue for the thread for later use in the function
        issue = regscale_issues[threads[i]]
        # update the issue in RegScale
        issue = issue.save()
        logger.debug(
            "RegScale Issue %i was updated with the ServiceNow incident #%s.",
            issue.id,
            issue.serviceNowId,
        )
        update_counter.append(issue)
        # update progress bar
        job_progress.update(task, advance=1)


def get_snow_incidents(snow_config: ServiceNowConfig, query: str = "", tag: Optional[dict] = None) -> List[dict]:
    """
    Get all incidents from ServiceNow

    :param ServiceNowConfig snow_config: ServiceNow Configuration object
    :param str query: Query string, defaults to ""
    :param dict tag: Tag to filter incidents by, defaults to None
    :return: List of incidents
    :rtype: List[dict]
    """
    snow_api = snow_config.api
    incident_url = urljoin(snow_config.url, INCIDENT_TABLE)
    offset = 0
    limit = 500
    data = []
    if tag:
        query += f"&sysparm_query=sys_tags.{tag['sys_id']}={tag['sys_id']}"

    while True:
        result, offset = query_service_now(
            api=snow_api,
            snow_url=incident_url,
            offset=offset,
            limit=limit,
            query=query,
        )
        data += result
        if not result:
            break

    return data


def sync_regscale_to_snow(
    regscale_issues: list[Issue],
    snow_config: ServiceNowConfig,
    config: dict,
    attachments: dict,
    tag: dict,
    sync_attachments: bool = True,
) -> list[Issue]:
    """
    Sync issues from RegScale to SNOW

    :param list[Issue] regscale_issues: list of RegScale issues to sync to SNOW
    :param ServiceNowConfig snow_config: SNOW configuration
    :param dict config: RegScale CLI configuration
    :param dict attachments: Dict of attachments from RegScale and SNOW
    :param dict tag: SNOW tag to add to new incidents
    :param bool sync_attachments: Sync attachments from RegScale to SNOW, defaults to True
    :return: list of RegScale issues that need to be updated
    :rtype: list[Issue]
    """
    new_issue_counter = 0
    issuess_to_update = []
    with job_progress:
        # create task to create ServiceNow incidents
        creating_issues = job_progress.add_task(
            f"[#f8b737]Verifying {len(regscale_issues)} RegScale issue(s) exist in ServiceNow...",
            total=len(regscale_issues),
        )
        for issue in regscale_issues:
            # create_incident has logic to check if the issue already has serviceNowId populated
            if new_issue := create_incident(
                iss=issue.model_dump(),
                snow_config=snow_config,
                snow_assignment_group=snow_config.incident_group,
                snow_incident_type=snow_config.incident_type,
                config=config,
                tag=tag,
                add_attachments=sync_attachments,
                attachments=attachments,
            ):
                # log progress
                new_issue_counter += 1
                # get the ServiceNow incident ID
                snow_id = new_issue["result"]["number"]
                # update the RegScale issue for the ServiceNow link
                issue.serviceNowId = snow_id
                # add the issue to the update_issues global list
                issuess_to_update.append(issue)
            job_progress.update(creating_issues, advance=1)
    # output the final result
    logger.info("%i new incident(s) opened in ServiceNow.", new_issue_counter)
    return issuess_to_update


def compare_files_for_dupes_and_upload(
    snow_issue: dict,
    regscale_issue: dict,
    snow_config: ServiceNowConfig,
    attachments: dict,
) -> None:
    """
    Compare files for duplicates and upload them to ServiceNow and RegScale

    :param dict snow_issue: SNOW issue to upload the attachments to
    :param dict regscale_issue: RegScale issue to upload the attachments from
    :param ServiceNowConfig snow_config: SNOW configuration
    :param dict attachments: Attachments from RegScale and ServiceNow
    :rtype: None
    """
    import tempfile

    api = Api()
    snow_uploaded_attachments = []
    regscale_uploaded_attachments = []
    with tempfile.TemporaryDirectory() as temp_dir:
        snow_dir, regscale_dir = download_issue_attachments_to_directory(
            directory=temp_dir,
            regscale_issue=regscale_issue,
            snow_issue=snow_issue,
            api=api,
            snow_config=snow_config,
            attachments=attachments,
        )
        snow_attachment_hashes = compute_hashes_in_directory(snow_dir)
        regscale_attachment_hashes = compute_hashes_in_directory(regscale_dir)

        upload_files_to_snow(
            snow_attachment_hashes=snow_attachment_hashes,
            regscale_attachment_hashes=regscale_attachment_hashes,
            snow_issue=snow_issue,
            snow_config=snow_config,
            regscale_issue=regscale_issue,
            snow_uploaded_attachments=snow_uploaded_attachments,
        )
        upload_files_to_regscale(
            snow_attachment_hashes=snow_attachment_hashes,
            regscale_attachment_hashes=regscale_attachment_hashes,
            regscale_issue=regscale_issue,
            api=api,
            regscale_uploaded_attachments=regscale_uploaded_attachments,
        )

    log_upload_results(regscale_uploaded_attachments, snow_uploaded_attachments, regscale_issue, snow_issue)


def download_snow_attachment(attachment: dict, snow_config: ServiceNowConfig, save_dir: str) -> None:
    """
    Download an attachment from ServiceNow

    :param dict attachment: Attachment to download
    :param ServiceNowConfig snow_config: SNOW configuration
    :param str save_dir: Directory to save the attachment in
    :rtype: None
    """
    snow_api = snow_config.api
    # check if the file_name has an extension
    if not Path(attachment["file_name"]).suffix:
        import mimetypes

        suffix = mimetypes.guess_extension(attachment["content_type"])
        attachment["file_name"] = attachment["file_name"] + suffix
    with open(os.path.join(save_dir, attachment["file_name"]), "wb") as file:
        res = snow_api.get(attachment["download_link"])
        if res.ok:
            file.write(res.content)
        else:
            logger.error("Unable to download %s from ServiceNow.", attachment["file_name"])


def upload_files_to_snow(
    snow_attachment_hashes: dict,
    regscale_attachment_hashes: dict,
    snow_issue: dict,
    snow_config: ServiceNowConfig,
    regscale_issue: dict,
    snow_uploaded_attachments: list,
) -> None:
    """
    Upload files to ServiceNow

    :param dict snow_attachment_hashes: Dictionary of SNOW attachment hashes
    :param dict regscale_attachment_hashes: Dictionary of RegScale attachment hashes
    :param dict snow_issue: SNOW issue to upload the attachments to
    :param ServiceNowConfig snow_config: SNOW configuration
    :param dict regscale_issue: RegScale issue to upload the attachments from
    :param list snow_uploaded_attachments: List of SNOW attachments that were uploaded
    :rtype: None
    """
    snow_api = snow_config.api
    upload_url = urljoin(snow_config.url, "/api/now/attachment/file")

    for file_hash, file in regscale_attachment_hashes.items():
        if file_hash not in snow_attachment_hashes:
            with open(file, "rb") as in_file:
                path_file = Path(file)
                data = in_file.read()
                params = {
                    "table_name": "incident",
                    "table_sys_id": snow_issue["sys_id"],
                    "file_name": f"RegScale_Issue_{regscale_issue['id']}_{path_file.name}",
                }
                headers = {"Content-Type": File.determine_mime_type(path_file.suffix), "Accept": APP_JSON}
                response = snow_api.post(url=upload_url, headers=headers, data=data, params=params)  # type: ignore
                if response.raise_for_status():
                    logger.error(
                        "Unable to upload %s to ServiceNow incident %s.",
                        path_file.name,
                        snow_issue["number"],
                    )
                else:
                    logger.debug(
                        "Uploaded %s to ServiceNow incident %s.",
                        path_file.name,
                        snow_issue["number"],
                    )
                    snow_uploaded_attachments.append(file)


def download_issue_attachments_to_directory(
    directory: str,
    regscale_issue: dict,
    snow_issue: dict,
    api: Api,
    snow_config: ServiceNowConfig,
    attachments: dict,
) -> tuple[str, str]:
    """
    Function to download attachments from ServiceNow and RegScale issues to a directory

    :param str directory: Directory to store the files in
    :param dict regscale_issue: RegScale issue to download the attachments for
    :param dict snow_issue: SNOW issue to download the attachments for
    :param Api api: Api object to use for interacting with RegScale
    :param ServiceNowConfig snow_config: SNOW configuration
    :param dict attachments: Dictionary of attachments from RegScale and ServiceNow
    :return: Tuple of strings containing the SNOW and RegScale directories
    :rtype: tuple[str, str]
    """
    # determine which attachments need to be uploaded to prevent duplicates by checking hashes
    snow_dir = os.path.join(directory, "snow")
    check_file_path(snow_dir, False)
    # download all attachments from ServiceNow to the snow directory in temp_dir
    for attachment in attachments["snow"].get(snow_issue.get("sys_id"), []):
        download_snow_attachment(attachment, snow_config, snow_dir)
    # get the regscale issue attachments
    regscale_issue_attachments = attachments["regscale"].get(regscale_issue["id"], [])
    # create a directory for the regscale attachments
    regscale_dir = os.path.join(directory, "regscale")
    check_file_path(regscale_dir, False)
    # download regscale attachments to the directory
    for attachment in regscale_issue_attachments:
        with open(os.path.join(regscale_dir, attachment.trustedDisplayName), "wb") as file:
            file.write(
                File.download_file_from_regscale_to_memory(
                    api=api,
                    record_id=regscale_issue["id"],
                    module="issues",
                    stored_name=attachment.trustedStorageName,
                    file_hash=(attachment.fileHash if attachment.fileHash else attachment.shaHash),
                )
            )
    return snow_dir, regscale_dir


def upload_files_to_regscale(
    snow_attachment_hashes: dict,
    regscale_attachment_hashes: dict,
    regscale_issue: dict,
    api: Api,
    regscale_uploaded_attachments: list,
) -> None:
    """
    Upload files to RegScale

    :param dict snow_attachment_hashes: Dictionary of SNOW attachment hashes
    :param dict regscale_attachment_hashes: Dictionary of RegScale attachment hashes
    :param dict regscale_issue: RegScale issue to upload the attachments to
    :param Api api: Api object to use for interacting with RegScale
    :param list regscale_uploaded_attachments: List of RegScale attachments that were uploaded
    :rtype: None
    :return: None
    """
    for file_hash, file in snow_attachment_hashes.items():
        if file_hash not in regscale_attachment_hashes:
            with open(file, "rb") as in_file:
                path_file = Path(file)
                if File.upload_file_to_regscale(
                    file_name=f"ServiceNow_attachment_{path_file.name}",
                    parent_id=regscale_issue["id"],
                    parent_module="issues",
                    api=api,
                    file_data=in_file.read(),
                ):
                    regscale_uploaded_attachments.append(file)
                    logger.debug(
                        "Uploaded %s to RegScale issue #%i.",
                        path_file.name,
                        regscale_issue["id"],
                    )
                else:
                    logger.warning(
                        "Unable to upload %s to RegScale issue #%i.",
                        path_file.name,
                        regscale_issue["id"],
                    )


def log_upload_results(
    regscale_uploaded_attachments: list, snow_uploaded_attachments: list, regscale_issue: dict, snow_issue: dict
) -> None:
    """
    Log the results of the upload process

    :param list regscale_uploaded_attachments: List of RegScale attachments that were uploaded
    :param list snow_uploaded_attachments: List of Snow attachments that were uploaded
    :param dict regscale_issue: RegScale issue that the attachments were uploaded to
    :param dict snow_issue: SNOW issue that the attachments were uploaded to
    :rtype: None
    """
    if regscale_uploaded_attachments and snow_uploaded_attachments:
        logger.info(
            "%i file(s) uploaded to RegScale issue #%i and %i file(s) uploaded to ServiceNow incident %s.",
            len(regscale_uploaded_attachments),
            regscale_issue["id"],
            len(snow_uploaded_attachments),
            snow_issue["number"],
        )
    elif snow_uploaded_attachments:
        logger.info(
            "%i file(s) uploaded to ServiceNow incident %s.",
            len(snow_uploaded_attachments),
            snow_issue["number"],
        )
    elif regscale_uploaded_attachments:
        logger.info(
            "%i file(s) uploaded to RegScale issue #%i.",
            len(regscale_uploaded_attachments),
            regscale_issue["id"],
        )


def sync_snow_incidents_to_regscale_issues(
    incidents: list[dict],
    regscale_issues: list[Issue],
    sync_attachments: bool,
    attachments: dict,
    app: "Application",
    snow_config: ServiceNowConfig,
    parent_id: int,
    parent_module: str,
) -> None:
    """
    Sync incidents from ServiceNow to RegScale

    :param list[dict] incidents: List of SNOW incidents to sync to RegScale
    :param list[Issue] regscale_issues: List of RegScale issues to compare to SNOW Incidents
    :param bool sync_attachments: Sync attachments from ServieNow to RegScale, defaults to True
    :param dict attachments: Attachments from RegScale and ServiceNow
    :param Application app: RegScale CLI application object
    :param dict snow_config: ServiceNow configuration
    :param int parent_id: Parent record ID in RegScale
    :param str parent_module: Parent record module in RegScale
    :rtype: None
    """
    issues_closed = []
    with job_progress:
        creating_issues = job_progress.add_task(
            f"[#f8b737]Comparing {len(incidents)} ServiceNow incident(s)"
            f" and {len(regscale_issues)} RegScale issue(s)...",
            total=len(incidents),
        )
        create_threads(
            process=create_and_update_regscale_issues,
            args=(
                incidents,
                regscale_issues,
                snow_config,
                sync_attachments,
                attachments,
                app,
                parent_id,
                parent_module,
                creating_issues,
                job_progress,
            ),
            thread_count=len(incidents),
        )
        logger.info(
            f"Analyzed {len(incidents)} ServiceNow incidents(s), created {len(new_regscale_objects)} issue(s), "
            f"updated {len(updated_regscale_objects)} issue(s), and closed {len(issues_closed)} issue(s) in RegScale.",
        )


def create_and_update_regscale_issues(args: Tuple, thread: int) -> None:
    """
    Function to create or update issues in RegScale from ServiceNow

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """
    # set up local variables from the passed args
    (
        incidents,
        regscale_issues,
        snow_config,
        add_attachments,
        attachments,
        app,
        parent_id,
        parent_module,
        task,
        progress,
    ) = args
    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(incidents))
    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        snow_incident: dict = incidents[threads[i]]
        regscale_issue: Optional[Issue] = next(
            (issue for issue in regscale_issues if issue.serviceNowId == snow_incident["number"]), None
        )
        data = Data(
            parentId=0,
            parentModule=Issue.get_module_string(),
            dataType="JSON",
            dataSource=f"ServiceNow Incident #{snow_incident['number']}",
            rawData=json.dumps(snow_incident),
        )
        # see if the incident needs to be created in RegScale
        if not regscale_issue:
            # map the SNOW incident to a RegScale issue object
            issue = map_incident_to_regscale_issue(
                incident=snow_incident,
                parent_id=parent_id,
                parent_module=parent_module,
            )
            # create the issue in RegScale
            if regscale_issue := issue.create():
                logger.debug(
                    "Created issue #%i-%s in RegScale.",
                    regscale_issue.id,
                    regscale_issue.title,
                )
                data.parentId = regscale_issue.id
                data.create()
                new_regscale_objects.append(regscale_issue)
            else:
                logger.warning("Unable to create issue in RegScale.\nIssue: %s", issue.dict())
        elif snow_incident["state"].lower() == "closed" and regscale_issue.status not in ["Closed", "Cancelled"]:
            # update the status and date completed of the RegScale issue
            regscale_issue.status = "Closed"
            regscale_issue.dateCompleted = snow_incident["closed_at"]
            # update the issue in RegScale
            updated_regscale_objects.append(regscale_issue.save())
            data.parentId = regscale_issue.id
            data.create_or_update()
        elif regscale_issue:
            # update the issue in RegScale
            updated_regscale_objects.append(regscale_issue.save())
            data.parentId = regscale_issue.id
            data.create_or_update()

        if add_attachments and regscale_issue and snow_incident["sys_id"] in attachments["snow"]:
            # determine which attachments need to be uploaded to prevent duplicates by
            # getting the hashes of all SNOW & RegScale attachments
            compare_files_for_dupes_and_upload(
                snow_issue=snow_incident,
                regscale_issue=regscale_issue.model_dump(),
                snow_config=snow_config,
                attachments=attachments,
            )
        # update progress bar
        progress.update(task, advance=1)


def map_incident_to_regscale_issue(incident: dict, parent_id: int, parent_module: str) -> Issue:
    """
    Map a ServiceNow incident to a RegScale issue

    :param dict incident: ServiceNow incident to map to RegScale issue
    :param int parent_id: Parent record ID in RegScale
    :param str parent_module: Parent record module in RegScale
    :return: RegScale issue object
    :rtype: Issue
    """
    default_due_date = datetime.datetime.now() + datetime.timedelta(days=30)
    new_issue = Issue(
        title=incident["short_description"],
        description=incident["description"],
        dueDate=incident["due_date"] or default_due_date.strftime("%Y-%m-%d %H:%M:%S"),
        parentId=parent_id,
        parentModule=parent_module,
        serviceNowId=incident["number"],
        status="Closed" if incident["state"].lower() == "closed" else "Open",
        severityLevel=Issue.assign_severity(incident["priority"].split(" ")[-1]),
    )
    # correct the status if it is canceled
    if incident["state"].lower() == "canceled":
        new_issue.status = "Cancelled"
    if new_issue.status in ["Closed", "Cancelled"]:
        new_issue.dateCompleted = incident.get("closed_at", get_current_datetime())
    return new_issue


def get_snow_attachment_metadata(snow_config: ServiceNowConfig) -> dict[str, list[dict]]:
    """
    Get attachments for a ServiceNow incident

    :param ServiceNowConfig snow_config: ServiceNow's configuration object
    :return: Dictionary of attachments with table_sys_id as the key and the attachments as the value
    :rtype: dict[str, list[dict]]
    """
    snow_api = snow_config.api
    attachment_url = urljoin(snow_config.url, "api/now/attachment")
    offset = 0
    limit = 500
    data = []
    sorted_data = {}

    while True:
        result, offset = query_service_now(
            api=snow_api,
            snow_url=attachment_url,
            offset=offset,
            limit=limit,
            query="&table_name=incident",
        )
        data += result
        if not result:
            break
    for item in data:
        key = item["table_sys_id"]
        if key in sorted_data:
            sorted_data[key].append(item)
        else:
            sorted_data[key] = [item]
    return sorted_data


def sync_notes_to_regscale(regscale_id: int = None, regscale_module: str = None) -> None:
    """
    Sync work notes from ServiceNow to existing issues

    :param int regscale_id: RegScale record ID
    :param str regscale_module: RegScale record module
    :rtype: None
    """
    app = Application()
    # get secrets
    snow_config = ServiceNowConfig(reg_config=app.config)
    query = ""
    data = get_service_now_incidents(snow_config, query=query)
    work_notes = get_service_now_work_notes(snow_config, data)
    work_notes_mapping = {}
    # change work_notes to a dictionary using the incident id as the key and a list of work notes as the value
    for work_note in work_notes:
        key = work_note["element_id"]
        if key in work_notes_mapping:
            work_notes_mapping[key].append(work_note)
        else:
            work_notes_mapping[key] = [work_note]
    process_work_notes(
        data=data,
        work_notes_mapping=work_notes_mapping,
        regscale_id=regscale_id,
        regscale_module=regscale_module,
    )


def get_service_now_work_notes(snow_config: ServiceNowConfig, incidents: list) -> list:
    """
    Get all work notes from ServiceNow

    :param ServiceNowConfig snow_config: ServiceNow's configuration dictionary
    :param list incidents: List of incidents from ServiceNow
    :return: List of work notes
    :rtype: list
    """
    snow_api = snow_config.api
    work_notes_url = urljoin(snow_config.url, "api/now/table/sys_journal_field")
    offset = 0
    limit = 500
    data = []
    if sys_ids := [incident["sys_id"] for incident in incidents]:
        # filter work notes by using the sys_ids, and only get work notes for incidents
        query = f"&element_idIN{','.join(sys_ids)}&element=work_notes&name=incident"
    else:
        query = "element=work_notes"

    while True:
        result, offset = query_service_now(
            api=snow_api,
            snow_url=work_notes_url,
            offset=offset,
            limit=limit,
            query=query,
        )
        data += result
        if not result:
            break

    return data


def process_work_notes(
    data: list,
    work_notes_mapping: dict[str, list[dict]],
    regscale_id: int = None,
    regscale_module: str = None,
) -> None:
    """
    Process and Sync the ServiceNow work notes to RegScale

    :param list data: list of data from ServiceNow to sync with RegScale
    :param dict[str, list[dict]] work_notes_mapping: Mapping of work notes from SNOW with the incident sys_id as the key
    :param int regscale_id: RegScale record ID, defaults to None
    :param str regscale_module: RegScale record module, defaults to None
    :rtype: None
    """
    update_issues: list[Issue] = []
    for dat in track(
        data,
        description=f"Processing {len(data):,} ServiceNow incidents",
    ):
        incident_number = dat["number"]
        try:
            if regscale_id and regscale_module:
                regscale_issues = Issue.get_all_by_parent(regscale_id, regscale_module)
            else:
                regscale_issues = Issue.find_by_service_now_id(incident_number)
            logger.debug("Processing ServiceNow Issue # %s", incident_number)
            if updated_issue := determine_issue_description(
                incident=dat,
                regscale_issues=regscale_issues,
                work_notes_mapping=work_notes_mapping,
            ):
                update_issues.append(updated_issue)
        except requests.HTTPError:
            logger.warning(
                "HTTP Error: Unable to find RegScale issue with ServiceNow incident ID of %s.",
                incident_number,
            )
    if len(update_issues) > 0:
        logger.debug(update_issues)
        _ = Issue.batch_update(update_issues)
    else:
        logger.warning("All ServiceNow work notes are already in RegScale. No updates needed.")
        sys.exit(0)


def determine_issue_description(
    incident: dict, regscale_issues: List[Issue], work_notes_mapping: dict[str, list[dict]]
) -> Optional[Issue]:
    """
    Determine if the issue description needs to be updated

    :param dict incident: ServiceNow incident
    :param List[Issue] regscale_issues: List of RegScale issues to update the description for
    :param dict[str, list[dict]] work_notes_mapping: Mapping of work notes from SNOW with the incident sys_id as the key
    :return: Issue if description needs to be updated
    """
    # legacy SNOW work notes are stored as a string in the incident object, check if it is populated
    # if not, check the work_notes_mapping for the incident sys_id which will return a list of work notes
    work_notes = incident.get("work_notes") or work_notes_mapping.get(incident["sys_id"], [])
    if not work_notes:
        return None

    for issue in regscale_issues:
        if issue.serviceNowId != incident["number"]:
            continue
        # if work_notes is a list, convert it to a string
        if isinstance(work_notes, list):
            work_notes = build_issue_description_from_list(work_notes, issue)
        if work_notes not in issue.description:
            logger.info(
                "Updating work item for RegScale issue # %s and ServiceNow incident " + "# %s.",
                issue.id,
                incident["number"],
            )
            issue.description = f"<strong>ServiceNow Work Notes: </strong>{work_notes}<br/>" + issue.description
            return issue


def build_issue_description_from_list(work_notes: list[dict], issue: Issue) -> str:
    """
    Build a new description from a list of work notes from ServiceNow

    :param list[dict] work_notes: List of work notes from ServiceNow
    :param Issue issue: RegScale issue
    :return: New description
    :rtype: str
    """
    new_description = ""
    # if work_notes is a list, convert it to a string
    for note in work_notes:
        if note["value"] not in issue.description:
            new_description += f"<br/>{note['value']}"
    return new_description


def query_service_now(api: Api, snow_url: str, offset: int, limit: int, query: str) -> Tuple[list, int]:
    """
    Paginate through query results

    :param Api api: API object
    :param str snow_url: URL for ServiceNow incidents
    :param int offset: Used in URL for ServiceNow API call
    :param int limit: Used in URL for ServiceNow API call
    :param str query: Query string for ServiceNow API call
    :return: Tuple[Result data from API call, offset integer provided]
    :rtype: Tuple[list, int]
    """
    result = []
    offset_param = f"&sysparm_offset={offset}"
    url = urljoin(snow_url, f"?sysparm_limit={limit}{offset_param}{query}")
    logger.debug(url)
    response = api.get(url=url, headers=HEADERS)
    if response.status_code == 200:
        try:
            result = response.json().get("result", [])
        except JSONDecodeError as e:
            logger.error("Unable to decode JSON: %s\nResponse: %i: %s", e, response.status_code, response.text)
    else:
        logger.error(
            "Unable to query ServiceNow. Status code: %s, Reason: %s",
            response.status_code,
            response.reason,
        )
    offset += limit
    logger.debug(len(result))
    return result, offset


def get_service_now_changes(snow_config: ServiceNowConfig, query: str) -> List[dict]:
    """
    Get all change requests from ServiceNow

    :param dict snow_config: ServiceNow configuration
    :param str query: Query string
    :return: List of change requests
    :rtype: List[dict]
    """
    snow_api = snow_config.api
    changes_url = urljoin(snow_config.url, "api/now/table/change_request")
    offset = 0
    limit = 500
    data = []

    while True:
        result, offset = query_service_now(
            api=snow_api,
            snow_url=changes_url,
            offset=offset,
            limit=limit,
            query=query,
        )
        data += result
        if not result:
            break

    return data


@servicenow.command(name="sync_changes")
@click.option(
    "--start_date",
    "-s",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="The start date to query ServiceNow for changes in YYYY-MM-DD format. Defaults to 30 days ago.",
    required=False,
    default=datetime.datetime.now() - datetime.timedelta(days=30),
)
@click.option(
    "--sync_all_changes",
    "-all",
    is_flag=True,
    help="Whether to Sync all change requests from ServiceNow into RegScale as Changes. Defaults to False.",
    default=False,
)
def sync_changes(
    start_date: datetime.datetime,
    # sync_attachments: bool,
    sync_all_changes: bool,
):
    """Sync change requests from ServiceNow into RegScale as Changes."""
    sync_snow_changes(
        start_date=start_date,
        sync_all_changes=sync_all_changes,
    )


def sync_snow_changes(
    start_date: datetime.datetime,
    sync_all_changes: bool = False,
) -> None:
    """
    Sync change requests from ServiceNow into RegScale as Changes

    :param datetime.datetime start_date: The start date to query SNOW for changes, ignored if sync_all_changes is True
    :param bool sync_all_changes: Whether to sync all change requests from SNOW into RegScale changes
    :rtype: None
    """
    app = check_license()
    config = app.config
    snow_config = ServiceNowConfig(reg_config=config)
    query = "&sysparm_display_value=true"

    if sync_all_changes:
        changes = get_service_now_changes(snow_config=snow_config, query=query)
    else:
        query += f"&sysparm_query=sys_created_on>={start_date.strftime('%Y-%m-%d %H:%M:%S')}"
        changes = get_service_now_changes(snow_config=snow_config, query=query)

    logger.info(f"Retrieved {len(changes)} change(s) from ServiceNow.")
    regscale_changes = Change.fetch_all_changes()

    if changes:
        sync_snow_changes_to_regscale_issues(
            changes=changes,
            regscale_changes=regscale_changes,
            app=app,
            snow_config=snow_config,
        )
        current_date = get_current_datetime(dt_format="%Y%m%d_%H-%M-%S")
        # save the snow_changes to a xlsx file
        save_data_to(
            file=Path(f"artifacts/snow_changes_{current_date}.xlsx"),
            data=changes,
            transpose_data=False,
        )
    else:
        logger.info("No changes need to be analyzed from ServiceNow.")


def sync_snow_changes_to_regscale_issues(
    changes: list[dict],
    regscale_changes: list[Change],
    app: "Application",
    snow_config: ServiceNowConfig,
) -> None:
    """
    Sync incidents from ServiceNow to RegScale

    :param list[dict] changes: List of SNOW incidents to sync to RegScale
    :param list[Change] regscale_changes: List of RegScale issues to compare to SNOW Incidents
    :param Application app: RegScale CLI application object
    :param dict snow_config: ServiceNow configuration
    :rtype: None
    """
    issues_closed = []
    with job_progress:
        creating_issues = job_progress.add_task(
            f"[#f8b737]Comparing {len(changes)} ServiceNow change(s)"
            f" and {len(regscale_changes)} RegScale change(s)...",
            total=len(changes),
        )
        app.thread_manager.submit_tasks_from_list(
            func=create_and_update_regscale_changes,
            items=changes,
            args=(
                changes,
                regscale_changes,
                snow_config,
                app,
                creating_issues,
                job_progress,
            ),
        )
        _ = app.thread_manager.execute_and_verify(terminate_after=True)
        logger.info(
            f"Analyzed {len(changes)} ServiceNow change(s), created {len(new_regscale_objects)} change(s), "
            f"updated {len(updated_regscale_objects)} change(s), and closed {len(issues_closed)} change(s) in RegScale.",
        )


def create_and_update_regscale_changes(snow_change: dict, args: Tuple) -> None:
    """
    Function to create or update changes in RegScale from ServiceNow

    :param dict snow_change: ServiceNow change request object
    :param Tuple args: Tuple of args to use during the process
    :rtype: None
    """
    # set up local variables from the passed args
    (
        snow_changes,
        regscale_changes,
        snow_config,
        app,
        task,
        progress,
    ) = args
    regscale_change: Optional[Change] = next(
        (change for change in regscale_changes if snow_change["number"] in change.title), None
    )
    change = map_snow_change_to_regscale_change(
        change=snow_change,
    )
    if regscale_change:
        change.id = regscale_change.id
        change.save()
        updated_regscale_objects.append(change)
    else:
        new_change = change.create()
        new_regscale_objects.append(new_change)
        change = new_change
    _ = Data(
        parentId=change.id,
        parentModule=Change.get_module_string(),
        dataType="JSON",
        dataSource=f"ServiceNow Change #{snow_change['number']}",
        rawData=json.dumps(snow_change),
    ).create_or_update()
    progress.update(task, advance=1)


def map_snow_change_to_regscale_change(change: dict) -> Change:
    """
    Map a ServiceNow change request to a RegScale change record

    :param dict change: ServiceNow change request to map to RegScale change object
    :return: RegScale change object
    :rtype: Change
    """
    from regscale.models.regscale_models.change import ChangePriority, ChangeStatus, ChangeType

    status_map = {
        "Approved": ChangeStatus.approved.value,
        "Not Requested": ChangeStatus.draft.value,
        "Authorize": ChangeStatus.pending_approval.value,
        "Closed": ChangeStatus.complete.value,
        "Canceled": ChangeStatus.cancelled.value,
    }
    priority_map = {
        "1 - Critical": ChangePriority.critical.value,
        "2 - High": ChangePriority.high.value,
        "3 - Moderate": ChangePriority.moderate.value,
        "4 - Low": ChangePriority.low.value,
    }
    change_type_map = {
        "Standard": ChangeType.standard.value,
        "Emergency": ChangeType.emergency.value,
        "Normal": ChangeType.normal.value,
    }

    regscale_change = Change(
        title=f'{change["short_description"]} #{change["number"]}',
        description=change["description"],
        changeReason=change.get("reason") or "No reason provided.",
        dateRequested=change["sys_created_on"],
        startChangeWindow=change.get("start_date") or change.get("opened_at"),
        endChangeWindow=change.get("end_date"),
        dateWorkCompleted=change.get("work_end") or change.get("closed_at"),
        outageRequired="No",
        priority=priority_map.get(change["priority"], ChangePriority.moderate.value),
        changeType=change_type_map.get(change.get("type", "Normal")),
        status=status_map.get(change["state"], ChangeStatus.draft.value),
        changePlan=change.get("implementation_plan"),
        riskAssessment=change.get("risk_impact_analysis"),
        rollbackPlan=change.get("backout_plan"),
        testPlan=change.get("test_plan"),
        notes=change.get("comments_and_work_notes"),
        securityImpactAssessment=change.get("impact"),
    )
    if regscale_change.dateWorkCompleted and regscale_change.status != ChangeStatus.complete.value:
        regscale_change.dateWorkCompleted = None

    return regscale_change
