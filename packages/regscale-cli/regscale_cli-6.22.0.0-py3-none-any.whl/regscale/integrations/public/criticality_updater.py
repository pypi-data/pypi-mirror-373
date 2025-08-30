import click
from regscale.models.regscale_models.security_control import SecurityControl
import logging

logger = logging.getLogger(__name__)


# Function to update the security control's criticality using the API
def update_security_control_criticality(control_id: str, criticality: str, control_dict: dict):
    """
    Update the security control's criticality using the API.
    :param control_dict:
    :param str control_id:
    :param str criticality:
    """
    control_id = control_id.lower().strip().replace(" ", "")
    matching_control: SecurityControl = control_dict.get(control_id.lower().strip())
    logger.info(
        f"Updating control {control_id} == {matching_control.controlId.lower().strip() if matching_control else None} with criticality {criticality}"
    )
    if control := control_dict.get(control_id):
        control.criticality = criticality
        control.save()


@click.group(name="criticality_updater")
def criticality_updater():
    """
    Update the criticality of security controls in the catalog.
    """


@criticality_updater.command(name="import")
@click.option("--file_path", "-f", help="Path to the Excel file", required=True, type=click.Path(exists=True))
@click.option("--catalog_id", "-cat", help="Catalog ID", required=True, type=int)
@click.option(
    "--column_header_control_id",
    "-ci",
    help="Column header for the Security Control ID",
    default="Security Control #",
    required=True,
)
@click.option(
    "--column_header_criticality",
    "-c",
    help="Column header for the Criticality Rating",
    default="Security Control Criticality Rating",
    required=True,
)
def update_control_criticality(
    file_path: str, catalog_id: int, column_header_control_id: str, column_header_criticality: str
):
    """
    Update the criticality of security controls in the catalog.
    """
    import pandas as pd  # Optimize import performance

    df = pd.read_excel(file_path)
    controls = SecurityControl.get_all_by_parent(parent_id=catalog_id, parent_module="catalogs")  # Get all the controls
    logger.info(f"Found {len(controls)} controls")
    control_dict = {control.controlId.lower(): control for control in controls}  # Create a dictionary for easy access
    # Loop through the DataFrame and map the controls
    for index, row in df.iterrows():
        control_id = row.get(column_header_control_id)  # Column A - Security Control
        criticality = row.get(column_header_criticality)  # Column D - Criticality Rating

        if pd.notna(control_id) and pd.notna(criticality):  # Ensure the values are not empty
            # Update the security control with the new criticality
            update_security_control_criticality(control_id, criticality, control_dict)
    logger.info("Finished processing all records.")
