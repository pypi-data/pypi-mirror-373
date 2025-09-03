#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SQL Server integration for the CLI that allows for executing SQL queries"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.internal.workflow import create_regscale_workflow_from_template
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    create_progress_object,
    get_current_datetime,
)
from regscale.core.app.utils.regscale_utils import (
    verify_provided_module,
)
from regscale.models.app_models.click import regscale_id, regscale_module
from regscale.models.regscale_models import Assessment, File

job_progress = create_progress_object()
logger = create_logger()
# SQL query
sql_query = """
SELECT p.name AS [LoginName], r.name AS [RoleName]
FROM sys.server_principals r
JOIN sys.server_role_members m ON r.principal_id = m.role_principal_id
JOIN sys.server_principals p ON p.principal_id = m.member_principal_id
WHERE r.type = 'R' AND r.name
IN (N'sysadmin', N'db_owner', N'securityadmin')
and p.is_disabled = 0
ORDER BY p.name;
"""


@click.group()
def sqlserver():
    """sqlserver integration to pull admin users \
        report via trusted connection."""


@sqlserver.command("admins_report")
@click.option(
    "--workflow_template_id",
    "-w",
    type=click.INT,
    help="Regscale workflow template ID",
    required=True,
    prompt=True,
)
@click.option(
    "--output_dir",
    "-o",
    help="Output directory to save the report. Defaults to sqlserver_reports",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
    default=Path("sqlserver_reports"),
    prompt=False,
)
@click.option(
    "--query_file",
    "-q",
    help="Path to a SQL query file.",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option(
    "--server",
    "-s",
    required=True,
    default=os.getenv("sqlServer"),
    help="SQL Server host.",
)
@click.option(
    "--database",
    "-d",
    required=True,
    default=os.getenv("sqlServerDbName"),
    help="Database name.",
)
@click.option(
    "--port",
    "-p",
    required=True,
    default=os.getenv("sqlServerPort"),
    help="Database Port number.",
)
@click.option("--username", "-u", default=os.getenv("sqlServerUser"), help="Username.")
@click.option("--password", "-pwd", default=os.getenv("sqlServerPassword"), help="Password.")
@regscale_id()
@regscale_module()
@click.option(
    "--output_file",
    "-f",
    help=f"Desired output file name. Defaults to RegScale_CLI_SQL_Report_{datetime.now().strftime('%Y%m%d')}",
    type=click.STRING,
    default=f"RegScale_CLI_SQL_Report_{datetime.now().strftime('%Y%m%d')}",
    prompt=False,
)
def generate_report(
    workflow_template_id: int,
    output_dir: str,
    output_file: str,
    server: str,
    database: str,
    port: int,
    username: str,
    password: str,
    regscale_id: int,
    regscale_module: str,
    query_file: Path,
) -> None:
    """Execute SQL query and save the data as a .csv report."""
    generate_and_save_report(
        workflow_template_id,
        output_dir,
        query_file,
        server,
        database,
        port,
        username,
        password,
        regscale_id,
        regscale_module,
        output_file,
    )


def generate_and_save_report(
    workflow_template_id: int,
    output_dir: str,
    query_file: Path,
    server: str,
    database: str,
    port: int,
    username: str,
    password: str,
    regscale_id: int,
    regscale_module: str,
    output_file: str = f"RegScale_CLI_SQL_Report_{datetime.now().strftime('%Y%m%d')}",
) -> None:
    """
    :param int workflow_template_id: RegScale workflow template ID
    :param str output_dir: Output directory
    :param Path query_file: SQL query file
    :param str server: SQL Server name
    :param str database: Database name
    :param int port: Port number
    :param str username: Username
    :param str password: Password
    :param int regscale_id: RegScale module Id
    :param str regscale_module: RegScale module name
    :param str output_file: Output file name, defaults to RegScale_CLI_SQL_Report_{datetime.now().strftime('%Y%m%d')}
    :rtype: None
    """
    import pandas as pd  # Optimize import performance

    app = check_license()

    # see if provided RegScale Module is an accepted option
    verify_provided_module(regscale_module)

    # Build the connection string
    conn_str = build_connection_string(server, database, port, username, password)
    import pyodbc

    with pyodbc.connect(conn_str) as cnxn:
        cursor = cnxn.cursor()
        if query_file:
            sql_query = _get_query_from_file(query_file)
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        # Create a DataFrame from the rows
        df = pd.DataFrame.from_records(rows, columns=[column[0] for column in cursor.description])

    if not df.empty:
        # Convert the DataFrame to an HTML table
        report = df.to_html(index=False)

        # Save the DataFrame to a CSV file
        new_file = f"{output_file}.csv"
        # Specify the directory where you want to save the CSV file

        # Create the directory if it does not exist
        check_file_path(output_dir)

        full_path = output_dir / new_file
        # Save the DataFrame to a CSV file in the specified directory
        df.to_csv(full_path, index=False)
        title = f"Sql Server Report assessment {regscale_module.title()}-{regscale_id}"
        description = f"Sql Server Report assessment {regscale_module.title()}-{regscale_id}"
        new_assessment_id = create_and_save_assessment(
            report,
            [full_path],
            regscale_id,
            regscale_module,
            title=title,
            description=description,
            app=app,
        )
        logger.debug(f"New assessment created here is the id: {new_assessment_id}")
        if new_assessment_id and workflow_template_id:
            create_regscale_workflow_from_template(
                new_assessment_id,
                template_id=workflow_template_id,
            )
    else:
        logger.info(f"No data found for query: {sql_query}.")


def _get_query_from_file(file_path: str) -> str:
    """
    Get the SQL query from a file.
    :param str file_path: Path to SQL query file
    :return: SQL query
    :rtype: str
    """
    with open(file_path, "r") as file:
        query = file.read()
    return query


def build_connection_string(
    server: str,
    database: str,
    port: int,
    username: Optional[str],
    password: Optional[str],
) -> str:
    """
    Build the connection string for the SQL Server.
    :param str server: SQL Server name
    :param str database: Database name
    :param int port: Port number for the SQL Server
    :param Optional[str] username: Database Username optional
    :param Optional[str] password: Database Password optional
    :return: Connection string
    :rtype: str
    """
    if username and password:
        conn_str = (
            r"DRIVER={ODBC Driver 17 for SQL Server};"
            r"SERVER=" + server + ";"
            r"DATABASE=" + database + ";"
            r"PORT=" + str(port) + ";"
            r"UID=" + username + ";"
            r"PWD=" + password + ";"
            r"TrustServerCertificate=yes;"
            r"TIMEOUT=30;"
            # Set the login timeout to 30 seconds
        )
    else:
        conn_str = (
            r"DRIVER={ODBC Driver 17 for SQL Server};"
            r"SERVER=" + server + ";"
            r"DATABASE=" + database + ";"
            r"PORT=" + str(port) + ";"
            r"Trusted_Connection=yes;"
        )
    return conn_str


def calculate_finish_date(current_date: datetime, days: int) -> str:
    """
    Calculate finish date for Assessment by adding days to current date
    :param datetime current_date: Date to start with
    :param int days: # of days to add to current date
    :return: String representation of finish date
    :rtype: str
    """
    return (current_date + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")


def create_assessment_object(
    app: Application,
    report: str,
    regscale_id: int,
    regscale_module: str,
    title: str,
    description: str,
) -> Assessment:
    """
    Create a RegScale assessment object
    :param Application app: Application object
    :param str report: Assessment report
    :param int regscale_id: RegScale ID
    :param str regscale_module: RegScale module
    :param str title: Assessment title
    :param str description: Assessment description
    :return: Assessment object
    :rtype: Assessment
    """
    finish_date = calculate_finish_date(datetime.now(), app.config["assessmentDays"])
    status = "Scheduled"
    new_assessment = Assessment(
        leadAssessorId=app.config["userId"],
        title=title,
        assessmentType="Control Testing",
        plannedStart=get_current_datetime(),
        plannedFinish=finish_date,
        assessmentReport=report,
        assessmentPlan=description,
        createdById=app.config["userId"],
        dateCreated=get_current_datetime(),
        lastUpdatedById=app.config["userId"],
        dateLastUpdated=get_current_datetime(),
        parentModule=regscale_module,
        parentId=regscale_id,
        status=status,
    )

    new_assessment.actualFinish = "true"
    new_assessment.assessmentResult = "Pass"
    return new_assessment


def upload_files_to_assessment(api: Api, assessment_id: int, files: list) -> None:
    """
    Upload files to the new RegScale Assessment
    :param Api api: Api object
    :param int assessment_id: RegScale assessment id
    :param list files: List of files to upload to RegScale assessment
    :rtype: None
    """
    upload_files = job_progress.add_task("[#0866b4]Uploading files to the new RegScale Assessment...", total=len(files))
    for new_file in files:
        new_file_upload = File.upload_file_to_regscale(
            file_name=new_file,
            parent_id=assessment_id,
            parent_module="assessments",
            api=api,
        )
        if new_file_upload:
            job_progress.update(upload_files, advance=1)


def create_and_save_assessment(
    report: str,
    files: list,
    regscale_id: int,
    regscale_module: str,
    title: str,
    description: str,
    app: Application,
) -> int:
    """
    Create a new RegScale Assessment and upload the report and files to it
    :param str report: Report to upload to assessment
    :param list files: List of files to upload to assessment
    :param int regscale_id: RegScale id
    :param str regscale_module: RegScale module
    :param str title: Assessment title
    :param str description: Assessment description
    :param Application app: Application object
    :return:RegScale assessment id
    :rtype: int
    """
    api = Api()
    new_assessment = create_assessment_object(app, report, regscale_id, regscale_module, title, description)
    create_assessment = job_progress.add_task("[#21a5bb]Creating assessment in RegScale...", total=1)
    if new_assessment_id := new_assessment.insert_assessment(app=app).id:
        logger.info(f"created new RegScale Assessment with id of {new_assessment_id}")
        job_progress.update(create_assessment, advance=1)
        upload_files_to_assessment(api, new_assessment_id, files)
    return new_assessment_id
