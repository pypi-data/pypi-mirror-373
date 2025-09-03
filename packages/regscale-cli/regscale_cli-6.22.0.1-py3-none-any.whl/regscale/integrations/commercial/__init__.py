"""
Commercial commands for the RegScale CLI
"""

import click

from regscale.core.lazy_group import LazyGroup
from regscale.models.app_models.click import show_mapping


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "authenticate": "regscale.integrations.commercial.ad.authenticate",
        "list_groups": "regscale.integrations.commercial.ad.list_groups",
        "sync_admins": "regscale.integrations.commercial.ad.sync_admins",
        "sync_general": "regscale.integrations.commercial.ad.sync_general",
        "sync_readonly": "regscale.integrations.commercial.ad.sync_readonly",
    },
    name="ad",
)
def ad():
    """Performs directory and user synchronization functions with Azure Active Directory."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_aqua": "regscale.integrations.commercial.aqua.aqua.import_aqua",
    },
    name="aqua",
)
def aqua():
    """Performs actions on Aqua Scanner artifacts."""
    pass


show_mapping(aqua, "aqua")


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync_assets": "regscale.integrations.commercial.aws.cli.sync_assets",
        "sync_findings_and_assets": "regscale.integrations.commercial.aws.cli.sync_findings_and_assets",
        "inspector": "regscale.integrations.commercial.aws.cli.inspector",
    },
    name="aws",
)
def aws():
    """AWS Integrations"""
    pass


show_mapping(aws, "aws_inspector")


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync_assets": "regscale.integrations.commercial.axonius.axonius_integration.sync_assets",
        "sync_findings": "regscale.integrations.commercial.axonius.axonius_integration.sync_findings",
    },
    name="axonius",
)
def axonius():
    """Axonius Integration"""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync_intune": "regscale.integrations.commercial.azure.intune.sync_intune",
    },
    name="azure",
)
def azure():
    """Azure Integrations"""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_burp": "regscale.integrations.commercial.burp.import_burp",
    },
    name="burp",
)
def burp():
    """Azure Integrations"""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "query_incidents": "regscale.integrations.commercial.crowdstrike.query_incidents",
        "sync_incidents": "regscale.integrations.commercial.crowdstrike.sync_incidents",
        "sync_compliance": "regscale.integrations.commercial.crowdstrike.run_compliance_sync",
    },
    name="crowdstrike",
)
def crowdstrike():
    """[BETA] CrowdStrike Integration to load threat intelligence to RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "authenticate": "regscale.integrations.commercial.microsoft_defender.defender.authenticate_in_defender",
        "sync_365_alerts": "regscale.integrations.commercial.microsoft_defender.defender.sync_365_alerts",
        "sync_365_recommendations": "regscale.integrations.commercial.microsoft_defender.defender.sync_365_recommendations",
        "sync_cloud_resources": "regscale.integrations.commercial.microsoft_defender.defender.sync_cloud_resources",
        "export_resources": "regscale.integrations.commercial.microsoft_defender.defender.export_resources_to_csv",
        "sync_cloud_alerts": "regscale.integrations.commercial.microsoft_defender.defender.sync_cloud_alerts",
        "sync_cloud_recommendations": "regscale.integrations.commercial.microsoft_defender.defender.sync_cloud_recommendations",
        "import_alerts": "regscale.integrations.commercial.microsoft_defender.defender.import_alerts",
    },
    name="defender",
)
def defender():
    """Sync assets, recommendations, and alerts from Microsoft Defender 365 and Microsoft Defender for
    Cloud into RegScale."""
    pass


show_mapping(group=defender, import_name="defender", file_type="csv")


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync_alerts": "regscale.integrations.commercial.dependabot.create_alerts",
    },
    name="dependabot",
)
def dependabot():
    """Create an assessment and child issues in RegScale from Dependabot alerts."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "scan": "regscale.integrations.commercial.durosuite.scanner.scan",
        "import_audit": "regscale.integrations.commercial.durosuite.scanner.cli_import_audit",
    },
    name="durosuite",
)
def durosuite():
    """Sync DuroSuite scan results and audits into RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_ecr": "regscale.integrations.commercial.ecr.import_ecr",
    },
    name="ecr",
)
def ecr():
    """Performs actions on ECR Scanner artifacts."""
    pass


