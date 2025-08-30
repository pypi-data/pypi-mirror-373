#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Salesforce integration for RegScale CLI to sync Salesforce Cases with RegScale Issues"""

import base64
import mimetypes
import os
import tempfile
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import click
import simple_salesforce.exceptions
from requests.exceptions import HTTPError
from simple_salesforce import Salesforce

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    compute_hashes_in_directory,
    convert_datetime_to_regscale_string,
    create_logger,
    create_progress_object,
    error_and_exit,
    get_current_datetime,
    get_file_name,
    get_file_type,
    save_data_to,
)
from regscale.utils.threading.threadhandler import create_threads, thread_assignment
from regscale.models import File, Issue, regscale_id, regscale_module

####################################################################################################
#
# simple-salesforce Documentation:
#   https://github.com/simple-salesforce/simple-salesforce
# Salesforce API Docs:
#   https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm
# How to get Security Token:
#   https://help.salesforce.com/s/articleView?id=sf.user_security_token.htm&type=5
#
####################################################################################################


job_progress = create_progress_object()
logger = create_logger()
updated_regscale_issues = []
new_regscale_issues = []
update_counter = []
new_sf_cases = []


@click.group()
def salesforce():
    """Sync data between Salesforce Cases & RegScale Issues"""


@salesforce.command()
@regscale_id()
@regscale_module()
@click.option(
    "--sf_status",
    type=click.STRING,
    help="Salesforce status to filter Cases. (CASE SENSITIVE)",
    required=False,
    default=None,
)
@click.option(
    "--not_equal",
    is_flag=True,
    help="Exclude the provided status from the filter.",
)
def sync(
    regscale_id: int,
    regscale_module: str,
    sync_attachments: bool = True,
    sf_status: Optional[str] = None,
    not_equal: Optional[bool] = False,
):
    """Sync Salesforce cases and RegScale issues."""
    sync_sf_and_regscale(
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        sync_attachments=sync_attachments,
        sales_force_status=sf_status,
        not_equal=not_equal,
    )


def create_salesforce_client(config: dict) -> Salesforce:
    """
    Create a Salesforce client with the provided config, if values aren't
    in the provided config, it will use ENV vars

    :param dict config: config to use to create the Salesforce client
    :return: Salesforce client
    :rtype: Salesforce
    """
    # try to get the needed credentials before creating the Salesforce client
    username = os.getenv("SF_USERNAME") or config.get("salesforceUserName")
    password = os.getenv("SF_PASSWORD") or config.get("salesforcePassword")
    security_token = os.getenv("SF_TOKEN") or config.get("salesforceToken")
    if not username or not password or not security_token:
        error_and_exit(
            "Unable to retrieve Salesforce credentials, please provide them in"
            " the init.yaml or as environment variables."
        )
    # make sure the credentials aren't the ones from Application.template
    if any(credential in Application().template.values() for credential in [username, password, security_token]):
        error_and_exit("Please update the Salesforce credentials in init.yaml or set up environment variables.")
    return Salesforce(
        username=username,
        password=password,
        security_token=security_token,
    )


