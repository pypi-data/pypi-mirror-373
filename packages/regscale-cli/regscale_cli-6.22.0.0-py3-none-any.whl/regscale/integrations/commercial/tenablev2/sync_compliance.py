"""
Sync the compliance data from Tenable.io to RegScale
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin

from pathlib import Path
from rich.console import Console

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    format_dict_to_html,
    get_current_datetime,
)
from regscale.models.integration_models.tenable_models.models import AssetCheck
from regscale.models.regscale_models import ControlImplementation

logger = logging.getLogger("regscale")
console = Console()
artifacts_dir = "./artifacts"
REGSCALE_INC = "RegScale, Inc."
REGSCALE_CLI = "RegScale CLI"
FULLY_IMPLEMENTED = "Fully Implemented"
NOT_IMPLEMENTED = "Not Implemented"
IN_REMEDIATION = "In Remediation"


def sync_compliance_data(ssp_id: int, catalog_id: int, framework: str, offline: Optional[Path] = None) -> None:
    """
    Sync the compliance data from Tenable.io to create control implementations for controls in frameworks
    :param int ssp_id: The ID number from RegScale of the System Security Plan
    :param int catalog_id: The ID number from RegScale Catalog that the System Security Plan's controls belong to
    :param str framework: The framework to use. from Tenable.io frameworks MUST be the same RegScale Catalog of controls
    :param Optional[Path] offline: The file path to load control data instead of fetching from Tenable.io, defaults to None
    :rtype: None
    """
    logger.info("Note: This command only available for Tenable.io")
    logger.info("Note: This command Requires admin access.")
    app = Application()
    config = app.config
    # we specifically don't gen client here, so we only get the client for Tenable.io as its only supported there

    compliance_data = _get_compliance_data(config=config, offline=offline)  # type: ignore

    dict_of_frameworks_and_asset_checks: Dict = dict()
    framework_controls: Dict[str, List[str]] = {}
    asset_checks: Dict[str, List[AssetCheck]] = {}
    passing_controls: Dict = dict()
    # partial_passing_controls: Dict = dict()
    failing_controls: Dict = dict()
    for findings in compliance_data:
        asset_check = AssetCheck(**findings)
        if not asset_check.reference:
            logger.warning(f"Asset check {asset_check.check_name} has no references, skipping.")
            continue
        for ref in asset_check.reference:
            if ref.framework not in framework_controls:
                framework_controls[ref.framework] = []
            if ref.control not in framework_controls[ref.framework]:  # Avoid duplicate controls
                framework_controls[ref.framework].append(ref.control)
                formatted_control_id = convert_control_id(ref.control)
                # sort controls by status
                add_control_to_status_dict(
                    control_id=formatted_control_id,
                    status=asset_check.status,
                    dict_obj=failing_controls,
                    desired_status="FAILED",
                )
                add_control_to_status_dict(
                    control_id=formatted_control_id,
                    status=asset_check.status,
                    dict_obj=passing_controls,
                    desired_status="PASSED",
                )
                remove_passing_controls_if_in_failed_status(passing=passing_controls, failing=failing_controls)
                if formatted_control_id not in asset_checks:
                    asset_checks[formatted_control_id] = [asset_check]
                else:
                    asset_checks[formatted_control_id].append(asset_check)
        dict_of_frameworks_and_asset_checks = {
            key: {"controls": framework_controls, "asset_checks": asset_checks} for key in framework_controls.keys()
        }
    logger.info(f"Found {len(dict_of_frameworks_and_asset_checks)} findings to process")
    framework_data = dict_of_frameworks_and_asset_checks.get(framework, None)
    process_compliance_data(
        framework_data=framework_data,
        catalog_id=catalog_id,
        ssp_id=ssp_id,
        framework=framework,
        passing_controls=passing_controls,
        failing_controls=failing_controls,
    )


def _get_compliance_data(config: dict, offline: Optional[Path] = None) -> Dict:
    """
    Get compliance data from Tenable.io
    :param dict config: Configuration dictionary
    :param Optional[Path] offline: File path to load control data instead of fetching from Tenable.io
    :return: Compliance data
    :rtype: Dict
    """
    from regscale import __version__
    from tenable.io import TenableIO

    if offline:
        with open(offline.absolute(), "r") as f:
            compliance_data = json.load(f)
    else:
        client = TenableIO(
            url=config["tenableUrl"],
            access_key=config["tenableAccessKey"],
            secret_key=config["tenableSecretKey"],
            vendor=REGSCALE_INC,
            product=REGSCALE_CLI,
            build=__version__,
        )
        compliance_data = client.exports.compliance()
    return compliance_data


def add_control_to_status_dict(control_id: str, status: str, dict_obj: Dict, desired_status: str) -> None:
    """
    Add a control to a status dictionary
    :param str control_id: The control id to add to the dictionary
    :param str status: The status of the control
    :param Dict dict_obj: The dictionary to add the control to
    :param str desired_status: The desired status of the control
    :rtype: None
    """
    friendly_control_id = control_id.lower()
    if status == desired_status and friendly_control_id not in dict_obj:
        dict_obj[friendly_control_id] = desired_status


def remove_passing_controls_if_in_failed_status(passing: Dict, failing: Dict) -> None:
    """
    Remove passing controls if they are in failed status
    :param Dict passing: Dictionary of passing controls
    :param Dict failing: Dictionary of failing controls
    :rtype: None
    """
    to_remove = []
    for k in passing.keys():
        if k in failing.keys():
            to_remove.append(k)

    for k in to_remove:
        del passing[k]


def process_compliance_data(
    framework_data: Dict,
    catalog_id: int,
    ssp_id: int,
    framework: str,
    passing_controls: Dict,
    failing_controls: Dict,
) -> None:
    """
    Processes the compliance data from Tenable.io to create control implementations for controls in frameworks
    :param Dict framework_data: List of tenable.io controls per framework
    :param int catalog_id: The catalog id
    :param int ssp_id: The ssp id
    :param str framework: The framework name
    :param Dict passing_controls: Dictionary of passing controls
    :param Dict failing_controls: Dictionary of failing controls
    :rtype: None
    """
    if not framework_data:
        return
    framework_controls = framework_data.get("controls", {})
    asset_checks = framework_data.get("asset_checks", {})
    existing_implementation_dict = get_existing_control_implementations(ssp_id)
    catalog_controls = get_controls(catalog_id)
    matched_controls = []
    for tenable_framework, tenable_controls in framework_controls.items():
        logger.info(f"Found {len(tenable_controls)} controls that passed for framework: {tenable_framework}")
        # logger.info(f"tenable_controls: {tenable_controls[0]}") if len(tenable_controls) >0 else None
        if tenable_framework == framework:
            matched_controls = get_matched_controls(tenable_controls, catalog_controls)

    logger.info(f"Found {len(matched_controls)} controls that matched")

    control_implementations = create_control_implementations(
        controls=matched_controls,
        parent_id=ssp_id,
        parent_module="securityplans",
        existing_implementation_dict=existing_implementation_dict,
        passing_controls=passing_controls,
        failing_controls=failing_controls,
    )

    logger.info(f"SSP now has {len(control_implementations)} control implementations")
    catalog_controls_dict = {c["id"]: c for c in catalog_controls}
    create_assessments(control_implementations, catalog_controls_dict, asset_checks)


def create_assessments(
    control_implementations: List[Dict],
    catalog_controls_dict: Dict,
    asset_checks: Dict,
) -> None:
    """
    Create assessments from control implementations
    :param List[Dict] control_implementations: List of control implementations
    :param Dict catalog_controls_dict: Dictionary of catalog controls
    :param Dict asset_checks: Dictionary of asset checks
    :rtype: None
    :return: None
    """
    app = Application()
    user_id = app.config.get("userId", "")
    assessments_to_create = []
    for cim in control_implementations:
        control = catalog_controls_dict.get(cim["controlID"], {})
        check = asset_checks.get(control["controlId"].lower())
        assessment = create_assessment_from_cim(cim, user_id, control, check)
        assessments_to_create.append(assessment)
    update_control_implementations(control_implementations, assessments_to_create)
    post_assessments_to_api(assessments_to_create)


def get_control_assessments(control: Dict, assessments_to_create: List[Dict]) -> List[Dict]:
    """
    Get control assessments
    :param Dict control: Control
    :param List[Dict] assessments_to_create: List of assessments to create
    :return: List of control assessments
    :rtype: List[Dict]
    """
    return [
        assess
        for assess in assessments_to_create
        if assess["controlID"] == control["id"] and assess["status"] == "Complete"
    ]


def post_assessments_to_api(assessments_to_create: List[Dict]) -> None:
    """
    Post assessments to the API
    :param List[Dict] assessments_to_create: List of assessments to create
    :rtype: None
    """
    app = Application()
    api = Api()
    assessment_url = urljoin(app.config.get("domain", ""), "/api/assessments/batchCreate")
    assessment_response = api.post(url=assessment_url, json=assessments_to_create)
    if assessment_response.ok:
        logger.info(f"Created {len(assessment_response.json())} Assessments!")
    else:
        logger.debug(assessment_response.status_code)
        logger.error(f"Failed to insert Assessment.\n{assessment_response.text}")


def update_control_implementations(control_implementations: List[Dict], assessments_to_create: List[Dict]) -> None:
    """
    Update control implementations with assessments
    :param List[Dict] control_implementations: List of control implementations
    :param List[Dict] assessments_to_create: List of assessments to create
    :rtype: None
    """
    for control in control_implementations:
        control_assessments = get_control_assessments(control, assessments_to_create)
        if sorted_assessments := sort_assessments(control_assessments):
            update_control_object(control, sorted_assessments)


def update_control_object(control: Dict, sorted_assessments: List[Dict]) -> None:
    """
    Update control object
    :param Dict control: Control
    :param List[Dict] sorted_assessments: Sorted assessments
    :rtype: None
    """

    dt_format = "%Y-%m-%d %H:%M:%S"
    app = Application()
    control["dateLastAssessed"] = sorted_assessments[0]["actualFinish"]
    control["lastAssessmentResult"] = sorted_assessments[0]["assessmentResult"]
    if control.get("lastAssessmentResult"):
        control_obj = ControlImplementation(**control)
        if control_obj.lastAssessmentResult == "Fail" and control_obj.status != IN_REMEDIATION:
            control_obj.status = IN_REMEDIATION
            control_obj.plannedImplementationDate = (datetime.now() + timedelta(30)).strftime(dt_format)
            control_obj.stepsToImplement = "n/a"
        elif control_obj.status == IN_REMEDIATION:
            control_obj.plannedImplementationDate = (
                (datetime.now() + timedelta(30)).strftime(dt_format)
                if not control_obj.plannedImplementationDate
                else control_obj.plannedImplementationDate
            )
            control_obj.stepsToImplement = "n/a" if not control_obj.stepsToImplement else control_obj.stepsToImplement
        elif control_obj.lastAssessmentResult == "Pass" and control_obj.status != FULLY_IMPLEMENTED:
            control_obj.status = FULLY_IMPLEMENTED
        ControlImplementation.update(app=app, implementation=control_obj)


def sort_assessments(control_assessments: List[Dict]) -> List[Dict]:
    """
    Sort assessments by actual finish date
    :param List[Dict] control_assessments: List of control assessments
    :return: Sorted assessments
    :rtype: List[Dict]
    """
    dt_format = "%Y-%m-%d %H:%M:%S"
    return sorted(
        control_assessments,
        key=lambda x: datetime.strptime(x["actualFinish"], dt_format),
        reverse=True,
    )


def get_assessment_status_from_implementation_status(status: str) -> str:
    """
    Get the assessment status from the implementation status
    :param str status: Implementation status
    :return: Assessment status
    :rtype: str
    """
    if status == FULLY_IMPLEMENTED:
        return "Pass"
    if status == IN_REMEDIATION:
        return "Fail"
    else:
        return "N/A"


def create_assessment_from_cim(cim: Dict, user_id: str, control: Dict, check: List[AssetCheck]) -> Dict:
    """
    Create an assessment from a control implementation
    :param Dict cim: Control Implementation
    :param str user_id: User ID
    :param Dict control: Control
    :param List[AssetCheck] check: Asset Check
    :return: Assessment
    :rtype: Dict
    """
    assessment_result = get_assessment_status_from_implementation_status(cim.get("status"))
    summary_dict = check[0].dict() if check else dict()
    summary_dict.pop("reference", None)
    title = summary_dict.get("check_name") if summary_dict else control.get("title")
    html_summary = format_dict_to_html(summary_dict)
    document_reviewed = check[0].audit_file if check else None
    check_name = check[0].check_name if check else None
    methodology = check[0].check_info if check else None
    summary_of_results = check[0].description if check else None
    uuid = check[0].asset_uuid if check and check[0].asset_uuid is not None else None
    title_part = f"{title} - {uuid}" if uuid else f"{title}"
    uuid_title = f"{title_part} Automated Assessment test"
    return {
        "leadAssessorId": user_id,
        "title": uuid_title,
        "assessmentType": "Control Testing",
        "plannedStart": get_current_datetime(),
        "plannedFinish": get_current_datetime(),
        "status": "Complete",
        "assessmentResult": assessment_result if assessment_result else "N/A",
        "controlID": cim["id"],
        "actualFinish": get_current_datetime(),
        "assessmentReport": html_summary if html_summary else "Passed",
        "parentId": cim["id"],
        "parentModule": "controls",
        "assessmentPlan": check_name if check_name else None,
        "documentsReviewed": document_reviewed if document_reviewed else None,
        "methodology": methodology if methodology else None,
        "summaryOfResults": summary_of_results if summary_of_results else None,
    }


def get_matched_controls(tenable_controls: List[Dict], catalog_controls: List[Dict]) -> List[Dict]:
    """
    Get controls that match between Tenable and the catalog
    :param List[Dict] tenable_controls: List of controls from Tenable
    :param List[Dict] catalog_controls: List of controls from the catalog
    :return: List of matched controls
    :rtype: List[Dict]
    """
    matched_controls = []
    for control in tenable_controls:
        formatted_control = convert_control_id(control)
        logger.info(formatted_control)
        for catalog_control in catalog_controls:
            if catalog_control["controlId"].lower() == formatted_control.lower():
                logger.info(f"Catalog Control {formatted_control} matched")
                matched_controls.append(catalog_control)
                break
    return matched_controls


def create_control_implementations(
    controls: list,
    parent_id: int,
    parent_module: str,
    existing_implementation_dict: Dict,
    passing_controls: Dict,
    failing_controls: Dict,
) -> List[Dict]:
    """
    Creates a list of control implementations
    :param list controls: list of controls
    :param int parent_id: parent control id
    :param str parent_module: parent module
    :param Dict existing_implementation_dict: Dictionary of existing control implementations
    :param Dict passing_controls: Dictionary of passing controls
    :param Dict failing_controls: Dictionary of failing controls
    :return: list of control implementations
    :rtype: List[Dict]
    """
    app = Application()
    api = Api()
    user_id = app.config.get("userId")
    domain = app.config.get("domain")
    control_implementations = []
    to_create = []
    to_update = []
    for control in controls:
        lower_case_control_id = control["controlId"].lower()
        status = check_implementation(
            passing_controls=passing_controls,
            failing_controls=failing_controls,
            control_id=lower_case_control_id,
        )
        if control["controlId"] not in existing_implementation_dict.keys():
            cim = ControlImplementation(
                controlOwnerId=user_id,
                dateLastAssessed=get_current_datetime(),
                status=status,
                controlID=control["id"],
                parentId=parent_id,
                parentModule=parent_module,
                createdById=user_id,
                dateCreated=get_current_datetime(),
                lastUpdatedById=user_id,
                dateLastUpdated=get_current_datetime(),
            ).dict()
            cim["controlSource"] = "Baseline"
            to_create.append(cim)

        else:
            # update existing control implementation data
            existing_imp = existing_implementation_dict.get(control["controlId"])
            existing_imp["status"] = status
            existing_imp["dateLastAssessed"] = get_current_datetime()
            existing_imp["lastUpdatedById"] = user_id
            existing_imp["dateLastUpdated"] = get_current_datetime()
            del existing_imp["createdBy"]
            del existing_imp["systemRole"]
            del existing_imp["controlOwner"]
            del existing_imp["lastUpdatedBy"]
            to_update.append(existing_imp)

    if len(to_create) > 0:
        ci_url = urljoin(domain, "/api/controlImplementation/batchCreate")
        resp = api.post(url=ci_url, json=to_create)
        if resp.ok:
            control_implementations.extend(resp.json())
            logger.info(f"Created {len(to_create)} Control Implementation(s), Successfully!")
        else:
            resp.raise_for_status()
    if len(to_update) > 0:
        ci_url = urljoin(domain, "/api/controlImplementation/batchUpdate")
        resp = api.post(url=ci_url, json=to_update)
        if resp.ok:
            control_implementations.extend(resp.json())
            logger.info(f"Updated {len(to_update)} Control Implementation(s), Successfully!")
        else:
            resp.raise_for_status()
    return control_implementations


def check_implementation(passing_controls: Dict, failing_controls: Dict, control_id: str) -> str:
    """
    Checks the status of a control implementation
    :param Dict passing_controls: Dictionary of passing controls
    :param Dict failing_controls: Dictionary of failing controls
    :param str control_id: control id
    :return: status of control implementation
    :rtype: str
    """
    if control_id in passing_controls.keys():
        return FULLY_IMPLEMENTED
    elif control_id in failing_controls.keys():
        return IN_REMEDIATION
    else:
        return NOT_IMPLEMENTED


def convert_control_id(control_id: str) -> str:
    """
    Convert the control id to a format that can be used in Tenable.io
    :param str control_id: The control id to convert
    :return: The converted control id
    :rtype: str
    """
    # Convert to lowercase
    control_id = control_id.lower()

    # Check if there's a parenthesis and replace its content
    if "(" in control_id and ")" in control_id:
        inner_value = control_id.split("(")[1].split(")")[0]
        control_id = control_id.replace(f"({inner_value})", f".{inner_value}")

    return control_id


def get_existing_control_implementations(parent_id: int) -> Dict:
    """
    fetch existing control implementations
    :param int parent_id: parent control id
    :return: Dictionary of existing control implementations
    :rtype: Dict
    """
    app = Application()
    api = Api()
    domain = app.config.get("domain")
    existing_implementation_dict = {}
    get_url = urljoin(domain, f"/api/controlImplementation/getAllByPlan/{parent_id}")
    response = api.get(get_url)
    if response.ok:
        existing_control_implementations_json = response.json()
        for cim in existing_control_implementations_json:
            existing_implementation_dict[cim["controlName"]] = cim
        logger.info(f"Found {len(existing_implementation_dict)} existing control implementations")
    elif response.status_code == 404:
        logger.info(f"No existing control implementations found for {parent_id}")
    else:
        logger.warning(f"Unable to get existing control implementations. {response.text}")

    return existing_implementation_dict


def get_controls(catalog_id: int) -> List[Dict]:
    """
    Gets all the controls
    :param int catalog_id: catalog id
    :return: list of controls
    :rtype: List[Dict]
    """
    app = Application()
    api = Api()
    url = urljoin(app.config.get("domain"), f"/api/SecurityControls/getList/{catalog_id}")
    response = api.get(url)
    if response.ok:
        return response.json()
    else:
        response.raise_for_status()
    return []