show_mapping(ecr, "ecr")


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_file": "regscale.integrations.commercial.opentext.commands.import_scans",
    },
    name="opentext",
)
def fortify():
    """Performs actions on opentext export files."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync_findings": "regscale.integrations.commercial.gcp.sync_findings",
        "sync_assets": "regscale.integrations.commercial.gcp.sync_assets",
    },
    name="gcp",
)
def gcp():
    """Sync assets and findings from GCP into RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync_issues": "regscale.integrations.commercial.gitlab.sync_issues",
    },
    name="gitlab",
)
def gitlab():
    """GitLab integration to pull issues via API."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_appscan": "regscale.integrations.commercial.ibm.import_appscan",
    },
    name="ibm",
)
def ibm():
    """Performs actions on IBM AppScan files."""
    pass


show_mapping(ibm, "ibm_appscan", "csv")


@click.group(
    cls=LazyGroup,
    name="import_all",
    lazy_subcommands={
        "run": "regscale.integrations.commercial.import_all.import_all_cmd.import_all",
    },
)
def import_all():
    """Import scans, vulnerabilities and assets to RegScale from scan export files."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "issues": "regscale.integrations.commercial.jira.issues",
        "tasks": "regscale.integrations.commercial.jira.tasks",
    },
    name="jira",
)
def jira():
    """Sync issues and attachments or tasks between Jira and RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_nexpose": "regscale.integrations.commercial.nexpose.import_nexpose",
    },
    name="nexpose",
)
def nexpose():
    """Performs actions on ECR Scanner artifacts."""
    pass


show_mapping(nexpose, "nexpose", "csv")


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "authenticate": "regscale.integrations.commercial.okta.authenticate",
        "get_active_users": "regscale.integrations.commercial.okta.get_active_users",
        "get_inactive_users": "regscale.integrations.commercial.okta.get_inactive_users",
        "get_all_users": "regscale.integrations.commercial.okta.get_all_users",
        "get_new_users": "regscale.integrations.commercial.okta.get_recent_users",
        "get_admin_users": "regscale.integrations.commercial.okta.get_admin_users",
    },
    name="okta",
)
def okta():
    """Okta integration to pull Okta users via API."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_prisma": "regscale.integrations.commercial.prisma.import_prisma",
    },
    name="prisma",
)
def prisma():
    """Performs actions on Prisma export files."""
    pass


show_mapping(prisma, "prisma", "csv")


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "export_scans": "regscale.integrations.commercial.qualys.export_past_scans",
        "import_scans": "regscale.integrations.commercial.qualys.import_scans",
        "import_container_scans": "regscale.integrations.commercial.qualys.__init__.import_container_scans",
        "import_was_scans": "regscale.integrations.commercial.qualys.__init__.import_was_scans",
        "import_policy_scans": "regscale.integrations.commercial.qualys.__init__.import_policy_scans",
        "save_results": "regscale.integrations.commercial.qualys.__init__.save_results",
        "sync_qualys": "regscale.integrations.commercial.qualys.__init__.sync_qualys",
        "get_asset_groups": "regscale.integrations.commercial.qualys.__init__.get_asset_groups",
        "import_total_cloud_xml": "regscale.integrations.commercial.qualys.__init__.import_total_cloud_from_xml",
        "import_total_cloud": "regscale.integrations.commercial.qualys.__init__.import_total_cloud",
        "validate_csv": "regscale.integrations.commercial.qualys.__init__.validate_csv",
    },
    name="qualys",
)
def qualys():
    """Performs actions from the Qualys API"""
    pass