def sync_sf_and_regscale(
    regscale_id: int,
    regscale_module: str,
    sync_attachments: Optional[bool] = True,
    sales_force_status: Optional[str] = None,
    not_equal: Optional[bool] = False,
) -> None:
    """
    Sync Salesforce cases and RegScale issues

    :param int regscale_id: ID # from RegScale to associate cases with
    :param str regscale_module: RegScale module to associate cases with
    :param Optional[bool] sync_attachments: Sync attachments between Salesforce & RegScale, defaults to True
    :param Optional[str] sales_force_status: Status to filter Salesforce cases by, defaults to None
    :param Optional[bool] not_equal: Exclude the provided status, defaults to False
    :rtype: None
    """
    if not_equal and not sales_force_status:
        error_and_exit("Cannot use '--not-equal' without providing '--sf-status'.")

    app = check_license()
    api = Api()
    api.timeout = 60

    sf_client = create_salesforce_client(app.config)

    (
        regscale_issues,
        regscale_attachments,
    ) = Issue.fetch_issues_and_attachments_by_parent(
        parent_id=regscale_id,
        parent_module=regscale_module,
        fetch_attachments=sync_attachments,
    )

    sf_cases = fetch_sf_cases(
        sf_client=sf_client,
        sf_status=sales_force_status,
        not_equal=not_equal,
    )

    if regscale_issues:
        # sync RegScale issues to Salesforce
        if issues_to_update := sync_regscale_to_sf(
            regscale_issues=regscale_issues,
            sf_client=sf_client,
            sf_status=sales_force_status,
            sync_attachments=sync_attachments,
            attachments=regscale_attachments,
            api=api,
        ):
            with job_progress:
                # create task to update RegScale issues
                updating_issues = job_progress.add_task(
                    f"[#f8b737]Updating {len(issues_to_update)} RegScale issue(s)" "from Salesforce...",
                    total=len(issues_to_update),
                )
                # create threads to analyze Salesforce cases and RegScale issues
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

    if sf_cases:
        # sync Salesforce cases to RegScale
        with job_progress:
            # create task to create RegScale issues
            creating_issues = job_progress.add_task(
                (
                    f"[#f8b737]Analyzing {len(sf_cases)} Salesforce case(s)"
                    f" and {len(regscale_issues)} RegScale issue(s)..."
                ),
                total=len(sf_cases),
            )
            # create threads to analyze Salesforce cases and RegScale issues
            create_threads(
                process=create_and_update_regscale_issues,
                args=(
                    sf_cases,
                    sf_client,
                    regscale_issues,
                    sync_attachments,
                    app,
                    regscale_id,
                    regscale_module,
                    creating_issues,
                ),
                thread_count=len(sf_cases),
            )
            # output the final result
            logger.info(
                "Created %i Salesforce case(s), created %i issue(s) and updated %i issue(s) in RegScale.",
                len(new_sf_cases),
                len(new_regscale_issues),
                len(updated_regscale_issues),
            )
    else:
        logger.info("No cases need to be analyzed from Salesforce.")


def fetch_sf_cases(
    sf_client: Salesforce,
    sf_status: Optional[str] = None,
    not_equal: Optional[bool] = False,
) -> list:
    """
    Fetch all cases from Salesforce by generating a SOQL with the optional params

    :param Salesforce sf_client: Salesforce client to use for the request
    :param Optional[str] sf_status: Status to filter Salesforce cases by, defaults to None
    :param Optional[bool] not_equal: Exclude the provided status, defaults to False
    :return: List of Salesforce cases
    :rtype: list
    """
    sf_cases = []
    case_fields = sf_client.Case.describe()["fields"]
    operator = "!=" if not_equal else "="
    status = f"WHERE Status {operator} '{sf_status}'" if sf_status else ""
    cases_query = f"""
    SELECT {', '.join([field['name'] for field in case_fields])}
    FROM Case
    {status}
    """
    cases = sf_client.query_all(cases_query)
    sf_cases.extend(cases["records"])
    while len(sf_cases) < cases["totalSize"]:
        # extend the list of cases with the next page of results
        sf_cases.extend(sf_client.query_more(cases["nextRecordsUrl"], identifier_is_url=True)["records"])
    if sf_cases:
        # write issue data to a json file
        check_file_path("artifacts")
        save_data_to(
            file=Path("./artifacts/existingSalesforceCases.json"),
            data=sf_cases,
            output_log=False,
        )
        logger.info(
            "Saved %i Salesforce case(s) with the provided criteria, see /artifacts/existingSalesforceCases.json",
            len(sf_cases),
        )
    return sf_cases


