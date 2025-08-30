import click
from pathlib import Path
import os
from rich.progress import track
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils.dataframe import dataframe_to_rows

from regscale.core.app.logz import create_logger
from regscale.models.regscale_models.modules import Modules
from regscale.models.regscale_models.rbac import RBAC
from regscale.models.regscale_models.group import Group
from regscale.models.app_models import ImportValidater

logger = create_logger()
PUBLIC_PRIVATE = "public | private"
READ_UPDATE = "Read | Read Update"


@click.group(name="set_permissions")
def set_permissions():
    """
    Sets permissions on RegScale records
    """


# Make Empty Spreadsheet for creating new assessments.
@set_permissions.command(name="new")
@click.option(
    "--path",
    type=click.Path(exists=False, dir_okay=True, path_type=Path),
    help="Provide the desired path into which the excel template file is saved.",
    default=os.path.join(os.getcwd(), "artifacts"),
    required=True,
)
def generate_new_file(path: Path):
    """This function will build an Excel spreadsheet for users to be
    load bulk ACLs on RegScale Records."""
    create_workbook(path)


def create_workbook(path: Path):
    """
    Creates a new Excel workbook with a worksheet for setting permissions in RegScale

    :param Path path: The path where the workbook will be saved
    """
    import pandas as pd

    workbook_filename = os.path.join(os.getcwd(), path, "import_acls.xlsx")
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "RegScale_Set_Permissions"
    workbook.save(filename=workbook_filename)

    filler = []
    for _index_ in range(100):
        filler.append("")

    data = {
        "regscale_id": filler,
        "regscale_module": filler,
        PUBLIC_PRIVATE: filler,
        "group_id": filler,
        READ_UPDATE: filler,
    }
    df = pd.DataFrame(data)
    # Create the headers and filler data
    for r in dataframe_to_rows(df, index=False, header=True):
        worksheet.append(r)

    # Set pick lists
    dv_mode = DataValidation(type="list", formula1='"public, private"', allow_blank=True)
    dv_mode.add(cell="C2:C100")
    worksheet.add_data_validation(dv_mode)
    dv_right = DataValidation(type="list", formula1='"R, RU"', allow_blank=True)
    dv_right.add(cell="E2:E100")
    worksheet.add_data_validation(dv_right)

    # Fix width
    for col in worksheet.columns:
        max_length = 0
        column_letter = col[0].column_letter

        for cell in col:
            # Determine max length for column width
            cell_length = len(str(cell.value))
            max_length = max(max_length, cell_length)

        # Set adjusted column width
        adjusted_width = (max_length + 2) * 1.2
        worksheet.column_dimensions[column_letter].width = adjusted_width

    # Write out the formatting to the file
    workbook.save(filename=workbook_filename)


@set_permissions.command(name="load")
@click.option(
    "--file",
    type=click.Path(exists=False, dir_okay=True, path_type=Path),
    help="Provide the path and filename of the file containing the permissions to load",
    required=True,
)
def import_permissions(file: Path):
    """This function creates permissions on RegScale records recorded
    in a spreadsheet"""
    import_permissions_workbook(file)


def import_permissions_workbook(file: Path):
    """
    Imports permissions from a workbook file and applies them to RegScale records

    :param Path file: The path to the workbook file containing permissions
    """
    # Read in the spreadsheet
    records = get_records(file=file)
    for index in track(
        range(len(records)),
        description="Processing rbacs...",
    ):
        record = records[index]
        # Check the records:

        if not Group.get_object(record["group_id"]):
            logger.error(f"Group {record['group_id']} doesn't exist in this instance.  Skipping row")
            continue

        my_class = Modules.module_to_class(record["regscale_module"])
        obj = my_class.get_object(record["regscale_id"])
        if not obj:
            logger.error(
                f"RegScale {record['regscale_module']} record {record['regscale_id']} doesn't exist. Skipping row"
            )
            continue

        # Set the permissions
        set_permissions(record=record)


def set_permissions(record: dict):
    """
    Sets the permissions for each record

    :param dict record: permissions dictionary
    """

    if record[READ_UPDATE] == "R":
        permissions = 1
    elif record[READ_UPDATE] == "RU":
        permissions = 2
    else:
        permissions = 0

    # Add the permission
    if not RBAC.add(
        module_id=Modules.get_module_to_id(record["regscale_module"]),
        parent_id=record["regscale_id"],
        group_id=record["group_id"],
        permission_type=permissions,
    ):
        logger.warning(
            f"Failed to set permissions for {record['regscale_module']} {record['regscale_id']} for group {record['group_id']}"
        )
        return

    if not RBAC.public(
        module_id=Modules.get_module_to_id(record["regscale_module"]),
        parent_id=record["regscale_id"],
        is_public=0 if record[PUBLIC_PRIVATE] == "private" else 1,
    ):
        logger.warning(
            f"Failed to set public/private for {record['regscale_module']} {record['regscale_id']} for group {record['group_id']}"
        )
        return

    if not RBAC.reset(
        module_id=Modules.get_module_to_id(record["regscale_module"]),
        parent_id=record["regscale_id"],
    ):
        logger.warning(
            f"Failed to proliferate permissions for {record['regscale_module']} {record['regscale_id']} for group {record['group_id']}"
        )


def get_records(file: Path) -> list:
    """
    Takes the file name and returns the records in the file

    :param Path file: spreadsheet containing permission records
    :return: records from file
    :return_type: list
    """
    required_headers = ["regscale_id", "regscale_module", PUBLIC_PRIVATE, "group_id", READ_UPDATE]
    validator = ImportValidater(
        file_path=file,
        required_headers=required_headers,
        worksheet_name="RegScale_Set_Permissions",
        skip_rows=1,
        disable_mapping=True,
        mapping_file_path="./",
    )
    return validator.data.to_dict(orient="records")
