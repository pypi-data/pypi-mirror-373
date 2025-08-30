#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Microsoft Defender recommendations and alerts integration"""
# standard python imports
import logging
from datetime import datetime, timedelta
from os import PathLike
from pathlib import Path
from typing import Literal, Optional, Tuple, Union

import click
from rich.console import Console

from regscale.core.app.api import Api
from regscale.core.app.internal.login import is_valid
from regscale.core.app.utils.app_utils import (
    check_license,
    create_progress_object,
    error_and_exit,
    flatten_dict,
    get_current_datetime,
    reformat_str_date,
    save_data_to,
    uncamel_case,
)
from regscale.integrations.commercial.microsoft_defender.defender_api import DefenderApi
from regscale.models import File, Issue, regscale_id, regscale_module, ssp_or_component_id
from regscale.models.app_models.click import NotRequiredIf
from regscale.models.integration_models.defender_data import DefenderData
from regscale.models.integration_models.flat_file_importer import FlatFileImporter

LOGIN_ERROR = "Login Invalid RegScale Credentials, please login for a new token."
console = Console()
job_progress = create_progress_object()
logger = logging.getLogger("regscale")
unique_recs = []
issues_to_create = []
closed = []
updated = []
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
IDENTIFICATION_TYPE = "Vulnerability Assessment"
CLOUD_RECS = "Microsoft Defender for Cloud Recommendation"
APP_JSON = "application/json"
AFD_ENDPOINTS = "microsoft.cdn/profiles/afdendpoints"


######################################################################################################
#
# Adding application to Microsoft Defender API:
#   https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/exposed-apis-create-app-webapp
# Microsoft Defender 365 APIs Docs:
#   https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/exposed-apis-list?view=o365-worldwide
# Microsoft Defender for Cloud Alerts API Docs:
#   https://learn.microsoft.com/en-us/rest/api/defenderforcloud/alerts?view=rest-defenderforcloud-2022-01-01
# Microsoft Defender for Cloud Recommendations API Docs:
#   https://learn.microsoft.com/en-us/rest/api/defenderforcloud/assessments/list?view=rest-defenderforcloud-2020-01-01
# Microsoft Defender for Cloud Resources API Docs:
#   https://learn.microsoft.com/en-us/rest/api/azureresourcegraph/resourcegraph/resources/resources
#
######################################################################################################


@click.group()
def defender():
    """Create RegScale issues for each Microsoft Defender 365 Recommendation"""


@defender.command(name="authenticate")
@click.option(
    "--system",
    type=click.Choice(["cloud", "365"], case_sensitive=False),
    help="Pull recommendations from Microsoft Defender 365 or Microsoft Defender for Cloud.",
    prompt="Please choose a system",
    required=True,
)
def authenticate_in_defender(system: Literal["cloud", "365"]):
    """Obtains an access token using the credentials provided in init.yaml."""
    authenticate(system=system)


@defender.command(name="sync_365_alerts")
@regscale_id(required=False, default=None, prompt=False)
@regscale_module(required=False, default=None, prompt=False)
def sync_365_alerts(regscale_id: Optional[int] = None, regscale_module: Optional[str] = None):
    """
    Get Microsoft Defender 365 alerts and create RegScale
    issues with the information from Microsoft Defender 365.
    """
    sync_defender_and_regscale(
        parent_id=regscale_id, parent_module=regscale_module, system="365", defender_object="alerts"
    )


@defender.command(name="sync_365_recommendations")
@regscale_id(required=False, default=None, prompt=False)
@regscale_module(required=False, default=None, prompt=False)
def sync_365_recommendations(regscale_id: Optional[int] = None, regscale_module: Optional[str] = None):
    """
    Get Microsoft Defender 365 recommendations and create RegScale
    issues with the information from Microsoft Defender 365.
    """
    sync_defender_and_regscale(
        parent_id=regscale_id, parent_module=regscale_module, system="365", defender_object="recommendations"
    )


