#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RegScale File Comparison"""

# standard python imports
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import pandas as pd  # Type Checking
from datetime import datetime, timedelta
from os.path import exists
from pathlib import Path
from typing import Any, Tuple
from rich.progress import TaskID

import click

from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import (
    check_license,
    create_progress_object,
    error_and_exit,
    get_current_datetime,
    get_file_name,
    get_file_type,
    get_recent_files,
)
from regscale.core.app.utils.regscale_utils import verify_provided_module
from regscale.models.app_models.click import NotRequiredIf, regscale_id, regscale_module
from regscale.models.regscale_models import Assessment, File

job_progress = create_progress_object()
XLSX = ".xlsx"
CSV = ".csv"
XLS = ".xls"
SUPPORTED_FILE_TYPES = [CSV, XLSX, XLS]


@click.group()
def compare():
    """Create RegScale Assessment of differences after comparing two files."""


@compare.command(name="compare_files")
@click.option(
    "--most_recent_in_file_path",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
    help="Grab two most recent files in the provided directory for comparison.",
    default=None,
    cls=NotRequiredIf,
    not_required_if=["old_file", "new_file"],
)
@click.option(
    "--most_recent_file_type",
    type=click.Choice([".csv", XLSX], case_sensitive=False),
    help="Filter the directory for .csv or .xlsx file types.",
    default=None,
    cls=NotRequiredIf,
    not_required_if=["old_file", "new_file"],
)
@click.option(
    "--old_file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
    help=(
        "Enter file path of the original file to compare: must be used with --new_file, "
        + "not required if --most_recent_in_file_path & --most_recent_file_type is used."
    ),
    cls=NotRequiredIf,
    not_required_if=["most_recent_in_file_path", "most_recent_file_type"],
)
@click.option(
    "--new_file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
    help=(
        "Enter file path of new file to compare: must be used with --old_file, "
        + "not required if --most_recent_in_file_path & --most_recent_file_type is used."
    ),
    cls=NotRequiredIf,
    not_required_if=["most_recent_in_file_path", "most_recent_file_type"],
)
@click.option(
    "--key",
    type=click.STRING,
    help="Enter unique key to compare the files.",
    prompt="Enter the key/column to compare files",
    required=True,
)
@regscale_id()
@regscale_module()
def compare_files_cli(
    old_file: str,
    new_file: str,
    most_recent_in_file_path: Path,
    most_recent_file_type: str,
    key: str,
    regscale_id: int,
    regscale_module: str,
):
    """Compare the two given files while using the provided key for any differences.
    Supports csv, xls and xlsx files."""
    compare_files(
        old_file=old_file,
        new_file=new_file,
        most_recent_in_file_path=most_recent_in_file_path,
        most_recent_file_type=most_recent_file_type,
        key=key,
        parent_id=regscale_id,
        parent_module=regscale_module,
    )


