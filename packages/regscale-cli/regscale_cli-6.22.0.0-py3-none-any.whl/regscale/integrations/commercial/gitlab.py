#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale Gitlab integration"""

# standard python imports
import os
import re
import sys
from urllib.parse import urljoin

import click
import markdown
import requests
from rich.progress import Progress

from regscale.core.app.internal.login import is_valid
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_license,
    create_progress_object,
    error_and_exit,
    get_current_datetime,
)
from regscale.models import regscale_id, regscale_module
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.link import Link

job_progress = create_progress_object()
logger = create_logger()


@click.group()
def gitlab():
    """GitLab integration to pull issues via API."""


@gitlab.command(name="sync_issues", help="Integration to GitLab to sync issues into a module.")
@regscale_id()
@regscale_module()
@click.option("--gitlab_url", "-u", default="https://gitlab.com", help="GitLab URL", required=True)
@click.option(
    "--gitlab_project_id",
    "-gpid",
    required=True,
    help="The ID of the GitLab project to pull issues from.",
    default=os.environ.get("GITLAB_PROJECT"),
)
@click.option(
    "--api_token",
    "-t",
    required=True,
    help="Your GitLab API token with API read access.",
    default=os.environ.get("GITLAB_API_TOKEN"),
)
@click.option(
    "--include_links",
    "-l",
    is_flag=True,
    help="Include links from the issue description.",
    default=False,
)
def sync_issues(
    regscale_id: int,
    regscale_module: str,
    gitlab_url: str,
    gitlab_project_id: int,
    api_token: str,
    include_links: bool,
):
    """Sync issues from a GitLab project into a RegScale record."""
    run_sync_issues(
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        gitlab_url=gitlab_url,
        gitlab_project_id=gitlab_project_id,
        api_token=api_token,
        include_links=include_links,
    )


def run_sync_issues(
    regscale_id: int,
    regscale_module: str,
    gitlab_url: str,
    gitlab_project_id: int,
    api_token: str,
    include_links: bool,
) -> None:
    """Sync issues from a GitLab project into a module

    :param int regscale_id: The RegScale ID to sync issues to
    :param str regscale_module: The RegScale module to sync issues to
    :param str gitlab_url: The GitLab URL to sync issues from
    :param int gitlab_project_id: The GitLab project ID to sync issues from
    :param str api_token: The GitLab API token to use
    :param bool include_links: Whether to include links from the issue description
    :rtype: None
    """
    app = check_license()
    if not is_valid(app=app):
        logger.warn("RegScale token is invalid. please login.")
        sys.exit(1)

    with job_progress:
        gitlab_issues = get_issues_from_gitlab(gitlab_url, gitlab_project_id, api_token, job_progress)

        regscale_issues = get_regscale_issues(regscale_id, regscale_module, job_progress)
        logger.debug(f"Fetched {len(regscale_issues)} issues from RegScale.")

        # Convert the issues to your desired format
        issues = convert_issues(
            gitlab_issues,
            regscale_id,
            regscale_module,
            include_links,
            job_progress,
        )

        # # Save or update the converted issues
        save_or_update_issues(issues, regscale_issues, job_progress)


def get_regscale_issues(regscale_id: int, regscale_module: str, job_progress: Progress) -> list:
    """Function to fetch issues from RegScale

    :param int regscale_id: The RegScale ID to fetch issues for
    :param str regscale_module: The RegScale module to fetch issues for
    :param Progress job_progress: The progress object to use for updating
    :return: list of regscale issues
    :rtype: list
    """
    app = check_license()
    task = job_progress.add_task("[#f8b737]Fetching issues from regscale", total=1)
    if regscale_module == "securityplans":
        existing_issues = Issue.fetch_issues_by_ssp(app=app, ssp_id=regscale_id)
        logger.info(f"Fetched {len(existing_issues)} issues from RegScale by SSP.")
    else:
        existing_issues = Issue.fetch_issues_by_parent(
            app=app, regscale_id=regscale_id, regscale_module=regscale_module
        )
        logger.info(f"Fetched {len(existing_issues)} issues from RegScale by issue parent.")
    job_progress.update(task, advance=1)
    return existing_issues


def save_or_update_issues(gitlab_issues: list, regscale_issues: list, job_progress: Progress) -> None:
    """Function to save or update issues from GitLab to RegScale

    :param list gitlab_issues: The list of GitLab issues to save or update
    :param list regscale_issues: The list of RegScale issues to save or update
    :param Progress job_progress: The progress object to use for updating
    :rtype: None
    """
    app = check_license()
    # figure out which issues need to be updated vs inserted
    task = job_progress.add_task(
        "[#f8b737]Saving issues from GitLab to RegScale...",
        total=len(gitlab_issues),
    )
    regscale_dict = {regscale_issue.dependabotId: regscale_issue for regscale_issue in regscale_issues}

    for gitlab_issue_obj in gitlab_issues:
        gitlab_issue = gitlab_issue_obj.get("issue")
        # if we have the issue already in the regscale dict, check and update it
        if gitlab_issue.dependabotId in regscale_dict:
            regscale_issue = regscale_dict.get(gitlab_issue.dependabotId)
            # has it updated?
            if regscale_issue.__eq__(gitlab_issue) is False:
                gitlab_issue.id = regscale_issue.id
                try:
                    Issue.update_issue(app=app, issue=gitlab_issue)
                    logger.info(f"Updated issue {gitlab_issue.id}")
                except Exception as vex:
                    logger.error(vex)
                existing_links = Link.fetch_links_by_parent(app, gitlab_issue.id, "issues")
                for link in gitlab_issue_obj.get("links", []):
                    # set here for comparison purposes
                    link.parentID = gitlab_issue.id
                    if link not in existing_links:
                        try:
                            new_link = Link.insert_link(app=app, link=link)
                            logger.info(f"Inserted link {new_link.id}")
                            # Add the new link to the existing_links list
                            existing_links.append(new_link)
                        except Exception as ex:
                            logger.error(ex)

        # insert new issue
        else:
            try:
                issue = Issue.insert_issue(app=app, issue=gitlab_issue)
                if issue is not None and issue.id is not None:
                    logger.info(f"Inserted issue {issue.id}")
            except Exception as ex:
                logger.error(ex)
            for link in gitlab_issue_obj.get("links", []):
                link.parentID = issue.id
                try:
                    new_link = Link.insert_link(app=app, link=link)
                except Exception as ex:
                    logger.error(ex)
        job_progress.update(task, advance=1)