@defender.command(name="sync_cloud_resources")
@ssp_or_component_id()
def sync_cloud_resources(regscale_ssp_id: Optional[int] = None, component_id: Optional[int] = None):
    """
    Get Microsoft Defender for Cloud resources and create RegScale assets with the information from Microsoft
    Defender for Cloud.
    """
    if not regscale_ssp_id and not component_id:
        error_and_exit("Please provide a RegScale SSP ID or component ID to sync Azure resources to.")
    from regscale.integrations.commercial.microsoft_defender.defender_scanner import DefenderScanner

    scanner_kwargs = {
        "system": "cloud",
        "plan_id": regscale_ssp_id or component_id,
        "is_component": component_id is not None,
    }
    defender_scanner = DefenderScanner(**scanner_kwargs)
    defender_scanner.sync_assets(**scanner_kwargs)


@defender.command(name="export_resources")
@regscale_id()
@regscale_module()
@click.option(
    "--query_name",
    "-q",
    "-n",
    type=click.STRING,
    help="The name of the saved query to export from Microsoft Defender for Cloud resource graph queries.",
    prompt="Enter the name of the query to export",
    default=None,
    cls=NotRequiredIf,
    not_required_if=["all_queries"],
)
@click.option(
    "--no_upload",
    "-n",
    is_flag=True,
    help="Flag to skip uploading the exported .csv file to RegScale.",
    default=False,
)
@click.option(
    "--all_queries",
    "-a",
    is_flag=True,
    help="Export all saved queries from Microsoft Defender for Cloud resource graph queries.",
)
def export_resources_to_csv(
    regscale_id: int, regscale_module: str, query_name: str, no_upload: bool, all_queries: bool
):
    """
    Export data from Microsoft Defender for Cloud queries and save them to a .csv file.
    """
    export_resources(
        parent_id=regscale_id,
        parent_module=regscale_module,
        query_name=query_name,
        no_upload=no_upload,
        all_queries=all_queries,
    )


@defender.command(name="sync_cloud_alerts")
@regscale_id(required=False, default=None, prompt=False)
@regscale_module(required=False, default=None, prompt=False)
def sync_cloud_alerts(regscale_id: Optional[int] = None, regscale_module: Optional[str] = None):
    """
    Get Microsoft Defender for Cloud alerts and create RegScale
    issues with the information from Microsoft Defender for Cloud.
    """
    sync_defender_and_regscale(
        parent_id=regscale_id, parent_module=regscale_module, system="cloud", defender_object="alerts"
    )


@defender.command(name="sync_cloud_recommendations")
@regscale_id(required=False, default=None, prompt=False)
@regscale_module(required=False, default=None, prompt=False)
def sync_cloud_recommendations(regscale_id: Optional[int] = None, regscale_module: Optional[str] = None):
    """
    Get Microsoft Defender for Cloud recommendations and create RegScale
    issues with the information from Microsoft Defender for Cloud.
    """
    sync_defender_and_regscale(
        parent_id=regscale_id, parent_module=regscale_module, system="cloud", defender_object="recommendations"
    )


