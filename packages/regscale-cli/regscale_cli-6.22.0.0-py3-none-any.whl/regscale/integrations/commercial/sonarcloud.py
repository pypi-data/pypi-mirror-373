#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale SonarCloud Integration"""

import logging
import math
from typing import Optional
from urllib.parse import urljoin

import click
import requests  # type: ignore

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    create_progress_object,
    days_between,
    error_and_exit,
    get_current_datetime,
)
from regscale.models import regscale_id, regscale_module
from regscale.models.regscale_models.assessment import Assessment
from regscale.models.regscale_models.issue import Issue

logger = logging.getLogger("regscale")


def get_sonarcloud_results(
    config: dict, organization: Optional[str] = None, branch: Optional[str] = None, project_key: Optional[str] = None
) -> list[list[dict]]:
    """
    Retrieve Sonarcloud Results from the Sonarcloud.io API

    :param dict config: RegScale CLI configuration
    :param Optional[str] organization: Organization name to filter results, defaults to None
    :param Optional[str] branch: Branch name to filter results, defaults to None
    :param Optional[str] project_key: SonarCloud Project Key, defaults to None
    :return: json response data from API GET request
    :rtype: list[list[dict]]
    """
    # create an empty list to hold multiple pages of data
    complete = []
    # api endpoint
    url = urljoin(config["sonarUrl"], "/api/issues/search")
    # SONAR_TOKEN from Sonarcloud
    token = config["sonarToken"]
    # arguments to pass to the API call
    params = {
        "statuses": "OPEN, CONFIRMED, REOPENED",
        "ps": 500,
    }
    if organization and project_key:
        params["componentKeys"] = project_key
    if organization:
        params["organization"] = organization
    if branch:
        params["branch"] = branch
    if project_key:
        params["projectKeys"] = project_key
    # GET request pulls in data to check results size
    logger.info("Fetching issues from SonarCloud/Qube...")
    r = requests.get(url, auth=(str(token), ""), params=params)
    if r.status_code != 200:
        error_and_exit(f"Sonarcloud API call failed with status code {r.status_code}: {r.reason}\n{r.text}")
    # if the status code does not equal 200
    if r and not r.ok:
        # exit the script gracefully
        error_and_exit(f"Sonarcloud API call failed please check the configuration\n{r.status_code}: {r.text}")
    # pull in response data to a dictionary
    data = r.json()
    # find the total results number
    total = data["paging"]["total"]
    complete.extend(data.get("issues", []))
    # find the number of results in each result page
    size = data["paging"]["pageSize"]
    # calculate the number of pages to iterate through sequentially
    pages = math.ceil(total / size)
    # loop through each page number
    for i in range(2, pages + 1, 1):
        # parameters to pass to the API call
        params["p"] = str(i)
        # for each page make a GET request to pull in the data
        r = requests.get(url, auth=(str(token), ""), params=params)
        # pull in response data to a dictionary
        data = r.json()
        # extract only the issues from the data
        issues = data["issues"]
        # add each page to the total results page
        complete.extend(issues)
    # return the list of json response objects for use
    logger.info(f"Retrieved {len(complete)}/{total} issue(s) from SonarCloud/Qube.")
    return complete


def build_data(
    api: Api, organization: Optional[str] = None, branch: Optional[str] = None, project_key: Optional[str] = None
) -> list[dict]:
    """
    Build vulnerability alert data list

    :param Api api: API object
    :param Optional[str] organization: Organization name to filter results, defaults to None
    :param Optional[str] branch: Branch name to filter results, defaults to None
    :param Optional[str] project_key: SonarCloud Project Key, defaults to None
    :return: vulnerability data list
    :rtype: list[dict]
    """
    # execute GET request
    data = get_sonarcloud_results(config=api.config, organization=organization, branch=branch, project_key=project_key)
    # create empty list to hold json response dicts
    vulnerability_data_list = []
    # loop through the lists in API response data
    for issue in data:
        # loop through the list of dicts in the API response data
        # format datetime stamp to use with days_between function
        create_date = issue["creationDate"][0:19] + "Z"
        # build vulnerability list
        vulnerability_data_list.append(
            {
                "key": issue["key"],
                "severity": issue["severity"],
                "component": issue["component"],
                "status": issue["status"],
                "message": issue["message"],
                "creationDate": issue["creationDate"][0:19],
                "updateDate": issue["updateDate"][0:19],
                "type": issue["type"],
                "days_elapsed": days_between(vuln_time=create_date),
            }
        )
    return vulnerability_data_list


def build_dataframes(sonar_data: list[dict]) -> str:
    """
    Build pandas dataframes from vulnerability alert data list

    :param list[dict] sonar_data: SonarCloud alerts and issues data
    :return: dataframe as an HTML table
    :rtype: str
    """
    import pandas as pd  # Optimize import performance

    df = pd.DataFrame(sonar_data)
    # sort dataframe by severity
    df.sort_values(by=["severity"], inplace=True)
    # reset and drop the index
    df.reset_index(drop=True, inplace=True)
    # convert the dataframe to an html table
    output = df.to_html(header=True, index=False, justify="center", border=1)
    return output


