import csv
import datetime
import uuid
from typing import Dict, List, Any, Optional

from regscale.core.app import create_logger
from regscale.core.app.utils.catalog_utils.common import parentheses_to_dot
from regscale.models import regscale_models as rm, ControlImplementationStatus

logger = create_logger()
# Define a list to hold log entries for CSV output
log_entries: List[Dict[str, str]] = []


def _log_change(action: str, model: str, message: str, changes: Optional[Dict[str, Any]] = None):
    """
    Log changes to both the logger and a list for later CSV output.
    :param str action: The type of action (e.g., 'Add', 'Update', 'Remove')
    :param str model: The model being changed (e.g., 'Control', 'Objective', 'Parameter')
    :param str message: The message to log
    :param Optional[Dict[str, Any]] changes: Optional changes to log
    """
    logger.info(message)
    log_entries.append({"action": action, "model": model, "message": message, "changes": str(changes)})


def _write_log_to_csv(filename: str):
    """
    Write all log entries to a CSV file.

    :param str filename: The filename for the CSV output
    """
    entry_count = len(log_entries)
    if entry_count > 0:
        logger.info(f"Writing {entry_count} changes to {filename}")
        with open(filename, "w", newline="") as csvfile:
            fieldnames = ["action", "model", "message", "changes"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in log_entries:
                writer.writerow(entry)
        logger.info(f"Successfully wrote all entries to {filename}")
    else:
        logger.info("No changes to write to CSV")


def _log_summary():
    """
    Log statistics about the entries, summarized by action and model.
    """
    from collections import defaultdict
    from rich.console import Console

    console = Console()
    summary: defaultdict[Any, int] = defaultdict(int)
    for entry in log_entries:
        key = (entry["action"], entry["model"])
        summary[key] += 1

    # Print statistics in a table-like format in green color
    console.print("Summary of Changes:", style="green")
    console.print(f"{'Action':<20} {'Model':<20} {'Count':<10}", style="green")
    console.print("-" * 50, style="green")
    for (action, model), count in summary.items():
        console.print(f"{action:<20} {model:<20} {count:<10}", style="green")


def sync_controls(catalog_controls: Dict[str, rm.SecurityControl], ssp_id: int, dry_run: bool = False):
    """
    Sync controls from a catalog to an SSP

    :param Dict[str, rm.SecurityControl] catalog_controls: List of controls from the catalog
    :param int ssp_id: SSP ID
    :param bool dry_run: Dry run flag
    """
    logger.info(f"Syncing controls from catalog to SSP: {ssp_id}")

    catalog_id_to_label = {x.id: x.controlId for x in catalog_controls.values()}

    ssp = rm.SecurityPlan.get_object(object_id=ssp_id)
    if not ssp:
        logger.warning("SSP not found")
        exit(1)

    ssp_controls = {
        parentheses_to_dot(catalog_id_to_label[x.controlID]): x
        for x in rm.ControlImplementation.get_all_by_parent(
            parent_id=ssp.id, parent_module=rm.SecurityPlan.get_module_string()
        )
        if x.controlID in catalog_id_to_label
    }

    # Add or update controls
    for control_id, control in catalog_controls.items():
        sync_control(control, control_id, dry_run, ssp, ssp_controls)

    # Remove controls not in the catalog
    for ssp_control_id, ssp_control in ssp_controls.items():
        if ssp_control.controlID not in catalog_id_to_label:
            _log_change("Remove", "Control", f"Removing control {ssp_control.controlID} from SSP {ssp.systemName}")
            if not dry_run:
                ssp_control.delete()


def sync_control(
    control: rm.Control,
    control_id: str,
    dry_run: bool,
    ssp: rm.SecurityPlan,
    ssp_controls: Dict[str, rm.ControlImplementation],
):
    """
    Sync a control from a catalog to an SSP

    :param rm.Control control: The control from the catalog
    :param str control_id: The control ID
    :param bool dry_run: Dry run flag
    :param rm.SecurityPlan ssp: The SSP
    :param Dict[str, rm.ControlImplementation] ssp_controls: The controls in the SSP
    """
    logger.debug(f"Syncing control {control_id}")
    ssp_control = ssp_controls.get(parentheses_to_dot(control_id))
    if ssp_control is None:
        # Create a new control in the SSP
        print(f"Control Owner ID: {ssp.createdById}")
        print(f"API Handler User ID: {rm.ControlImplementation.get_user_id()}")
        ssp_control = rm.ControlImplementation(
            controlOwnerId=ssp.systemOwnerId or ssp.createdById or rm.ControlImplementation.get_user_id(),
            status=ControlImplementationStatus.NotImplemented,
            controlID=control.id,
            parentId=ssp.id,
            parentModule=ssp.get_module_string(),
        )
        _log_change(
            "Add",
            "Control",
            f"Adding control {control.controlId} to SSP {ssp.systemName}",
            changes=ssp_control.show_changes(),
        )
        if not dry_run:
            ssp_control = ssp_control.create()
    else:
        # Update the existing control in the SSP
        if ssp_control.controlOwnerId in ["", None]:
            ssp_control.controlOwnerId = ssp.systemOwnerId or ssp.createdById or rm.ControlImplementation.get_user_id()
        if ssp_control.has_changed():
            _log_change(
                "Update",
                "Control",
                f"Updating control {control.controlId} in SSP {ssp.systemName}",
                changes=ssp_control.show_changes(),
            )
            if not dry_run:
                ssp_control.save()
    sync_objectives(control, dry_run, ssp_control)
    sync_parameters(control, dry_run, ssp_control)


def sync_objectives(control: rm.SecurityControl, dry_run: bool, ssp_control: rm.Control):
    """
    Sync objectives for a control

    :param rm.SecurityControl control: The control
    :param bool dry_run: Dry run flag
    :param rm.Control ssp_control: The SSP control
    """
    ssp_objectives: Dict[int, rm.ImplementationObjective] = {  # type: ignore
        x.objectiveId: x
        for x in rm.ImplementationObjective.get_all_by_parent(
            parent_id=ssp_control.id, parent_module=rm.ControlImplementation.get_module_string()
        )
    }
    control_objectives: Dict[int, rm.ControlObjective] = {  # type: ignore
        x.id: x
        for x in rm.ControlObjective.get_all_by_parent(
            parent_id=control.id, parent_module=rm.SecurityControl.get_module_string()
        )
    }

    # Remove objectives that are not in the catalog
    for objective_id in ssp_objectives.keys():
        if objective_id not in control_objectives.keys():
            _log_change(
                "Remove",
                "Objective",
                f"Removing objective {objective_id} from control {control.controlId}",
            )
            if not dry_run:
                ssp_objectives[objective_id].delete()


def sync_parameters(control: rm.SecurityControl, dry_run: bool, ssp_control: rm.ControlImplementation):
    """
    Sync parameters for a control

    :param rm.SecurityControl control: The control
    :param bool dry_run: Dry run flag
    :param rm.ControlImplementation ssp_control: The SSP control
    """
    ssp_parameters = get_ssp_parameters(ssp_control)
    control_parameters = get_control_parameters(control)

    # Add or update parameters
    add_or_update_parameters(control_parameters, ssp_parameters, control, dry_run, ssp_control)

    # Remove parameters that are not in the catalog
    remove_unused_parameters(ssp_parameters, control_parameters, control, dry_run)


def get_ssp_parameters(ssp_control):
    return {
        x.parentParameterId: x
        for x in rm.Parameter.get_all_by_parent(
            parent_id=ssp_control.id, parent_module=rm.ControlImplementation.get_module_string()
        )
    }


def get_control_parameters(control):
    return {
        x.id: x
        for x in rm.ControlParameter.get_all_by_parent(
            parent_id=control.id, parent_module=rm.SecurityControl.get_module_string()
        )
    }


def add_or_update_parameters(control_parameters, ssp_parameters, control, dry_run, ssp_control):
    for control_parameter in control_parameters.values():
        if control_parameter.id in ssp_parameters:
            update_parameter(ssp_parameters[control_parameter.id], control_parameter, control, dry_run)
        else:
            add_parameter(control_parameter, control, dry_run, ssp_control)


def update_parameter(ssp_parameter, control_parameter, control, dry_run):
    ssp_parameter.parentParameterId = control_parameter.id
    ssp_parameter.name = control_parameter.displayName
    ssp_parameter.value = control_parameter.text
    if ssp_parameter.has_changed():
        _log_change(
            "Update",
            "Parameter",
            f"Updating parameter {ssp_parameter.name} in control {control.controlId}",
            changes=ssp_parameter.show_changes(),
        )
        if not dry_run:
            ssp_parameter.save()


def add_parameter(control_parameter, control, dry_run, ssp_control):
    ssp_parameter = rm.Parameter(
        uuid=uuid.uuid4().__str__(),
        name=control_parameter.displayName,
        value=control_parameter.text or "",
        controlImplementationId=ssp_control.id,
        parentParameterId=control_parameter.id,
    )
    _log_change(
        "Add",
        "Parameter",
        f"Adding parameter {ssp_parameter.name} to control {control.controlId}",
        changes=ssp_parameter.show_changes(),
    )
    if not dry_run:
        ssp_parameter = ssp_parameter.create()


def remove_unused_parameters(ssp_parameters, control_parameters, control, dry_run):
    for parameter_id in ssp_parameters.keys():
        if parameter_id not in control_parameters:
            _log_change(
                "Remove",
                "Parameter",
                f"Removing parameter {parameter_id} from control {control.controlId}",
            )
            if not dry_run:
                ssp_parameters[parameter_id].delete()


def get_controls_from_profile(ssp_id: int) -> Dict[str, rm.SecurityControl]:
    """
    Get controls from a profile

    :param int ssp_id: The SSP ID
    :return: The controls
    :rtype: Dict[str, rm.SecurityControl]
    """
    logger.info(f"Getting controls from profile: {ssp_id}")
    profile_links = rm.ProfileLink.get_all_by_parent(
        parent_id=ssp_id, parent_module=rm.SecurityPlan.get_module_string()
    )
    controls: List[rm.SecurityControl] = []
    control_get_count = 0
    for profile_link in profile_links:
        profile_mappings: list[rm.ProfileMapping] = rm.ProfileMapping.get_all_by_parent(
            parent_id=profile_link.profileId, parent_module=rm.Profile.get_module_string()
        )
        for profile_mapping in profile_mappings:
            control = rm.SecurityControl.get_object(object_id=profile_mapping.controlID)
            if control:
                print(control.controlId, end=" ")
                controls.append(control)
                control_get_count += 1
                if control_get_count % 10 == 0:
                    print()
            else:
                logger.warning(f"Control {profile_mapping.controlID} not found")
    return {parentheses_to_dot(x.controlId): x for x in controls}


def sync_plan_controls(ssp_id: int, dry_run: bool = False):
    """
    Sync controls from a profile to an SSP

    :param int ssp_id: The SSP ID
    :param bool dry_run: Dry run flag
    """
    logger.info(f"Syncing controls from profile to SSP: {ssp_id}")
    log_entries.clear()
    catalog_controls = get_controls_from_profile(ssp_id=ssp_id)
    sync_controls(catalog_controls=catalog_controls, ssp_id=ssp_id, dry_run=dry_run)
    _write_log_to_csv(f"plan_{ssp_id}_log_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
    _log_summary()


def sync_all_plans(dry_run: bool = False):
    """
    Sync all plans

    :param bool dry_run: Dry run flag
    """
    for ssp in rm.SecurityPlan.get_list():  # type: rm.SecurityPlan
        sync_plan_controls(ssp.id, dry_run)