def fetch_sf_attachments(
    sf_client: Salesforce,
    case: OrderedDict,
) -> None:
    """
    Fetch all attachments from Salesforce for the provided case

    :param Salesforce sf_client: Salesforce client to use for the request
    :param OrderedDict case: Case to fetch attachments for
    :rtype: None
    """
    attachments = None
    attempt_one = sf_client.query_all(
        f"""
            SELECT
            ContentDocumentId,
            ContentDocument.Title,
            ContentDocument.FileType,
            ContentDocument.FileExtension
            FROM ContentDocumentLink
            WHERE LinkedEntityId = '{case.get("Id") or case.get("id")}'
        """
    )
    attempt_two = sf_client.query_all(
        f"""
            SELECT Id, Name, ContentType
            FROM Attachment
            WHERE ParentId = '{case.get("Id") or case.get("id")}'
        """
    )
    if attempt_one["totalSize"] > 0 and attempt_two["totalSize"] > 0:
        attachments = {
            key: attempt_one.get(key, []) + attempt_two.get(key, []) for key in set(attempt_one).union(set(attempt_two))
        }
    elif attempt_one["totalSize"] > 0:
        attachments = attempt_one
    elif attempt_two["totalSize"] > 0:
        attachments = attempt_two
    case["Attachments"] = attachments["records"] if attachments else []


def map_case_to_regscale_issue(case: dict, config: dict, parent_id: int, parent_module: str) -> Issue:
    """
    Map Salesforce case to a RegScale issue

    :param dict case: Salesforce case
    :param dict config: Application config
    :param int parent_id: Parent record ID in RegScale
    :param str parent_module: Parent record module in RegScale
    :return: Issue object of the newly created issue in RegScale
    :rtype: Issue
    """
    import pandas as pd  # Optimize import performance

    due_date = map_case_due_date(case.get("Priority"), config)
    issue = Issue(
        title=case.get("Subject"),
        severityLevel=Issue.assign_severity(case.get("Priority")),
        issueOwnerId=config["userId"],
        dueDate=due_date,
        # pd.DataFrame.T transposes the columns and headers
        description=f"{pd.DataFrame([case]).T.to_html(justify='left', border=1)}",
        status=("Closed" if case["IsClosed"] else config["issues"]["salesforce"]["status"]),
        salesforceId=case["CaseNumber"],
        parentId=parent_id,
        parentModule=parent_module,
        dateCreated=get_current_datetime(),
        dateCompleted=get_current_datetime() if case["IsClosed"] else None,
    )
    return issue


def map_case_due_date(priority: Optional[str], config: dict) -> str:
    """
    Use the provided priority to determine the due date of the issue in RegScale

    :param Optional[str] priority: The priority of the case in Salesforce
    :param dict config: Application config
    :return: due date as a string
    :rtype: str
    """
    if not priority or priority.lower() not in config["issues"]["salesforce"].values():
        due_date = datetime.now() + timedelta(days=config["issues"]["salesforce"]["low"])
    else:
        due_date = datetime.now() + timedelta(days=config["issues"]["salesforce"][priority.lower()])
    return convert_datetime_to_regscale_string(due_date)