def create_alert_assessment(
    sonar_data: list[dict], api: Api, parent_id: Optional[int] = None, parent_module: Optional[str] = None
) -> Optional[int]:
    """
    Create Assessment containing SonarCloud alerts

    :param list[dict] sonar_data: SonarCloud alerts and issues data
    :param Api api: API object
    :param Optional[int] parent_id: Parent ID of the assessment, defaults to None
    :param Optional[str] parent_module: Parent module of the assessment, defaults to None
    :return: New Assessment ID, if created
    :rtype: Optional[int]
    """
    # create the assessment report HTML table
    df_output = build_dataframes(sonar_data)
    # build assessment model data
    assessment_data = Assessment(
        leadAssessorId=api.config["userId"],
        title="SonarCloud Code Scan Assessment",
        assessmentType="Control Testing",
        plannedStart=get_current_datetime(),
        plannedFinish=get_current_datetime(),
        assessmentReport=df_output,
        assessmentPlan="Complete the child issues created by the SonarCloud code scan results that were retrieved by the API. The assessment will fail if any high severity vulnerabilities has a days_elapsed value greater than or equal to 10 days.",
        createdById=api.config["userId"],
        dateCreated=get_current_datetime(),
        lastUpdatedById=api.config["userId"],
        dateLastUpdated=get_current_datetime(),
        status="In Progress",
    )
    if parent_id and parent_module:
        assessment_data.parentId = parent_id
        assessment_data.parentModule = parent_module
    # if assessmentResult is changed to Pass / Fail then status has to be
    # changed to complete and a completion date has to be passed
    for vulnerability in sonar_data:
        if vulnerability["severity"] == "CRITICAL" and vulnerability["days_elapsed"] >= 10:
            assessment_data.status = "Complete"
            assessment_data.actualFinish = get_current_datetime()
            assessment_data.assessmentResult = "Fail"

    # create a new assessment in RegScale
    if new_assessment := assessment_data.create():
        # log assessment creation result
        api.logger.debug("Assessment was created successfully")
        return new_assessment.id
    else:
        api.logger.debug("Assessment was not created")
        return None


def create_alert_issues(
    parent_id: Optional[int] = None,
    parent_module: Optional[str] = None,
    organization: Optional[str] = None,
    branch: Optional[str] = None,
    project_key: Optional[str] = None,
) -> None:
    """
    Create child issues from the alert assessment

    :param Optional[int] parent_id: Parent ID record to associate the assessment to, defaults to None
    :param Optional[str] parent_module: Parent module to associate the assessment to, defaults to None
    :param Optional[str] organization: Organization name to filter results, defaults to None
    :param Optional[str] branch: Branch name to filter results, defaults to None
    :param Optional[str] project_key: SonarCloud Project Key, defaults to None
    :rtype: None
    """
    # set environment and application configuration
    app = Application()
    api = Api()
    sonar_data = build_data(api=api, organization=organization, branch=branch, project_key=project_key)
    # execute POST request and return new assessment ID
    assessment_id = create_alert_assessment(
        sonar_data=sonar_data, api=api, parent_id=parent_id, parent_module=parent_module
    )

    # create vulnerability data list
    # loop through each vulnerability alert in the list
    with create_progress_object() as progress:
        task = progress.add_task("Creating/updating issue(s) in RegScale...", total=len(sonar_data))
        for vulnerability in sonar_data:
            # create issue model
            issue_data = Issue(
                title="Sonarcloud Code Scan",  # Required
                dateCreated=get_current_datetime("%Y-%m-%dT%H:%M:%S"),
                description=vulnerability["message"],
                severityLevel=Issue.assign_severity(vulnerability["severity"]),  # Required
                dueDate=Issue.get_due_date(
                    severity=vulnerability["severity"].lower(), config=app.config, key="sonarcloud"
                ),
                identification="Code scan assessment",
                status="Open",
                assessmentId=assessment_id,
                parentId=parent_id or assessment_id,
                parentModule=parent_module or "assessments",
                sourceReport="SonarCloud/Qube",
                otherIdentifier=vulnerability["key"],
            )
            # log issue creation result
            if issue_data.create_or_update(bulk_create=True, bulk_update=True):
                logger.debug("Issue was created/updated successfully")
            else:
                logger.debug("Issue was not created.")
            progress.advance(task)
        Issue.bulk_save(progress)


@click.group()
def sonarcloud() -> None:
    """
    Create an assessment and child issues in RegScale from SonarCloud alerts.
    """
    pass


@sonarcloud.command(name="sync_alerts")
@regscale_id(required=False, default=None)
@regscale_module(required=False, default=None)
@click.option(
    "--organization",
    "-o",
    type=click.STRING,
    help="Organization name to filter results, defaults to None",
    default=None,
)
@click.option("--branch", "-b", type=click.STRING, help="Branch name to filter results, defaults to None", default=None)
@click.option("--project_key", "-p", type=click.STRING, help="SonarCloud Project Key, defaults to None", default=None)
def create_alerts(
    regscale_id: Optional[int] = None,
    regscale_module: Optional[str] = None,
    organization: Optional[str] = None,
    branch: Optional[str] = None,
    project_key: Optional[str] = None,
) -> None:
    """
    Create a child assessment and child issues in RegScale from SonarCloud alerts.
    """
    create_alert_issues(
        parent_id=regscale_id,
        parent_module=regscale_module,
        organization=organization,
        branch=branch,
        project_key=project_key,
    )
