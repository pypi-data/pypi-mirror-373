"""
Internal commands for the RegScale CLI
"""

import click
from regscale.core.lazy_group import LazyGroup


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "send_reminders": "regscale.core.app.internal.admin_actions.send_reminders",
        "update_compliance_history": "regscale.core.app.internal.admin_actions.update_compliance_history",
        "user_report": "regscale.core.app.internal.admin_actions.user_report",
    },
    name="admin_actions",
)
def admin_actions():
    """Performs administrative actions on the RegScale platform."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "delete_files": "regscale.core.app.internal.assessments_editor.delete_files",
        "generate": "regscale.core.app.internal.assessments_editor.generate",
        "generate_new_file": "regscale.core.app.internal.assessments_editor.generate_new_file",
        "load": "regscale.core.app.internal.assessments_editor.load",
    },
    name="assessments",
)
def assessments():
    """Performs actions on Assessments CLI Feature to create new or update assessments to RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "sync_security_plans": "regscale.core.app.internal.catalog.sync_security_plans",
        "import": "regscale.core.app.internal.catalog.import_",
        "download": "regscale.core.app.internal.catalog.export",
        "diagnose": "regscale.core.app.internal.catalog.diagnostic",
        "compare": "regscale.core.app.internal.catalog.compare",
        "update": "regscale.core.app.internal.catalog.update",
        "check_for_updates": "regscale.core.app.internal.catalog.check_for_updates",
        "update_via_platform": "regscale.core.app.internal.catalog.update_via_platform",
    },
    name="catalog",
)
def catalog():
    """Export, diagnose, and compare catalog from RegScale.com/regulations."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "compare_files": "regscale.core.app.internal.comparison.compare_files_cli",
    },
    name="compare",
)
def compare():
    """Create RegScale Assessment of differences after comparing two files."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "generate": "regscale.core.app.internal.control_editor.generate_data_download",
        "load": "regscale.core.app.internal.control_editor.generate_db_update",
        "delete_files": "regscale.core.app.internal.control_editor.generate_delete_file",
    },
    name="control_editor",
)
def control_editor():
    """Performs actions on Control Editor Feature to edit controls to RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "start": "regscale.core.app.internal.evidence.start",
        "build_package": "regscale.core.app.internal.evidence.build_package",
    },
    name="evidence",
)
def evidence():
    """Welcome to the RegScale Evidence Collection Automation CLI!"""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "inheritance_converter": "regscale.core.app.internal.migrations.inheritance_converter",
        "issue_linker": "regscale.core.app.internal.migrations.issue_linker",
        "assessment_linker": "regscale.core.app.internal.migrations.assessment_linker",
        "risk_linker": "regscale.core.app.internal.migrations.risk_linker",
    },
    name="import",
)
def migrations():
    """Performs data processing for legacy data to migrate data formats or perform bulk processing."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "new": "regscale.core.app.internal.model_editor.generate_new_file",
        "generate": "regscale.core.app.internal.model_editor.generate",
        "load": "regscale.core.app.internal.model_editor.load",
        "delete_files": "regscale.core.app.internal.model_editor.generate_delete_file",
    },
)
def model():
    """Performs actions on CLI models Feature to update issues to RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "generate": "regscale.core.app.internal.poam_editor.generate_all_issues",
        "load": "regscale.core.app.internal.poam_editor.generate_upload_data",
        "delete_files": "regscale.core.app.internal.poam_editor.generate_delete_file",
    },
    name="issues",
)
def issues():
    """Performs actions on Issues CLI Feature to create new or update issues to RegScale."""
    pass


@click.group(
    cls=LazyGroup,
    lazy_subcommands={
        "new": "regscale.core.app.internal.set_permissions.generate_new_file",
        "load": "regscale.core.app.internal.set_permissions.import_permissions",
    },
    name="set_permissions",
)
def set_permissions():
    """Builk sets permissions on records in RegScale from a generated spreadsheet"""
    pass