def create_and_update_regscale_issues(args: Tuple, thread: int) -> None:
    """
    Function to create or update issues in RegScale from Salesforce

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """
    # set up local variables from the passed args
    (
        sf_cases,
        sf_client,
        regscale_issues,
        add_attachments,
        app,
        parent_id,
        parent_module,
        task,
    ) = args
    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(sf_cases))

    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        case: OrderedDict = sf_cases[threads[i]]
        regscale_issue: Optional[Issue] = next(
            (issue for issue in regscale_issues if issue.salesforceId == case.get("CaseNumber")),
            None,
        )
        # see if the Salesforce case needs to be created as closed in RegScale
        if case["IsClosed"] and regscale_issue:
            # update the status and date completed of the RegScale issue
            regscale_issue.status = "Closed"
            regscale_issue.dateCompleted = get_current_datetime()
            # update the issue in RegScale
            updated_regscale_issues.append(Issue.update_issue(app=app, issue=regscale_issue))
        elif regscale_issue:
            # update the issue in RegScale
            updated_regscale_issues.append(Issue.update_issue(app=app, issue=regscale_issue))
        else:
            # map the Salesforce case to a RegScale issue object
            issue = map_case_to_regscale_issue(
                case=case,
                config=app.config,
                parent_id=parent_id,
                parent_module=parent_module,
            )
            # create the issue in RegScale
            if regscale_issue := Issue.insert_issue(
                app=app,
                issue=issue,
            ):
                logger.debug(
                    "Created issue #%i-%s in RegScale.",
                    regscale_issue.id,
                    regscale_issue.title,
                )
                new_regscale_issues.append(regscale_issue)
            else:
                logger.warning("Unable to create issue in RegScale.\nIssue: %s", issue.dict())
        if add_attachments and regscale_issue:
            # determine which attachments need to be uploaded to prevent duplicates by
            # getting the hashes of all Salesforce & RegScale attachments
            compare_files_for_dupes_and_upload(
                case=case,
                regscale_issue=regscale_issue,
                sf_client=sf_client,
                api=Api(),
            )
        # update progress bar
        job_progress.update(task, advance=1)


def sync_regscale_to_sf(
    regscale_issues: list[Issue],
    sf_client: Salesforce,
    api: Api,
    sync_attachments: bool = True,
    sf_status: Optional[str] = None,
    attachments: Optional[list[File]] = None,
) -> list[Issue]:
    """
    Sync issues from RegScale to Salesforce cases
    :param list[Issue] regscale_issues: list of RegScale issues to sync to Salesforce
    :param Salesforce sf_client: Salesforce client to use for case creation in Salesforce
    :param Api api: RegScale API client to move files, if sync_attachments is True
    :param bool sync_attachments: Sync attachments from RegScale to Sales, defaults to True
    :param Optional[str] sf_status: Status to set the Salesforce case to, defaults to None
    :param Optional[list[File]] attachments: List of files to sync from RegScale to Salesforce, defaults to None
    :return: list of RegScale issues that need to be updated
    :rtype: list[Issue]
    """
    issues_to_update = []
    for issue in regscale_issues:
        new_case_details = None
        # see if Salesforce case already exists
        if not issue.salesforceId:
            new_case = create_case_in_sf(
                issue=issue,
                sf_client=sf_client,
                sf_status=sf_status,
                add_attachments=sync_attachments,
                attachments=attachments,
            )
            # get the case number, creating a case only returns the ID
            new_case_details = sf_client.Case.get(new_case["id"])
            # update the RegScale issue for the Salesforce case number
            issue.salesforceId = new_case_details.get("CaseNumber")
            # add the issue to the update_issues global list
            issues_to_update.append(issue)
        elif issue.salesforceId:
            try:
                new_case_details = sf_client.Case.get_by_custom_id("CaseNumber", issue.salesforceId)
            except simple_salesforce.exceptions.SalesforceResourceNotFound:
                logger.warning("Unable to get details for Salesforce case #%s.", issue.salesforceId)
                continue
        if sync_attachments and attachments and (new_case_details and issue.salesforceId):
            compare_files_for_dupes_and_upload(
                case=new_case_details,
                regscale_issue=issue,
                sf_client=sf_client,
                api=api,
            )
    return issues_to_update


