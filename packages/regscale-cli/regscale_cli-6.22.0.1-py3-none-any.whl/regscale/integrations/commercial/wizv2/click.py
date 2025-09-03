#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates Wiz.io into RegScale"""

# standard python imports
import logging
from typing import Optional

import click

from regscale.integrations.commercial.wizv2.variables import WizVariables
from regscale.models import regscale_id
from regscale.models.app_models.click import regscale_ssp_id, regscale_module

logger = logging.getLogger("regscale")


@click.group()  # type: ignore
def wiz():
    """Integrates continuous monitoring data from Wiz.io."""


@wiz.command()
@click.option("--client_id", default=None, hide_input=False, required=False)  # type: ignore
@click.option("--client_secret", default=None, hide_input=True, required=False)  # type: ignore
def authenticate(client_id, client_secret):
    """Authenticate to Wiz."""
    from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate

    wiz_authenticate(client_id, client_secret)


@wiz.command()
@click.option(
    "--wiz_project_id",
    "-p",
    required=False,
    type=str,
    help="Comma Seperated list of one or more Wiz project ids to pull inventory for.",
)
@regscale_ssp_id(
    help="RegScale SSP ID to push inventory to in RegScale.",
)
@click.option(
    "--client_id",
    "-ci",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(
    "--client_secret",
    "-cs",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=False,
    required=False,
)
@click.option(
    "--filter_by_override",
    "-f",
    default=None,
    type=str,
    required=False,
    help="""Filter by override to use for pulling inventory you can use one or more of the following.
    IE: --filter_by='{projectId: ["1234"], type: ["VIRTUAL_MACHINE"], subscriptionExternalId: ["1234"],
         providerUniqueId: ["1234"], updatedAt: {after: "2023-06-14T14:07:06Z"}, search: "test-7"}' """,
)
def inventory(
    wiz_project_id: str,
    regscale_ssp_id: int,
    client_id: str,
    client_secret: str,
    filter_by_override: Optional[str] = None,
) -> None:
    """Process inventory from Wiz and create assets in RegScale."""
    from regscale.integrations.commercial.wizv2.scanner import WizVulnerabilityIntegration

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    scanner = WizVulnerabilityIntegration(plan_id=regscale_ssp_id)
    scanner.sync_assets(
        plan_id=regscale_ssp_id,
        filter_by_override=filter_by_override or WizVariables.wizInventoryFilterBy,  # type: ignore
        client_id=client_id,  # type: ignore
        client_secret=client_secret,  # type: ignore
        wiz_project_id=wiz_project_id,
    )


@wiz.command()
@click.option(
    "--wiz_project_id",
    "-p",
    prompt="Enter the project ID for Wiz",
    default=None,
    required=False,
)
@regscale_ssp_id(help="RegScale will create and update issues as children of this record.")
@click.option(
    "--client_id",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(
    "--client_secret",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=True,
    required=False,
)
@click.option(
    "--filter_by_override",
    "-f",
    default=None,
    type=str,
    required=False,
    help="""Filter by override to use for pulling inventory you can use one or more of the following.
    IE: --filter_by='{projectId: ["1234"], type: ["VIRTUAL_MACHINE"], subscriptionExternalId: ["1234"],
         providerUniqueId: ["1234"], updatedAt: {after: "2023-06-14T14:07:06Z"}, search: "test-7"}' """,
)
def issues(
    wiz_project_id: str,
    regscale_ssp_id: int,
    client_id: str,
    client_secret: str,
    filter_by_override: Optional[str] = None,
) -> None:
    """
    Process Issues from Wiz into RegScale
    """
    from regscale.core.app.utils.app_utils import check_license
    from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate
    from regscale.integrations.commercial.wizv2.issue import WizIssue
    import json

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    check_license()
    wiz_authenticate(client_id, client_secret)
    filter_by = json.loads(filter_by_override or WizVariables.wizIssueFilterBy.replace("\n", ""))

    filter_by["project"] = wiz_project_id

    scanner = WizIssue(plan_id=regscale_ssp_id)
    scanner.sync_findings(
        plan_id=regscale_ssp_id,
        filter_by_override=filter_by_override,  # type: ignore
        client_id=client_id,  # type: ignore
        client_secret=client_secret,  # type: ignore
        wiz_project_id=wiz_project_id,
    )


@wiz.command(name="attach_sbom")
@click.option(  # type: ignore
    "--client_id",
    "-ci",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(  # type: ignore
    "--client_secret",
    "-cs",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=True,
    required=False,
)
@regscale_ssp_id(help="RegScale will create and update issues as children of this record.")
@click.option("--report_id", "-r", help="Wiz Report ID", required=True)  # type: ignore
@click.option(  # type: ignore
    "--standard", "-s", help="SBOM standard CycloneDX or SPDX default is CycloneDX", default="CycloneDX", required=False
)
def attach_sbom(
    client_id,
    client_secret,
    regscale_ssp_id: str,
    report_id: str,
    standard="CycloneDX",
):
    """Download SBOMs from a Wiz report by ID and add them to the corresponding RegScale assets."""
    from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate
    from regscale.integrations.commercial.wizv2.utils import fetch_sbom_report

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    wiz_authenticate(
        client_id=client_id,
        client_secret=client_secret,
    )
    fetch_sbom_report(
        report_id,
        parent_id=regscale_ssp_id,
        report_file_name="sbom_report",
        report_file_extension="zip",
        standard=standard,
    )


@wiz.command()
def threats():
    """Process threats from Wiz -> Coming soon"""
    from regscale.core.app.utils.app_utils import check_license

    check_license()
    logger.info("Threats - COMING SOON")


@wiz.command()
@click.option(  # type: ignore
    "--wiz_project_id",
    "-p",
    prompt="Enter the project ID for Wiz",
    default=None,
    required=False,
)
@regscale_ssp_id(help="RegScale will create and update issues as children of this record.")
@click.option(  # type: ignore
    "--client_id",
    "-ci",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(  # type: ignore
    "--client_secret",
    "-cs",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=True,
    required=False,
)
@click.option(  # type: ignore
    "--filter_by_override",
    "-f",
    default=None,
    type=str,
    required=False,
    help="""Filter by override to use for pulling inventory you can use one or more of the following.
    IE: --filter_by='{projectId: ["1234"], type: ["VIRTUAL_MACHINE"], subscriptionExternalId: ["1234"],
         providerUniqueId: ["1234"], updatedAt: {after: "2023-06-14T14:07:06Z"}, search: "test-7"}' """,
)
def vulnerabilities(
    wiz_project_id: str,
    regscale_ssp_id: int,
    client_id: str,
    client_secret: str,
    filter_by_override: Optional[str] = None,
):
    """Process vulnerabilities from Wiz"""
    from regscale.integrations.commercial.wizv2.scanner import WizVulnerabilityIntegration

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    scanner = WizVulnerabilityIntegration(plan_id=regscale_ssp_id)
    scanner.sync_findings(
        plan_id=regscale_ssp_id,
        filter_by_override=filter_by_override,  # type: ignore
        client_id=client_id,  # type: ignore
        client_secret=client_secret,  # type: ignore
        wiz_project_id=wiz_project_id,
    )


@wiz.command(name="add_report_evidence")
@click.option(  # type: ignore
    "--client_id",
    "-ci",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(  # type: ignore
    "--client_secret",
    "-cs",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=True,
    required=False,
)
@click.option("--evidence_id", "-e", help="Wiz Evidence ID", required=True, type=int)  # type: ignore
@click.option("--report_id", "-r", help="Wiz Report ID", required=True)  # type: ignore
@click.option("--report_file_name", "-n", help="Report file name", default="evidence_report", required=False)  # type: ignore
@click.option("--report_file_extension", "-e", help="Report file extension", default="csv", required=False)  # type: ignore
def add_report_evidence(
    client_id,
    client_secret,
    evidence_id: int,
    report_id: str,
    report_file_name: str = "evidence_report",
    report_file_extension: str = "csv",
):
    """Download a Wiz report by ID and Attach to Evidence locker"""
    from regscale.integrations.commercial.wizv2.wiz_auth import wiz_authenticate
    from regscale.integrations.commercial.wizv2.utils import fetch_report_by_id

    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    wiz_authenticate(
        client_id=client_id,
        client_secret=client_secret,
    )
    fetch_report_by_id(
        report_id, parent_id=evidence_id, report_file_name=report_file_name, report_file_extension=report_file_extension
    )


@wiz.command("sync_compliance")
@click.option(  # type: ignore
    "--wiz_project_id",
    "-p",
    prompt="Enter the Wiz project ID",
    help="Enter the Wiz Project ID for policy compliance sync.",
    required=True,
)
@regscale_id(help="RegScale will create and update control assessments as children of this record.")
@regscale_module(required=True, default="securityplans", prompt=False)
@click.option(  # type: ignore
    "--client_id",
    "-i",
    help="Wiz Client ID, or can be set as environment variable wizClientId",
    default="",
    hide_input=False,
    required=False,
)
@click.option(  # type: ignore
    "--client_secret",
    "-s",
    help="Wiz Client Secret, or can be set as environment variable wizClientSecret",
    default="",
    hide_input=True,
    required=False,
)
@click.option(  # type: ignore
    "--framework_id",
    "-f",
    help="Wiz framework ID or shorthand (e.g., 'nist', 'aws', 'wf-id-4'). Use --list-frameworks to see options. Default: wf-id-4 (NIST SP 800-53 Rev 5)",
    default="wf-id-4",
    required=False,
)
@click.option(  # type: ignore
    "--list-frameworks",
    "-lf",
    is_flag=True,
    help="List all available framework options and shortcuts",
    default=False,
)
@click.option(  # type: ignore
    "--create-issues/--no-create-issues",
    "-ci/-ni",
    default=True,
    help="Create issues for failed policy assessments (default: enabled)",
)
@click.option(  # type: ignore
    "--update-control-status/--no-update-control-status",
    "-ucs/-nucs",
    default=True,
    help="Update control implementation status based on assessment results (default: enabled)",
)
@click.option(  # type: ignore
    "--create-poams/--no-create-poams",
    "-cp/-ncp",
    default=False,
    help="Mark created issues as POAMs (default: disabled)",
)
@click.option(  # type: ignore
    "--refresh/--no-refresh",
    "-r/-nr",
    default=False,
    help="Force refresh and ignore cached data (default: use cache if available)",
)
@click.option(  # type: ignore
    "--cache-duration",
    "-cd",
    type=click.INT,
    default=1440,
    help="Cache duration in minutes - reuse cached data if newer than this (default: 1440 minutes / 1 day)",
)
def sync_compliance(
    wiz_project_id,
    regscale_id,
    regscale_module,
    client_id,
    client_secret,
    framework_id,
    list_frameworks,
    create_issues,
    update_control_status,
    create_poams,
    refresh,
    cache_duration,
):
    """
    Sync policy compliance assessments from Wiz to RegScale.

    This command fetches policy assessment data from Wiz and creates:
    - Control assessments based on policy compliance results
    - Issues for failed policy assessments (if --create-issues enabled)
    - Updates to control implementation status (if --update-control-status enabled)
    - JSON output file with policy compliance data in artifacts/wiz/ directory
    - Cached framework mapping for improved performance

    CACHING:
    By default, the command will reuse cached policy data if it's newer than the cache
    duration (default: 60 minutes). Use --refresh to force fresh data from Wiz.
    Use --cache-duration to adjust how long cached data is considered valid.
    """
    from regscale.integrations.commercial.wizv2.policy_compliance import (
        WizPolicyComplianceIntegration,
        list_available_frameworks,
        resolve_framework_id,
    )

    # Handle --list-frameworks flag
    if list_frameworks:
        click.echo(list_available_frameworks())
        return

    # Use environment variables if not provided
    if not client_secret:
        client_secret = WizVariables.wizClientSecret
    if not client_id:
        client_id = WizVariables.wizClientId

    # Resolve framework ID using the enhanced framework resolution
    try:
        resolved_framework_id = resolve_framework_id(framework_id.lower())
        if resolved_framework_id != framework_id:
            from regscale.integrations.commercial.wizv2.policy_compliance import FRAMEWORK_MAPPINGS

            framework_name = FRAMEWORK_MAPPINGS.get(resolved_framework_id, resolved_framework_id)
            click.echo(f"🔍 Resolved '{framework_id}' to '{framework_name}' ({resolved_framework_id})")
    except ValueError as e:
        click.echo(f"❌ {str(e)}")
        click.echo("\nUse --list-frameworks to see all available options.")
        return

    # Create and run the policy compliance integration
    policy_integration = WizPolicyComplianceIntegration(
        plan_id=regscale_id,
        wiz_project_id=wiz_project_id,
        client_id=client_id,
        client_secret=client_secret,
        framework_id=resolved_framework_id,
        regscale_module=regscale_module,
        create_poams=create_poams,
        cache_duration_minutes=cache_duration,
        force_refresh=refresh,
    )

    # Run the policy compliance sync
    policy_integration.sync_policy_compliance(
        create_issues=create_issues,
        update_control_status=update_control_status,
    )