show_mapping(group=qualys, import_name="qualys", file_type="csv")


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_scans": "regscale.integrations.commercial.trivy.import_scans",
    },
    name="trivy",
)
def trivy():
    """Performs actions on Trivy export files."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_scans": "regscale.integrations.commercial.grype.commands.import_scans",
    },
    name="grype",
)
def grype():
    """Performs actions on Trivy export files."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync": "regscale.integrations.commercial.salesforce.sync",
    },
    name="salesforce",
)
def salesforce():
    """Sync data and attachments between Salesforce Cases & RegScale Issues"""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "issues": "regscale.integrations.commercial.servicenow.issues",
        "issues_and_attachments": "regscale.integrations.commercial.servicenow.issues_and_attachments",
        "sync_work_notes": "regscale.integrations.commercial.servicenow.sync_work_notes",
        "sync_changes": "regscale.integrations.commercial.servicenow.sync_changes",
    },
    name="servicenow",
)
def servicenow():
    """Sync incidents and attachments, issues, and work notes between ServiceNow and RegScale issues."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync_assets": "regscale.integrations.commercial.sicura.commands.sync_assets",
        "sync_findings": "regscale.integrations.commercial.sicura.commands.sync_findings",
    },
    name="sicura",
)
def sicura():
    """Sync assets and findings from Sicura into RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_snyk": "regscale.integrations.commercial.snyk.import_snyk",
    },
    name="snyk",
)
def snyk():
    """Performs actions on Snyk export files."""
    pass


show_mapping(snyk, "snyk", "xlsx")


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync_alerts": "regscale.integrations.commercial.sonarcloud.create_alerts",
    },
    name="sonarcloud",
)
def sonarcloud():
    """Sync assets, findings, and assessments from STIG .ckl files into RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "run": "regscale.integrations.commercial.stig_mapper_integration.click_commands.run",
    },
    name="stig_mapper",
)
def stig_mapper():
    """Map data from STIGs to RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync_findings": "regscale.integrations.commercial.stigv2.click_commands.sync_findings",
        "sync_assets": "regscale.integrations.commercial.stigv2.click_commands.sync_assets",
        "process_checklist": "regscale.integrations.commercial.stigv2.click_commands.process_checklist",
        "cci_assessment": "regscale.integrations.commercial.stigv2.click_commands.cci_assessment",
    },
    name="stig",
)
def stig():
    """Sync assets, findings, and assessments from STIG .ckl files into RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "io": "regscale.integrations.commercial.tenablev2.commands.io",
        "sc": "regscale.integrations.commercial.tenablev2.commands.sc",
        "nessus": "regscale.integrations.commercial.tenablev2.commands.nessus",
        "sync_jsonl": "regscale.integrations.commercial.tenablev2.commands.sync_jsonl",
        "sync_vulns": "regscale.integrations.commercial.tenablev2.commands.sync_vulns",
    },
    name="tenable",
)
def tenable():
    """Performs actions on the Tenable APIs."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_veracode": "regscale.integrations.commercial.veracode.import_veracode",
    },
    name="veracode",
)
def veracode():
    """Performs actions on Veracode export files."""
    pass


show_mapping(veracode, "veracode")


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "authenticate": "regscale.integrations.commercial.wizv2.click.authenticate",
        "inventory": "regscale.integrations.commercial.wizv2.click.inventory",
        "issues": "regscale.integrations.commercial.wizv2.click.issues",
        "attach_sbom": "regscale.integrations.commercial.wizv2.click.attach_sbom",
        "threats": "regscale.integrations.commercial.wizv2.click.threats",
        "vulnerabilities": "regscale.integrations.commercial.wizv2.click.vulnerabilities",
        "add_report_evidence": "regscale.integrations.commercial.wizv2.click.add_report_evidence",
        "sync_compliance": "regscale.integrations.commercial.wizv2.click.sync_compliance",
    },
    name="wiz",
)
def wiz():
    """Integrates continuous monitoring data from Wiz.io."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "import_xray": "regscale.integrations.commercial.xray.import_xray",
    },
    name="xray",
)
def xray():
    """Performs actions on Prisma export files."""
    pass


show_mapping(xray, "xray", "json")