def compare_files(
    key: str,
    parent_id: int,
    parent_module: str,
    old_file: Optional[str] = None,
    new_file: Optional[str] = None,
    most_recent_in_file_path: Optional[Path] = None,
    most_recent_file_type: Optional[str] = None,
) -> None:
    """Compare the two given files while using the provided key for any differences

    :param str key: Unique key to compare the files
    :param int parent_id: ID of the RegScale Module
    :param str parent_module: Name of the RegScale Module
    :param str old_file: File path of the original file to compare
    :param str new_file: File path of new file to compare
    :param Path most_recent_in_file_path: Path to the directory to find the two most recent files
    :param str most_recent_file_type: File type to filter the directory for
    :rtype: None
    """
    app = check_license()
    api = Api()

    # see if provided RegScale Module is an accepted option
    verify_provided_module(parent_module)

    # see if most_recent_in argument was used, get the old and new file
    if most_recent_in_file_path:
        # get the two most_recent_file_type in the provided most_recent_in_file_path
        recent_files = get_recent_files(
            file_path=most_recent_in_file_path,
            file_count=2,
            file_type=most_recent_file_type,
        )
        # verify we have two files to compare
        if len(recent_files) == 2:
            # set the old_file and new_file accordingly
            old_file = recent_files[1]
            new_file = recent_files[0]
        else:
            # notify user we don't have two files to compare and exit application
            error_and_exit(
                f"Required 2 files to compare, but only 1 {most_recent_file_type}"
                f"file found in {most_recent_in_file_path}!"
            )
    # make sure both file paths exist
    if not exists(old_file) and not exists(new_file):
        error_and_exit("Please check the file paths of the provided files and try again.")
    with job_progress:
        # check the file extensions and compare them
        old_file_type, new_file_type = get_file_type(old_file), get_file_type(new_file)
        file_type = None
        for supported_file_type in SUPPORTED_FILE_TYPES:
            if old_file_type == new_file_type:
                file_type = supported_file_type
        if not file_type:
            error_and_exit(
                f"{old_file_type or new_file_type} files are not a supported file type provided for comparison."
            )
        # get the file names of from the provided file paths
        old_file_name, new_file_name = get_file_name(old_file), get_file_name(new_file)

        # create task for progress bar
        comparing = job_progress.add_task(f"[#f8b737]Comparing {file_type} files for differences...", total=1)
        output, old_row_count, new_row_count = comparison(old_file, new_file, key, file_type)

        # mark the comparing task as complete
        job_progress.update(comparing, advance=1)

        # create task for formatting data
        formatting = job_progress.add_task(
            "[#ef5d23]Formatting data of comparison outcome...",
            total=1,
        )

        # drop any rows that has no value for the provided key
        output = output.dropna(subset=[key])

        # check if there were any changes, if no changes the assessment
        # will be created with complete as the status
        if output.empty:
            status = "Complete"
            actual_finish = get_current_datetime()
            report = f"<h3>No differences between {old_file_name} & {new_file_name}</h3>"
        else:
            status = "Scheduled"
            actual_finish = False
            # format report string for assessment
            report = (
                f"<h3>{old_file_name} Deleted Rows</h3>"
                f"{create_filtered_html_table(output, 'flag', 'deleted')}"
                f"<h3>{new_file_name} Added Rows</h3>"
                f"{create_filtered_html_table(output, 'flag', 'added')}"
            )

        # get data overview
        overview = create_overview(
            data=output,
            old_row_count=old_row_count,
            new_row_count=new_row_count,
            old_file=old_file_name,
            new_file=new_file_name,
        )

        # set up descript for assessment
        desc = (
            f"Comparing two {file_type} files using {key} as a key.<br>"
            f"<b>{old_file_name}</b> contains <b>{old_row_count}</b> row(s) and<br>"
            f"<b>{new_file_name}</b> contains <b>{new_row_count}</b> row(s)<br>{overview}"
        )

        # create new task for creating assessment in RegScale
        create_assessment_task = job_progress.add_task(
            "[#21a5bb]Creating assessment in RegScale...",
            total=1,
        )

        if created_assessment := create_assessment(
            config=app.config,
            file_type=file_type,
            desc=desc,
            parent_id=parent_id,
            parent_module=parent_module,
            report=report,
            status=status,
            formatting=formatting,
            actual_finish=actual_finish,
        ):
            # mark the create_assessment task as complete
            job_progress.update(create_assessment_task, advance=1)

            # create new task for file uploads
            upload_files = job_progress.add_task(
                "[#0866b4]Uploading files to the new RegScale Assessment...",
                total=2,
            )
            upload_files_to_assessment(
                api=api,
                assessment_id=created_assessment.id,
                file_paths=[old_file, new_file],
                upload_files_task=upload_files,
            )

            # notify user assessment was created and output a link to it
            app.logger.info(
                "New assessment has been created and marked as %s: %s/form/assessments/%s",
                status,
                app.config["domain"].rstrip("/"),
                created_assessment.id,
            )
        else:
            # notify the user we were unable to create the assessment int RegScale
            error_and_exit("Unable to create new RegScale Assessment!")


def upload_files_to_assessment(api: Api, assessment_id: int, file_paths: list[str], upload_files_task: TaskID):
    """
    Function to upload files to a RegScale Assessment

    :param Api api: RegScale API object
    :param int assessment_id: ID of the RegScale Assessment
    :param list[str] file_paths: List of file paths to upload
    :param TaskID upload_files_task: TaskID for progress bar
    :rtype: None
    """
    upload_count = 0
    for file in file_paths:
        if File.upload_file_to_regscale(
            file_name=file,
            parent_id=assessment_id,
            parent_module="assessments",
            api=api,
        ):
            upload_count += 1
        job_progress.update(upload_files_task, advance=1)
    if upload_count == 2:
        api.logger.info("Files uploaded to the new assessment in RegScale successfully.")
    else:
        api.logger.error("Unable to upload both files to the assessment in RegScale.")