def create_case_in_sf(
    issue: Issue,
    sf_client: Salesforce,
    sf_status: Optional[str] = None,
    add_attachments: Optional[bool] = True,
    attachments: Optional[list[Issue]] = None,
    api: Optional[Api] = None,
) -> dict:
    """
    Create a new case in Salesforce

    :param Issue issue: RegScale issue object
    :param Salesforce sf_client: Salesforce client to use for case creation in Salesforce
    :param Optional[str] sf_status: Status to set the Salesforce case to, defaults to None
    :param Optional[bool] add_attachments: Whether to add attachments to new case, defaults to true
    :param Optional[list[Issue]] attachments: Dictionary containing attachments, defaults to None
    :param Optional[Api] api: API object to download attachments from RegScale, defaults to None
    :return: Newly created case in Salesforce
    :rtype: dict
    """
    new_case = sf_client.Case.create(
        {
            "Subject": f"RegScale Issue {issue.id}: {issue.title}",
            "Description": f"RegScale Issue #{issue.id} description: {issue.description}",
            "Priority": map_regscale_severity_to_sf(issue.severityLevel),
            "Status": sf_status if sf_status else "New",
        }
    )
    if new_case["errors"]:
        logger.error(
            "Unable to create case in Salesforce for RegScale issue #%i.\n%s",
            issue.id,
            new_case["errors"],
        )
    new_sf_cases.append(new_case)
    # add the attachments to the new case in Salesforce
    if add_attachments and attachments:
        if not api:
            api = Api()
            api.timeout = 60
        compare_files_for_dupes_and_upload(
            case=sf_client.Case.get(new_case["id"]),
            regscale_issue=issue,
            sf_client=sf_client,
            api=api,
        )
    return new_case


def map_regscale_severity_to_sf(severity: str) -> str:
    """
    Map RegScale severity to Salesforce priority
    :param str severity: RegScale severity
    :return: Salesforce priority
    :rtype: str
    """
    priority = "Low"
    if severity.startswith("I -"):
        priority = "High"
    elif severity.startswith("II -"):
        priority = "Medium"
    return priority


def compare_files_for_dupes_and_upload(
    case: OrderedDict, regscale_issue: Issue, sf_client: Salesforce, api: Api
) -> None:
    """
    Compare files for provided Salesforce Case and RegScale issue via hash to prevent duplicates
    and then upload the attachments to the Salesforce case and/or RegScale issue
    :param OrderedDict case: Salesforce case to compare attachments from
    :param Issue regscale_issue: RegScale issue object to compare attachments from
    :param Salesforce sf_client: Salesforce client to fetch attachments for the provided case
    :param Api api:API client to move files, if sync_attachments is True
    :rtype: None
    """
    sf_uploaded_attachments = []
    regscale_uploaded_attachments = []
    # create a temporary directory to store the downloaded attachments from Salesforce and RegScale
    with tempfile.TemporaryDirectory() as temp_dir:
        # write attachments to the temporary directory
        sf_dir, regscale_dir = download_attachments_to_directory(
            directory=temp_dir,
            case=case,
            regscale_issue=regscale_issue,
            api=api,
            sf_client=sf_client,
        )
        # get the hashes for the attachments in the RegScale and Salesforce directories
        # iterate all files in the Salesforce directory and compute their hashes
        sf_attachment_hashes = compute_hashes_in_directory(sf_dir)
        regscale_attachment_hashes = compute_hashes_in_directory(regscale_dir)

        sf_uploaded_attachments = process_attachments_and_upload_to_sf(
            regscale_attachment_hashes=regscale_attachment_hashes,
            sf_attachment_hashes=sf_attachment_hashes,
            case=case,
            regscale_issue=regscale_issue,
            sf_client=sf_client,
            api=api,
        )

        regscale_uploaded_attachments = process_attachments_and_upload_to_regscale(
            regscale_attachment_hashes=regscale_attachment_hashes,
            sf_attachment_hashes=sf_attachment_hashes,
            regscale_issue=regscale_issue,
            api=api,
        )
    output_console_summary(
        regscale_issue=regscale_issue,
        sf_case=case,
        regscale_uploads=regscale_uploaded_attachments,
        sf_uploads=sf_uploaded_attachments,
    )