def extract_links_with_labels(text: str, parent_id: int, parent_module: str) -> list[Link]:
    """Extract links from an issue description text with labels

    :param str text: The issue description containing links
    :param int parent_id: The parent ID associated with the parent module
    :param str parent_module: The parent module associated with the parent ID
    :return: A list of Link objects extracted from the text
    :rtype: list[Link]
    """
    results = []
    url_pattern = re.compile(r"https?://(?:[a-zA-Z0-9$@.&+*(),%-]|%[0-9a-fA-F]{2})+")

    for line in text.split("\n"):
        if ":" in line and ("Link" in line or "link" in line):
            label, url = line.split(":", 1)
            url = url.strip().replace("<br>", "")

            if url.startswith("https:"):
                url = url[6:].strip()

            if url_pattern.match(url):
                results.append(
                    Link(
                        title=label.replace("-", "").strip(),
                        url=url,
                        parentID=parent_id,
                        parentModule=parent_module,
                    )
                )

    return results


def convert_issues(
    gitlab_issues: list,
    regscale_id: int,
    regscale_module: str,
    include_links: bool,
    job_progress: Progress,
) -> list:
    """
    Converts issues from GitLab to regscale

    :param list gitlab_issues: The list of GitLab issues to convert
    :param int regscale_id: The RegScale ID to convert issues to
    :param str regscale_module: The RegScale module to convert issues to
    :param bool include_links: Whether to include links from the issue description
    :param Progress job_progress: The progress object to use for updating
    :return: list of converted issues
    :rtype: list
    """
    app = check_license()

    task = job_progress.add_task("[#f8b737]Converting issues from gitlab...", total=len(gitlab_issues))
    regscale_issues = []
    for issue in gitlab_issues:
        status = "Open"
        if issue.get("state"):
            if issue.get("state") == "open":
                status = "Open"
            elif issue.get("state") == "closed":
                status = "Closed"
        severity_level = Issue.assign_severity(issue.get("weight", 0))
        # Convert the issue to your desired format
        converted_issue = Issue(
            title=issue["title"],
            description=str(markdown.markdown(issue["description"])),
            severityLevel=severity_level,
            issueOwnerId=app.config["userId"],
            costEstimate=0,
            levelOfEffort=0,
            dueDate=issue["due_date"],
            identification="Other",
            dependabotId=str(issue["id"]),
            dateCreated=issue["created_at"],
            parentId=regscale_id,
            parentModule=regscale_module,
            status=status,
            securityPlanId=regscale_id if regscale_module == "securityplans" else None,
            componentId=regscale_id if regscale_module == "components" else None,
        )
        if converted_issue.status == "Closed":
            if issue.get("closed_at"):
                converted_issue.dateCompleted = issue.get("closed_at")
            else:
                converted_issue.dateCompleted = get_current_datetime()
        # Extract the links from the description
        if include_links:
            links = extract_links_with_labels(issue["description"], 0, "issues")
            regscale_issues.append({"issue": converted_issue, "links": links})
        else:
            regscale_issues.append({"issue": converted_issue, "links": []})
        job_progress.update(task, advance=1)
    return regscale_issues


def get_issues_from_gitlab(gitlab_url: str, gitlab_project_id: int, api_token: str, job_progress: Progress) -> list:
    """Fetch issues from GitLab

    :param str gitlab_url: The GitLab URL to fetch issues from
    :param int gitlab_project_id: The GitLab project ID to fetch issues from
    :param str api_token: The GitLab API token to use
    :param Progress job_progress: The progress object to use for updating
    :return: list of issues
    :rtype: list
    """
    # Define the GitLab API URL for issues
    api_call = f"/api/v4/projects/{gitlab_project_id}/issues"
    url = urljoin(gitlab_url, api_call)
    logger.info("Fetching issues from gitlab...")
    logger.debug(f"Fetching with API token {api_token}")
    # Define the headers, including your API token
    headers = {"Private-Token": api_token}
    # Send a GET request to the API
    fetching_issues = job_progress.add_task("[#f8b737]Fetching issues from gitlab...", total=1)
    response = requests.get(url, headers=headers)
    job_progress.update(fetching_issues, advance=1)
    issues = []
    # If the request was successful
    if response.ok:
        # Load the issues from the response
        issues = response.json()
        logger.info(f"Fetched {len(issues)} issues from gitlab")
    else:
        logger.error(response.status_code)
        logger.error(response.text)
        error_and_exit(f"Failed to get issues from GitLab. Status code: {response.status_code}")
    return issues