def create_assessment(
    config: dict,
    file_type: str,
    desc: str,
    parent_id: int,
    parent_module: str,
    report: str,
    status: str,
    formatting: TaskID,
    actual_finish: Optional[str] = None,
) -> Assessment:
    """
    Function to create a new Assessment in RegScale

    :param dict config: Config file for the application
    :param str file_type: Type of file being compared
    :param str desc: Description of the comparison
    :param int parent_id: ID of the parent object
    :param str parent_module: Module of the parent object
    :param str report: Report of the comparison
    :param str status: Status of the comparison
    :param TaskID formatting: TaskID for formatting task
    :param Optional[str] actual_finish: Actual finish date of the assessment
    :return: New Assessment object created in RegScale
    :rtype: Assessment
    """

    # set up title for the new Assessment
    title = f"{file_type} Comparison for {parent_module.title()}-{parent_id}"

    # set up plannedFinish date with days from config file
    finish_date = (datetime.now() + timedelta(days=config["assessmentDays"])).strftime("%Y-%m-%dT%H:%M:%S")

    # map to assessment dataclass
    new_assessment = Assessment(
        title=title,
        assessmentType="Control Testing",
        plannedStart=get_current_datetime(),
        plannedFinish=finish_date,
        assessmentReport=report,
        assessmentPlan=desc,
        dateCreated=get_current_datetime(),
        dateLastUpdated=get_current_datetime(),
        parentModule=parent_module,
        parentId=parent_id,
        status=status,
    )
    # update the appropriate fields to complete the assessment
    if actual_finish:
        new_assessment.actualFinish = actual_finish
        new_assessment.assessmentResult = "Pass"

    # mark the formatting task as complete
    job_progress.update(formatting, advance=1)

    return new_assessment.create()


def comparison(file_one: str, file_two: str, key: str, file_type: str) -> Tuple["pd.DataFrame", int, int]:
    """
    Function that will compare two files using the provided key, uses
    a comparison method depending on the provided file_type and will
    return the differences between the two files in a pandas dataframe

    :param str file_one: Old file to compare
    :param str file_two: New file to compare
    :param str key: key field to compare the files on
    :param str file_type: file type of the two files
    :return: Tuple[difference between two files as panda's dataframe, # of rows in file_one, # of rows in file_two]
    :rtype: Tuple[pd.DataFrame, int, int]
    """
    import pandas as pd  # Optimize import performance

    if file_type.lower() not in [".csv", XLSX, ".xls"]:
        error_and_exit("Unsupported file type provided for comparison.")

    df1, df2 = [], []
    if file_type.lower() == ".csv":
        # open the files
        df1 = pd.read_csv(file_one)
        df2 = pd.read_csv(file_two)
    elif file_type.lower() in [XLSX, ".xls"]:
        # open the files
        df1 = pd.read_excel(file_one)
        df2 = pd.read_excel(file_two)
    # add flags to each dataset
    df1["flag"] = "deleted"
    df2["flag"] = "added"

    # combine the two datasets
    df = pd.concat([df1, df2])

    # get the differences between the two datasets
    output = df.drop_duplicates(df.columns.difference(["flag", key]), keep=False)

    # return the differences and the row counts for each file
    return output, len(df1), len(df2)


def create_overview(
    data: "pd.DataFrame",
    old_row_count: int,
    new_row_count: int,
    old_file: str,
    new_file: str,
) -> str:
    """
    Function to create html formatted description from comparing
    data from provided pandas dataframe and row counts

    :param pd.DataFrame data: Pandas dataframe of data to format and filter
    :param int old_row_count: Number of rows in the old file
    :param int new_row_count: Number of rows in the new file
    :param str old_file: Old file name
    :param str new_file: New file name
    :return: string of HTML formatted table of the provided data
    :rtype: str
    """
    # convert data frame to a series style dictionary
    data = data.to_dict("series")

    # create dictionary to store all the changes
    changes = {"deletes": 0, "additions": 0}

    # combine the flags and update the changes dictionary
    for change in data["flag"].items():
        if change[1] == "deleted":
            changes["deletes"] += 1
        elif change[1] == "added":
            changes["additions"] += 1

    # calculate % of rows deleted from old_file
    percent_deleted = round(((old_row_count - changes["deletes"]) / old_row_count) * -100 + 100, 2)

    # calculate % of rows added to new_file
    percent_added = round(((new_row_count - changes["additions"]) / new_row_count) * -100 + 100, 2)

    # format the html string with the changes and percentages
    overview = f"<br>{changes['deletes']} row(s) deleted from {old_file}: ({percent_deleted}%)<br>"
    overview += f"<br>{changes['additions']} row(s) added to {new_file}: ({percent_added}%)<br>"

    # return the html formatted string
    return overview


def create_filtered_html_table(data: "pd.DataFrame", column: str, value: Any, pop_flag: bool = True) -> str:
    """
    Function to return an HTML formatted table of data from the provided
    pandas dataframe where the provided column == provided value

    :param pd.DataFrame data: Data to create into an HTML table
    :param str column: Column to filter the data on
    :param Any value: Value to filter the data with
    :param bool pop_flag: Whether to remove the column used to filter the data defaults to True
    :return: String of HTML formatted table
    :rtype: str
    """
    # filter the provided pandas dataframe on the column and value provided
    filtered_data = data.loc[data[column] == value]

    # remove the field if requested, default is True
    if pop_flag:
        # remove the column from the dataset
        filtered_data.pop(column)

    # return HTML formatted data table
    return None if filtered_data.empty else filtered_data.to_html(justify="left", index=False)