def process_attachments_and_upload_to_sf(
    regscale_attachment_hashes: dict,
    sf_attachment_hashes: dict,
    case: OrderedDict,
    regscale_issue: Issue,
    sf_client: Salesforce,
    api: Api,
) -> int:
    """
    Process attachment hashes for RegScale and Salesforce and upload missing
    files to Salesforce case

    :param dict regscale_attachment_hashes: Dictionary containing RegScale attachment & hashes
    :param dict sf_attachment_hashes: Dictionary containing Salesforce attachment & hashes
    :param OrderedDict case: Salesforce case to compare attachments from
    :param Issue regscale_issue: RegScale issue object to compare attachments from
    :param Salesforce sf_client: Salesforce client to fetch attachments for the provided case
    :param Api api: API client to move files
    :return: # of attachments uploaded to Salesforce case
    :rtype: int
    """
    sf_uploaded_attachments = 0
    # check where the files need to be uploaded to before uploading
    for file_hash, file in regscale_attachment_hashes.items():
        if file_hash not in sf_attachment_hashes:
            if upload_file_to_sf(
                # If it was a newly created case, it has id, if it already existed it
                # we will use Id, with the or statement it will use whatever
                # key is in the case dictionary
                case_id=case.get("Id") or case.get("id"),
                file_path=file,
                file_name=f"RegScale_Issue_{regscale_issue.id}_{Path(file).name}",
                sf_url=sf_client.base_url,
                sf_session_id=sf_client.session_id,
                api=api,
            ):
                sf_uploaded_attachments += 1
                logger.debug(
                    "Uploaded %s to Salesforce case #%s.",
                    Path(file).name,
                    case.get("Id") or case.get("id"),
                )
            else:
                logger.warning(
                    "Unable to upload %s to Salesforce case #%s.",
                    Path(file).name,
                    case.get("Id") or case.get("id"),
                )
    return sf_uploaded_attachments


def process_attachments_and_upload_to_regscale(
    regscale_attachment_hashes: dict,
    sf_attachment_hashes: dict,
    regscale_issue: Issue,
    api: Api,
) -> int:
    """
    Process attachment hashes for RegScale and Salesforce and upload missing files to RegScale issue

    :param dict regscale_attachment_hashes: Dictionary containing RegScale attachment & hashes
    :param dict sf_attachment_hashes: Dictionary containing Salesforce attachment & hashes
    :param Issue regscale_issue: RegScale issue to upload attachments to
    :param Api api: API client to upload files to RegScale
    :return: # of attachments uploaded to RegScale issue
    :rtype: int
    """
    regscale_uploaded_attachments = 0
    for file_hash, file in sf_attachment_hashes.items():
        if file_hash not in regscale_attachment_hashes:
            with open(file, "rb") as in_file:
                if File.upload_file_to_regscale(
                    file_name=f"Salesforce_attachment_{Path(file).name}",
                    parent_id=regscale_issue.id,
                    parent_module="issues",
                    api=api,
                    file_data=in_file.read(),
                ):
                    regscale_uploaded_attachments += 1
                    logger.debug(
                        "Uploaded %s to RegScale issue #%i.",
                        Path(file).name,
                        regscale_issue.id,
                    )
                else:
                    logger.warning(
                        "Unable to upload %s to RegScale issue #%i.",
                        Path(file).name,
                        regscale_issue.id,
                    )
    return regscale_uploaded_attachments


def output_console_summary(
    regscale_issue: Issue,
    sf_case: dict,
    regscale_uploads: Optional[int] = None,
    sf_uploads: Optional[int] = None,
) -> None:
    """
    Output a summary of the files uploaded to Salesforce and RegScale to the console

    :param Issue regscale_issue: RegScale issue object
    :param dict sf_case: Salesforce case dictionary
    :param Optional[int] regscale_uploads: # of files uploaded to RegScale issue
    :param Optional[int] sf_uploads: # of files uploaded to Salesforce case
    :rtype: None
    """
    if regscale_uploads and sf_uploads:
        logger.info(
            "%i file(s) uploaded to RegScale issue #%i and %i file(s) uploaded to Salesforce Case #%s.",
            regscale_uploads,
            regscale_issue.id,
            sf_uploads,
            sf_case["CaseNumber"],
        )
    elif sf_uploads:
        logger.info(
            "%i file(s) uploaded to Salesforce case #%s.",
            sf_uploads,
            sf_case["CaseNumber"],
        )
    elif regscale_uploads:
        logger.info(
            "%i file(s) uploaded to RegScale issue #%i.",
            regscale_uploads,
            regscale_issue.id,
        )