@defender.command(name="import_alerts")
@FlatFileImporter.common_scanner_options(
    message="File path to the folder containing Defender .csv files to process to RegScale.",
    prompt="File path to Defender files",
    import_name="defender",
)
def import_alerts(
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
    Import Microsoft Defender alerts from a CSV file
    """
    import_defender_alerts(
        folder_path,
        regscale_ssp_id,
        scan_date,
        mappings_path,
        disable_mapping,
        s3_bucket,
        s3_prefix,
        aws_profile,
        upload_file,
    )


def import_defender_alerts(
    folder_path: PathLike[str],
    regscale_ssp_id: int,
    scan_date: datetime,
    mappings_path: Path,
    disable_mapping: bool,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
    upload_file: Optional[bool] = True,
) -> None:
    """
    Import Microsoft Defender alerts from a CSV file

    :param PathLike[str] folder_path: File path to the folder containing Defender .csv files to process to RegScale
    :param int regscale_ssp_id: The RegScale SSP ID
    :param datetime scan_date: The date of the scan
    :param Path mappings_path: The path to the mappings file
    :param bool disable_mapping: Whether to disable custom mappings
    :param str s3_bucket: The S3 bucket to download the files from
    :param str s3_prefix: The S3 prefix to download the files from
    :param str aws_profile: The AWS profile to use for S3 access
    :param Optional[bool] upload_file: Whether to upload the file to RegScale after processing, defaults to True
    :rtype: None
    """
    from regscale.models.integration_models.defenderimport import DefenderImport

    FlatFileImporter.import_files(
        import_type=DefenderImport,
        import_name="Defender",
        file_types=".csv",
        folder_path=folder_path,
        object_id=regscale_ssp_id,
        scan_date=scan_date,
        mappings_path=mappings_path,
        disable_mapping=disable_mapping,
        s3_bucket=s3_bucket,
        s3_prefix=s3_prefix,
        aws_profile=aws_profile,
        upload_file=upload_file,
    )


def authenticate(system: Literal["cloud", "365"]) -> None:
    """
    Obtains an access token using the credentials provided in init.yaml

    :param Literal["cloud", "365"] system: The system to authenticate for, either Defender 365 or Defender for Cloud
    :rtype: None
    """
    _ = check_license()
    defender_api = DefenderApi(system=system)
    defender_api.get_token()


def sync_defender_and_regscale(
    parent_id: Optional[int] = None,
    parent_module: Optional[str] = None,
    system: Literal["365", "cloud"] = "365",
    defender_object: Literal["alerts", "recommendations"] = "recommendations",
) -> None:
    """
    Sync Microsoft Defender data with RegScale

    :param Optional[int] parent_id: The RegScale ID to sync the alerts to, defaults to None
    :param Optional[str] parent_module: The RegScale module to sync the alerts to, defaults to None
    :param Literal["365", "cloud"] system: The system to sync the alerts from, defaults to "365"
    :param Literal["alerts", "recommendations"] defender_object: The type of data to sync, defaults to "recommendations"
    :rtype: None
    """
    app = check_license()
    api = Api()
    # check if RegScale token is valid:
    if not is_valid(app=app):
        error_and_exit(LOGIN_ERROR)
    defender_api = DefenderApi(system=system)
    mapping_key = f"{system}_{defender_object}"
    url_mapping = {
        "365_alerts": "https://api.securitycenter.microsoft.com/api/alerts",
        "365_recommendations": "https://api.securitycenter.microsoft.com/api/recommendations",
        "cloud_alerts": f'https://management.azure.com/subscriptions/{app.config["azureCloudSubscriptionId"]}/'
        + "providers/Microsoft.Security/alerts?api-version=2022-01-01",
        "cloud_recommendations": f"https://management.azure.com/subscriptions/{app.config['azureCloudSubscriptionId']}/"
        + "providers/Microsoft.Security/assessments?api-version=2020-01-01&$expand=metadata",
    }
    url = url_mapping[mapping_key]
    defender_key = "id" if system == "365" else "name"
    mapping_func = {
        "365_alerts": map_365_alert_to_issue,
        "365_recommendations": map_365_recommendation_to_issue,
        "cloud_alerts": map_cloud_alert_to_issue,
        "cloud_recommendations": map_cloud_recommendation_to_issue,
    }
    logging_object = f"{defender_object[:-1]}(s)"
    logging_system = "365" if system == "365" else "for Cloud"
    logger.info(f"Retrieving Microsoft Defender {system.title()} {logging_object}...")
    if defender_objects := defender_api.get_items_from_azure(url=url):
        defender_data = [
            DefenderData(id=data[defender_key], data=data, system=system, object=defender_object)
            for data in defender_objects
        ]
        integration_field = defender_data[0].integration_field
        logger.info(f"Found {len(defender_data)} Microsoft Defender {logging_system} {logging_object}.")
    else:
        defender_data = []
        integration_field = DefenderData.get_integration_field(system=system, object=defender_object)
        logger.info(f"No Microsoft Defender {logging_system} {defender_object} found.")

    # get all issues from RegScale where the defenderId field is populated
    # if regscale_id and regscale_module aren't provided
    if parent_id and parent_module:
        app.logger.info(f"Retrieving issues from RegScale for {parent_module} #{parent_id}...")
        issues = Issue.get_all_by_parent(parent_id=parent_id, parent_module=parent_module)
        # sort the issues that have the integration field populated
        issues = [issue for issue in issues if getattr(issue, integration_field, None)]
    elif mapping_key == "cloud_recommendations":
        app.logger.warning(f"Retrieving all issues with {integration_field} populated in RegScale...")
        issues = Issue.get_all_by_manual_detection_source(value=CLOUD_RECS)
    else:
        app.logger.warning(f"Retrieving all issues with {integration_field} populated in RegScale...")
        issues = Issue.get_all_by_integration_field(field=integration_field)
    logger.info(f"Retrieved {len(issues)} issue(s) from RegScale.")

    regscale_issues = [
        DefenderData(
            id=getattr(issue, integration_field, ""), data=issue.model_dump(), system=system, object=defender_object
        )
        for issue in issues
    ]
    new_issues = []
    # create progress bars for each threaded task
    with job_progress:
        # see if there are any issues with defender id populated
        if regscale_issues:
            logger.info(f"{len(regscale_issues)} RegScale issue(s) will be analyzed.")
            # create progress bar and analyze the RegScale issues
            analyze_regscale_issues = job_progress.add_task(
                f"[#f8b737]Analyzing {len(regscale_issues)} RegScale issue(s)...", total=len(regscale_issues)
            )
            # evaluate open issues in RegScale
            app.thread_manager.submit_tasks_from_list(
                evaluate_open_issues,
                regscale_issues,
                (
                    api,
                    defender_data,
                    analyze_regscale_issues,
                ),
            )
            _ = app.thread_manager.execute_and_verify()
        else:
            logger.info("No issues from RegScale need to be analyzed.")
        # compare defender 365 recommendations and RegScale issues
        # while removing duplicates, updating existing RegScale Issues,
        # and adding new unique recommendations to unique_recs global variable
        if defender_data:
            logger.info(
                f"Comparing {len(defender_data)} Microsoft Defender {logging_system} {logging_object} "
                f"and {len(regscale_issues)} RegScale issue(s).",
            )
            compare_task = job_progress.add_task(
                f"[#ef5d23]Comparing {len(defender_data)} Microsoft Defender {logging_system} {logging_object} and "
                + f"{len(regscale_issues)} RegScale issue(s)...",
                total=len(defender_data),
            )
            app.thread_manager.submit_tasks_from_list(
                compare_defender_and_regscale,
                defender_data,
                (
                    api,
                    regscale_issues,
                    defender_key,
                    compare_task,
                ),
            )
            _ = app.thread_manager.execute_and_verify()
        # start threads and progress bar for # of issues that need to be created
        if len(unique_recs) > 0:
            logger.info("Prepping %s issue(s) for creation in RegScale.", len(unique_recs))
            create_issues = job_progress.add_task(
                f"[#21a5bb]Prepping {len(unique_recs)} issue(s) for creation in RegScale...",
                total=len(unique_recs),
            )
            app.thread_manager.submit_tasks_from_list(
                prep_issues_for_creation,
                unique_recs,
                (
                    mapping_func[mapping_key],
                    api.config,
                    defender_key,
                    parent_id,
                    parent_module,
                    create_issues,
                ),
            )
            _ = app.thread_manager.execute_and_verify()
            logger.info(
                "%s/%s issue(s) ready for creation in RegScale.",
                len(issues_to_create),
                len(unique_recs),
            )
            new_issues = Issue.batch_create(issues_to_create, progress_context=job_progress)
            logger.info(f"Created {len(new_issues)} issue(s) in RegScale.")
    # check if issues needed to be created, updated or closed and print the appropriate message
    if (len(unique_recs) + len(updated) + len(closed)) == 0:
        logger.info("[green]No changes required for existing RegScale issue(s)!")
    else:
        logger.info(
            f"{len(new_issues)} issue(s) created, {len(updated)} issue(s)"
            + f" updated and {len(closed)} issue(s) were closed in RegScale."
        )


def get_due_date(score: Union[str, int, None], config: dict, key: str) -> str:
    """
    Function to return due date based on the severity score of
    the Microsoft Defender recommendation; the values are in the init.yaml
    and if not, use the industry standards

    :param Union[str, int, None] score: Severity score from Microsoft Defender
    :param dict config: Application config
    :param str key: The key to use for init.yaml
    :return: Due date for the issue
    :rtype: str
    """
    # check severity score and assign it to the appropriate due date
    # using the init.yaml specified days
    today = datetime.now().strftime("%m/%d/%y")

    if not score:
        score = 0

    # check if the score is a string, if so convert it to an int & determine due date
    if isinstance(score, str):
        if score.lower() == "low":
            score = 3
        elif score.lower() == "medium":
            score = 5
        elif score.lower() == "high":
            score = 9
        else:
            score = 0
    if score >= 7:
        days = config["issues"][key]["high"]
    elif 4 <= score < 7:
        days = config["issues"][key]["moderate"]
    else:
        days = config["issues"][key]["low"]
    due_date = datetime.strptime(today, "%m/%d/%y") + timedelta(days=days)
    return due_date.strftime(DATE_FORMAT)


def format_description(defender_data: dict, tenant_id: str) -> str:
    """
    Function to format the provided dictionary into an HTML table

    :param dict defender_data: Microsoft Defender data as a dictionary
    :param str tenant_id: The Microsoft Defender tenant ID
    :return: HTML table as a string
    :rtype: str
    """
    url = get_defender_url(defender_data, tenant_id)
    defender_data = flatten_dict(data=defender_data)
    payload = create_payload(defender_data)  # type: ignore
    description = create_html_table(payload, url)
    return description


def get_defender_url(rec: dict, tenant_id: str) -> str:
    """
    Function to get the URL for the Microsoft Defender data

    :param dict rec: Microsoft Defender data as a dictionary
    :param str tenant_id: The Microsoft Defender tenant ID
    :return: URL as a string
    :rtype: str
    """
    try:
        url = rec["properties"]["alertUri"]
    except KeyError:
        url = f"https://security.microsoft.com/security-recommendations?tid={tenant_id}"
    return f'<a href="{url}">{url}</a>'


def create_payload(rec: dict) -> dict:
    """
    Function to create a payload for the Microsoft Defender data

    :param dict rec: Microsoft Defender data as a dictionary
    :return: Payload as a dictionary
    :rtype: dict
    """
    payload = {}
    skip_keys = ["associatedthreats", "alerturi", "investigation steps"]
    for key, value in rec.items():
        key = key.replace("propertiesExtendedProperties", "").replace("properties", "")
        if isinstance(value, list) and len(value) > 0 and key.lower() not in skip_keys:
            payload[uncamel_case(key)] = process_list_value(value)
        elif key.lower() not in skip_keys and "entities" not in key.lower():
            if not isinstance(value, list):
                payload[uncamel_case(key)] = value
    return payload


def process_list_value(value: list) -> str:
    """
    Function to process the list value for the Microsoft Defender data

    :param list value: List of values
    :return: Processed list value as a string
    :rtype: str
    """
    if isinstance(value[0], dict):
        return "".join(f"</br>{k}: {v}" for item in value for k, v in item.items())
    elif isinstance(value[0], list):
        return "".join("</br>".join(item) for item in value)
    else:
        return "</br>".join(value)


def create_html_table(payload: dict, url: str) -> str:
    """
    Function to create an HTML table for the Microsoft Defender data

    :param dict payload: Payload for the Microsoft Defender data
    :param str url: URL for the Microsoft Defender data
    :return: HTML table as a string
    :rtype: str
    """
    description = '<table style="border: 1px solid;">'
    for key, value in payload.items():
        if value:
            if "time" in key.lower():
                value = reformat_str_date(value, dt_format="%b %d, %Y")
            description += (
                f'<tr><td style="border: 1px solid;"><b>{key}</b></td>'
                f'<td style="border: 1px solid;">{value}</td></tr>'
            )
    description += (
        '<tr><td style="border: 1px solid;"><b>View in Defender</b></td>'
        f'<td style="border: 1px solid;">{url}</td></tr>'
    )
    description += "</table>"
    return description


def compare_defender_and_regscale(def_data: DefenderData, args: Tuple) -> None:
    """
    Function to check for duplicates between issues in RegScale
    and recommendations/alerts from Microsoft Defender while using threads

    :param DefenderData def_data: Microsoft Defender data
    :param Tuple args: Tuple of args to use during the process
    :rtype: None
    """
    # set local variables with the args that were passed
    api, issues, defender_key, task = args

    # see if recommendation has been analyzed already
    if not def_data.analyzed:
        # change analyzed flag
        def_data.analyzed = True

        # set duplication flag to false
        dupe_check = False

        # iterate through the RegScale issues with defenderId populated
        for issue in issues:
            # check if the RegScale key == Windows Defender ID
            if issue.data.get(issue.integration_field) == def_data.data[defender_key]:
                # change the duplication flag to True
                dupe_check = True
                # check if the RegScale issue is closed or cancelled
                if issue.data["status"].lower() in ["closed", "cancelled"]:
                    # reopen RegScale issue because Microsoft Defender has
                    # recommended it again
                    change_issue_status(
                        api=api,
                        status=api.config["issues"][issue.init_key]["status"],
                        issue=issue.data,
                        rec=def_data,
                        rec_type=issue.init_key,
                    )
        # check if the recommendation is a duplicate
        if dupe_check is False:
            # append unique recommendation to global unique_reqs
            unique_recs.append(def_data)
    job_progress.update(task, advance=1)


def evaluate_open_issues(issue: DefenderData, args: Tuple) -> None:
    """
    function to check for Open RegScale issues against Microsoft
    Defender recommendations and will close the issues that are
    no longer recommended by Microsoft Defender while using threads

    :param DefenderData issue: Microsoft Defender data
    :param Tuple args: Tuple of args to use during the process
    :rtype: None
    """
    # set up local variables from the passed args
    api, defender_data, task = args

    defender_data_dict = {defender_data.id: defender_data for defender_data in defender_data if defender_data.id}

    # check if the issue has already been analyzed
    if not issue.analyzed:
        # set analyzed to true
        issue.analyzed = True

        # check if the RegScale defenderId was recommended by Microsoft Defender
        if issue.data.get(issue.integration_field) not in defender_data_dict and issue.data["status"] not in [
            "Closed",
            "Cancelled",
        ]:
            # the RegScale issue is no longer being recommended and the issue
            # status is not closed or cancelled, we need to close the issue
            change_issue_status(
                api=api,
                status="Closed",
                issue=issue.data,
                rec=defender_data_dict.get(issue.data.get(issue.integration_field)),
                rec_type=issue.init_key,
            )
    job_progress.update(task, advance=1)


def change_issue_status(
    api: Api,
    status: str,
    issue: dict,
    rec: Optional[DefenderData] = None,
    rec_type: str = None,
) -> None:
    """
    Function to change a RegScale issue to the provided status

    :param Api api: API object
    :param str status: Status to change the provided issue to
    :param dict issue: RegScale issue
    :param dict rec: Microsoft Defender recommendation, defaults to None
    :param str rec_type: The platform of Microsoft Defender (cloud or 365), defaults to None
    :rtype: None
    """
    # update issue last updated time, set user to current user and change status
    # to the status that was passed
    issue["lastUpdatedById"] = api.config["userId"]
    issue["dateLastUpdated"] = get_current_datetime(DATE_FORMAT)
    issue["status"] = status

    if not rec:
        return
    rec = rec.data

    # check if rec dictionary was passed, if not create it
    if rec_type == "defender365":
        issue["title"] = rec["recommendationName"]
        issue["description"] = format_description(defender_data=rec, tenant_id=api.config["azure365TenantId"])
        issue["severityLevel"] = Issue.assign_severity(rec["severityScore"])
        issue["issueOwnerId"] = api.config["userId"]
        issue["dueDate"] = get_due_date(score=rec["severityScore"], config=api.config, key="defender365")
    elif rec_type == "defenderCloud":
        issue["title"] = (f'{rec["properties"]["productName"]} Alert - {rec["properties"]["compromisedEntity"]}',)
        issue["description"] = format_description(defender_data=rec, tenant_id=api.config["azureCloudTenantId"])
        issue["severityLevel"] = (Issue.assign_severity(rec["properties"]["severity"]),)
        issue["issueOwnerId"] = api.config["userId"]
        issue["dueDate"] = get_due_date(
            score=rec["properties"]["severity"],
            config=api.config,
            key="defenderCloud",
        )

    # if we are closing the issue, update the date completed
    if status.lower() == "closed":
        if rec_type == "defender365":
            message = "via Microsoft 365 Defender"
        elif rec_type == "defenderCloud":
            message = "via Microsoft Defender for Cloud"
        else:
            message = "via Microsoft Defender"
        issue["dateCompleted"] = get_current_datetime(DATE_FORMAT)
        issue["description"] += f'<p>No longer reported {message} as of {get_current_datetime("%b %d,%Y")}</p>'
        closed.append(issue)
    else:
        issue["dateCompleted"] = ""
        updated.append(issue)

    # use the api to change the status of the given issue
    Issue(**issue).save()


def prep_issues_for_creation(def_data: DefenderData, args: Tuple) -> None:
    """
    Function to utilize threading and create an issues in RegScale for the assigned thread

    :param DefenderData def_data: Microsoft Defender data to create an issue for
    :param Tuple args: Tuple of args to use during the process
    :rtype: None
    """
    # set up local variables from args passed
    mapping_func, config, defender_key, parent_id, parent_module, task = args

    # set the recommendation for the thread for later use in the function
    description = format_description(defender_data=def_data.data, tenant_id=config["azure365TenantId"])

    # check if the recommendation was already created as a RegScale issue
    if not def_data.created:
        # set created flag to true
        def_data.created = True

        # set up the data payload for RegScale API
        issue = mapping_func(data=def_data, config=config, description=description)
        issue.__setattr__(def_data.integration_field, def_data.data[defender_key])
        if parent_id and parent_module:
            issue.parentId = parent_id
            issue.parentModule = parent_module
        issues_to_create.append(issue)
    job_progress.update(task, advance=1)


def map_365_alert_to_issue(data: DefenderData, config: dict, description: str) -> Issue:
    """
    Function to map a Microsoft 365 Defender alert to a RegScale issue

    :param DefenderData data: Microsoft Defender recommendation
    :param dict config: Application config
    :param str description: Description of the alert
    :return: RegScale issue object
    :rtype: Issue
    """
    return Issue(
        title=f'{data.data["title"]}',
        description=description,
        severityLevel=Issue.assign_severity(data.data["severity"]),
        dueDate=get_due_date(score=data.data["severity"], config=config, key=data.init_key),
        identification=IDENTIFICATION_TYPE,
        assetIdentifier=f'Machine ID:{data.data["machineId"]}\n'
        f'DNS Name({data.data.get("computerDnsName", "No DNS Name found")})',
        status=config["issues"][data.init_key]["status"],
        sourceReport="Microsoft Defender 365 Alert",
    )


def map_365_recommendation_to_issue(data: DefenderData, config: dict, description: str) -> Issue:
    """
    Function to map a Microsoft 365 Defender recommendation to a RegScale issue

    :param DefenderData data: Microsoft Defender recommendation
    :param dict config: Application config
    :param str description: Description of the recommendation
    :return: RegScale issue object
    :rtype: Issue
    """
    severity = data.data["severityScore"]
    return Issue(
        title=f'{data.data["recommendationName"]}',
        description=description,
        severityLevel=Issue.assign_severity(severity),
        dueDate=get_due_date(score=severity, config=config, key=data.init_key),
        identification=IDENTIFICATION_TYPE,
        status=config["issues"][data.init_key]["status"],
        vendorName=data.data["vendor"],
        sourceReport="Microsoft Defender 365 Recommendation",
    )


def map_cloud_alert_to_issue(data: DefenderData, config: dict, description: str) -> Issue:
    """
    Function to map a Microsoft Defender for Cloud alert to a RegScale issue

    :param DefenderData data: Microsoft Defender for Cloud alert
    :param dict config: Application config
    :param str description: Description of the alert
    :return: RegScale issue object
    :rtype: Issue
    """
    severity = data.data["properties"]["severity"]
    return Issue(
        title=f'{data.data["properties"]["productName"]} Alert - {data.data["properties"]["compromisedEntity"]}',
        description=description,
        severityLevel=Issue.assign_severity(severity),
        dueDate=get_due_date(
            score=severity,
            config=config,
            key=data.init_key,
        ),
        assetIdentifier="\n".join(
            resource["azureResourceId"]
            for resource in data.data["properties"].get("resourceIdentifiers", [])
            if "azureResourceId" in resource
        ),
        recommendedActions="\n".join(data.data["properties"].get("remediationSteps", [])),
        identification=IDENTIFICATION_TYPE,
        status=config["issues"]["defenderCloud"]["status"],
        vendorName=data.data["properties"]["vendorName"],
        sourceReport="Microsoft Defender for Cloud Alert",
        otherIdentifier=data.data["id"],
    )


def map_cloud_recommendation_to_issue(data: DefenderData, config: dict, description: str) -> Issue:
    """
    Function to map a Microsoft Defender for Cloud alert to a RegScale issue

    :param DefenderData data: Microsoft Defender for Cloud alert
    :param dict config: Application config
    :param str description: Description of the alert
    :return: RegScale issue object
    :rtype: Issue
    """
    metadata = data.data["properties"].get("metadata", {})
    severity = metadata.get("severity")
    resource_details = data.data["properties"].get("resourceDetails", {})
    res_parts = [
        resource_details.get("ResourceProvider"),
        resource_details.get("ResourceType"),
        resource_details.get("ResourceName"),
    ]
    res_parts = filter(None, res_parts)
    title = f"{metadata.get('displayName')}{' on ' if res_parts else ''}{'/'.join(res_parts)}"
    return Issue(
        title=title,
        description=description,
        severityLevel=Issue.assign_severity(severity),
        dueDate=get_due_date(
            score=severity,
            config=config,
            key=data.init_key,
        ),
        identification=IDENTIFICATION_TYPE,
        status=config["issues"]["defenderCloud"]["status"],
        recommendedActions=metadata.get("remediationDescription"),
        assetIdentifier=resource_details.get("Id"),
        sourceReport=CLOUD_RECS,
        manualDetectionId=data.id,
        manualDetectionSource=CLOUD_RECS,
        otherIdentifier=data.data["id"],
    )


def export_resources(parent_id: int, parent_module: str, query_name: str, no_upload: bool, all_queries: bool) -> None:
    """
    Export data from Microsoft Defender for Cloud queries and save them to a .csv file

    :param int parent_id: The RegScale ID to save the data to
    :param str parent_module: The RegScale module to save the data to
    :param str query_name: The name of the query to export from Microsoft Defender for Cloud resource graph queries
    :param bool no_upload: Flag to skip uploading the exported .csv file to RegScale
    :param bool all_queries: If True, export all saved queries from Microsoft Defender for Cloud resource graph queries
    :rtype: None
    """
    app = check_license()
    # check if RegScale token is valid:
    if not is_valid(app=app):
        error_and_exit(LOGIN_ERROR)
    defender_api = DefenderApi(system="cloud")
    cloud_queries = defender_api.fetch_queries_from_azure()
    # Add user feedback if no queries are found
    if not cloud_queries:
        logger.warning("No saved queries found in Azure. Please create at least one query to use this export function.")
        return
    if all_queries:
        logger.info(f"Exporting all {len(cloud_queries)} queries...")
        for query in cloud_queries:
            fetch_save_and_upload_query(
                defender_api=defender_api,
                query=query,
                parent_id=parent_id,
                parent_module=parent_module,
                no_upload=no_upload,
            )
    else:
        query = prompt_user_for_query_selection(queries=cloud_queries, query_name=query_name)
        fetch_save_and_upload_query(
            defender_api=defender_api,
            query=query,
            parent_id=parent_id,
            parent_module=parent_module,
            no_upload=no_upload,
        )


def prompt_user_for_query_selection(queries: list, query_name: Optional[str] = None) -> dict:
    """
    Function to prompt the user to select a query from a list of queries

    :param list queries: The list of queries to select from
    :param str query_name: The name of the query to select, defaults to None
    :return: The selected query
    :rtype: dict
    """
    if query_name and any(q for q in queries if q["name"].lower() == query_name.lower()):
        return next(q for q in queries if q["name"].lower() == query_name.lower())
    query = click.prompt("Select a query", type=click.Choice([query["name"] for query in queries]), show_choices=True)
    return next(q for q in queries if q["name"].lower() == query.lower())


def fetch_save_and_upload_query(
    defender_api: DefenderApi, query: dict, parent_id: int, parent_module: str, no_upload: bool
) -> None:
    """
    Function to fetch Microsoft Defender queries from Azure and save them to a .xlsx file

    :param DefenderApi defender_api: The Defender API object, used to call Microsoft Defender
    :param dict query: The query object to parse and run
    :param int parent_id: The RegScale ID to upload the results to
    :param str parent_module: The RegScale module to upload the results to
    :param bool no_upload: Flag to skip uploading the exported .csv file to RegScale
    :rtype: None
    """
    logger.info(f"Exporting data from Microsoft Defender for Cloud query: {query['name']}...")
    data = defender_api.fetch_and_run_query(query=query)
    todays_date = get_current_datetime(dt_format="%Y%m%d")
    file_path = Path(f"./artifacts/{query['name']}_{todays_date}.csv")
    save_data_to(file=file_path, data=data, transpose_data=False)
    if not no_upload and File.upload_file_to_regscale(
        file_name=file_path,
        parent_id=parent_id,
        parent_module=parent_module,
        api=defender_api.api,
    ):
        logger.info(f"Successfully uploaded {file_path.name} to {parent_module} #{parent_id} in RegScale.")