def download_attachments_to_directory(
    directory: str,
    case: OrderedDict,
    regscale_issue: Issue,
    api: Api,
    sf_client: Salesforce,
) -> tuple[str, str]:
    """
    Function to download attachments from Salesforce and RegScale to a directory

    :param str directory: Directory to store the files in
    :param OrderedDict case: Salesforce case to download the attachments for
    :param Issue regscale_issue: RegScale issue to download the attachments for
    :param Api api: Api object to use for interacting with RegScale
    :param Salesforce sf_client: Salesforce client to use for interacting with Salesforce
    :return: Tuple of strings containing the Salesforce and RegScale directories
    :rtype: tuple[str, str]
    """
    # determine which attachments need to be uploaded to prevent duplicates by checking hashes
    sf_dir = os.path.join(directory, "salesforce")
    check_file_path(sf_dir, False)
    fetch_sf_attachments(
        sf_client=sf_client,
        case=case,
    )
    if case.get("Attachments"):
        # download all attachments from Salesforce case to the Salesforce directory in temp_dir
        for attachment in case["Attachments"]:
            download_attachment_from_sf(
                sf_url=sf_client.base_url,
                sf_session_id=sf_client.session_id,
                attachment=attachment,
                api=api,
                directory=sf_dir,
            )

    # get the regscale issue attachments
    regscale_issue_attachments = File.get_files_for_parent_from_regscale(
        api=api,
        parent_id=regscale_issue.id,
        parent_module="issues",
    )
    # create a directory for the regscale attachments
    regscale_dir = os.path.join(directory, "regscale")
    check_file_path(regscale_dir, False)
    # download regscale attachments to the directory
    for attachment in regscale_issue_attachments:
        with open(os.path.join(regscale_dir, attachment.trustedDisplayName), "wb") as file:
            file.write(
                File.download_file_from_regscale_to_memory(
                    api=api,
                    record_id=regscale_issue.id,
                    module="issues",
                    stored_name=attachment.trustedStorageName,
                    file_hash=(attachment.shaHash if attachment.shaHash else attachment.fileHash),
                )
            )
    return sf_dir, regscale_dir


def download_attachment_from_sf(
    sf_url: str,
    sf_session_id: str,
    attachment: OrderedDict,
    api: Api,
    directory: str,
) -> None:
    """
    Function to download an attachment from Salesforce and save it to the provided directory

    :param str sf_url: Salesforce base url to use for downloading the file
    :param str sf_session_id: Salesforce session id to use for authenticating the API call
    :param OrderedDict attachment: Attachment to download from Salesforce
    :param Api api: Api object to use for downloading the file
    :param str directory: Directory to save the file to
    :rtype: None
    """
    attachment_id = None
    endpoint = None
    headers = {
        "Authorization": f"Bearer {sf_session_id}",
    }
    if attachment.get("Id"):
        attachment_id = attachment["Id"]
        endpoint = "Attachment"
    elif attachment.get("ContentDocumentId"):
        attachment_id = attachment["ContentDocumentId"]
        endpoint = "Document"
    if not attachment_id or not endpoint:
        logger.warning(
            "Unable to download attachment from Salesforce case. No attachment ID found.\n%s",
            attachment,
        )
        return
    # Prepare Salesforce REST API endpoint for standard URL
    url_standard = f"{sf_url}/sobjects/{endpoint}/{attachment_id}/body"

    response = None
    # Try to download from standard URL
    try:
        response = api.get(url_standard, headers=headers)
        response.raise_for_status()
    except HTTPError:
        # Download from standard URL fails, try Lightning URL
        # Prepare Salesforce REST API endpoint for Lightning URL
        url_lightning = (
            f'https://{sf_url.split("//")[1].split(".")[0]}.lightning.force.com'
            f"/services/data/v58.0/sobjects/{endpoint}/{attachment_id}/body"
        )
        try:
            response = api.get(url_lightning, headers=headers)
            response.raise_for_status()
        except HTTPError:
            file_url = (
                f'https://{sf_url.split("//")[1].split(".")[0]}.file.force.com'
                f"/sfc/servlet.shepherd/document/download/{attachment_id}"
            )
            try:
                response = api.get(file_url, headers=headers)
                response.raise_for_status()
            except HTTPError:
                logger.error(
                    "Failed to download '%s.%s' from both standard and Lightning URLs in Salesforce.",
                    attachment["Title"],
                    attachment["FileType"].lower(),
                )
    # If a response was received, write the file data to a file
    if response.ok:
        try:
            file_name = attachment["Name"]
        except KeyError:
            file_name = f'{attachment["ContentDocument"]["Title"]}.{attachment["ContentDocument"]["FileExtension"]}'
        if not file_name:
            logger.error(
                "Unable to determine file name for attachment from Salesforce attachment.\n%s",
                attachment,
            )
            return
        with open(
            os.path.join(
                directory,
                file_name.replace(" ", "_"),
            ),
            "wb",
        ) as out_file:
            out_file.write(response.content)


def upload_file_to_sf(
    case_id: str,
    file_path: str,
    file_name: str,
    sf_url: str,
    sf_session_id: str,
    api: Api,
) -> bool:
    """
    Function to upload a file to Salesforce via API

    :param str case_id: Salesforce Case ID to upload the file to
    :param str file_path: File path to the file to upload
    :param str file_name: Desired name of the file once uploaded
    :param str sf_url: Salesforce URL to use for uploading the file
    :param str sf_session_id: Salesforce session ID to use for authenticating the API call
    :param Api api: Api object to use for uploading the file
    :return: If upload was successful
    :rtype: bool
    """
    response = None
    with open(file_path, "rb") as in_file:
        data = in_file.read()

    # Encode file data in base64
    data = base64.b64encode(data).decode()

    # Prepare Salesforce REST API headers
    headers = {
        "Authorization": "Bearer " + sf_session_id,
        "Content-Type": "application/json",
    }

    # Prepare Salesforce REST API endpoint
    url_standard = f"{sf_url}/sobjects/Attachment"

    # Prepare Salesforce REST API request body
    body = {
        "Name": file_name,
        "ParentId": case_id,
        "Body": data,
        "ContentType": mimetypes.types_map[get_file_type(file_path)],
    }

    # Make Salesforce REST API request
    try:
        response = api.post(url_standard, headers=headers, json=body)
        response.raise_for_status()
    except HTTPError:
        # If upload with standard URL fails, try Lightning URL
        # Prepare Salesforce REST API endpoint for Lightning URL
        url_lightning = (
            f'https://{sf_url.split("//")[1].split(".")[0]}.lightning.force.com'
            f"/services/data/v52.0/sobjects/Attachment"
        )
        try:
            response = api.post(url_lightning, headers=headers, json=body)
            response.raise_for_status()
        except HTTPError:
            logger.error(
                "Failed to upload '%s' using both standard and Lightning URLs in Salesforce.",
                get_file_name(file_path),
            )
    return response.ok or False


def update_regscale_issues(args: Tuple, thread: int) -> None:
    """
    Function to compare Salesforce cases and RegScale issues with threads

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
        Issue.update_issue(app=app, issue=issue)
        update_counter.append(Issue)
        logger.info(
            "RegScale Issue %i was updated with the Salesforce case number.",
            issue.id,
        )
        # update progress bar
        job_progress.update(task, advance=1)
