#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates CSAM into RegScale"""

# standard python imports
import logging
from typing import List, Optional, Tuple, Any, Dict
from urllib.parse import urljoin
from rich.progress import track
import click
from rich.console import Console
from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.utils.date import format_to_regscale_iso, date_obj
from regscale.core.app.utils.app_utils import error_and_exit, filter_list
from regscale.core.app.utils.parser_utils import safe_date_str
from regscale.models.regscale_models import (
    Catalog,
    ControlImplementation,
    InheritedControl,
    Inheritance,
    Issue,
    Organization,
    SecurityControl,
    SecurityPlan,
    User,
)
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models.regscale_models.module import Module
from regscale.models.regscale_models.form_field_value import FormFieldValue
from regscale.core.app.utils.regscale_utils import normalize_controlid

logger = logging.getLogger("regscale")
console = Console()

####################################################################################################
#
# IMPORT SSP / POAM FROM DoJ's CSAM GRC
# CSAM API Docs: https://csam.dhs.gov/CSAM/api/docs/index.html (required PIV)
#
####################################################################################################

SSP_BASIC_TAB = "Basic Info"
SSP_SYSTEM_TAB = "System Information"
SSP_FINANCIAL_TAB = "Financial Info"
SSP_PRIVACY_TAB = "Privacy-Details"
CSAM_FIELD_NAME = "CSAM Id"
FISMA_FIELD_NAME = "FISMA Id"
POAM_ID = "POAM Id"
SYSTEM_ID = "System ID"


@click.group()
def csam():
    """Integrate CSAM."""


@csam.command(name="import_ssp")
def import_ssp():
    """
    Import SSP from CSAM
    Into RegScale
    """

    import_csam_ssp()


@csam.command(name="import_poam")
def import_poam():
    """
    Import POAMS from CSAM
    Into RegScale
    """

    import_csam_poams()


def import_csam_ssp():
    """
    Import an SSP from CSAM
    Into RegScale
    """
    custom_fields_basic_list = [
        "acronym",
        "Financial System",
        "Classification",
        "FISMA Reportable",
        "Contractor System",
        "Authorization Process",
        "ATO Date",
        "Critical Infrastructure",
        "Mission Essential",
        "uui Code",
        "HVA Identifier",
        "External Web Interface",
        "CFO Designation",
        "AI/ML Components",
        "Law Enforcement Sensitive",
        CSAM_FIELD_NAME,
        FISMA_FIELD_NAME,
    ]
    custom_fields_financial_list = [
        "omb Exhibit",
        "Investment Name",
        "Portfolio",
        "Prior Fy Funding",
        "Current Fy Funding",
        "Next Fy Funding",
        "Funding Import Status",
    ]

    # Check Custom Fields exist
    custom_fields_basic_map = FormFieldValue.check_custom_fields(
        custom_fields_basic_list, "securityplans", SSP_BASIC_TAB
    )
    custom_fields_financial_map = FormFieldValue.check_custom_fields(
        custom_fields_financial_list, "securityplans", SSP_FINANCIAL_TAB
    )

    # Get a map of existing custom forms
    ssp_map = retrieve_ssps_custom_form_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[FISMA_FIELD_NAME]
    )

    # Get a list of orgs and create a map to id
    orgs = Organization.get_list()
    org_map = {org.name: org.id for org in orgs}

    # Grab the data from CSAM
    app = Application()
    csam_token = app.config.get("csamToken")
    csam_url = app.config.get("csamURL")
    csam_filter = app.config.get("csamFilter", None)

    results = retrieve_from_csam(
        csam_token=csam_token,
        csam_url=csam_url,
        csam_endpoint="/CSAM/api/v1/systems",
    )

    results = filter_list(results, csam_filter)
    if not results:
        error_and_exit(
            "No results match filter in CSAM. \
                       Please check your CSAM configuration."
        )

    # Parse the results
    updated_ssps = []
    updated_ssps = save_ssp_front_matter(
        results=results,
        ssp_map=ssp_map,
        custom_fields_basic_map=custom_fields_basic_map,
        custom_fields_financial_map=custom_fields_financial_map,
        org_map=org_map,
    )

    # Now have to get the system details for each system
    update_ssp_agency_details(updated_ssps, csam_token, csam_url, custom_fields_basic_map)

    # Import the Privacy date
    import_csam_privacy_info(import_ids=[ssp.id for ssp in updated_ssps])

    # Import the controls
    import_csam_controls(import_ids=[ssp.id for ssp in updated_ssps])

    # Set inheritance if system type = program
    for result in results:
        if result.get("systemType") == "Program":
            # Get the RegScale SSP Id
            program_id = ssp_map.get(result["externalId"])
            if not program_id:
                logger.error(
                    f"Could not find RegScale SSP for CSAM id: {result['externalId']}. \
                    Please create or import the Security Plan prior to importing inheritance."
                )
                continue

            # Set the inheritable flag
            set_inheritable(regscale_id=result.get("id"))

    # Import the Inheritance
    import_csam_inheritance(import_ids=[ssp.id for ssp in updated_ssps])

    # Import the POCs
    import_csam_pocs(import_ids=[ssp.id for ssp in updated_ssps])


def import_csam_controls(import_ids: Optional[List[int]] = None):
    """
    Import Controls from CSAM

    :param list import_ids: Filtered list of SSPs
    :return: None
    """

    # Grab the data from CSAM
    app = Application()
    csam_token = app.config.get("csamToken")
    csam_url = app.config.get("csamURL")

    # Get existing ssps by CSAM Id
    custom_fields_basic_map = FormFieldValue.check_custom_fields([CSAM_FIELD_NAME], "securityplans", SSP_BASIC_TAB)
    ssp_map = retrieve_custom_form_ssp_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    plans = import_ids if import_ids else list(ssp_map.keys())

    # Find the Catalogs
    rev5_catalog_id, rev4_catalog_id = get_catalogs()

    # Get the list of controls for each catalog
    rev5_controls = SecurityControl.get_list_by_catalog(catalog_id=rev5_catalog_id)
    rev4_controls = SecurityControl.get_list_by_catalog(catalog_id=rev4_catalog_id)

    control_implementations = []
    for regscale_ssp_id in plans:
        results = []
        system_id = ssp_map.get(regscale_ssp_id)

        # Get the Implementation for AC-1
        # Check the controlSet
        # Match the catalog
        imp = retrieve_from_csam(
            csam_token=csam_token,
            csam_url=csam_url,
            csam_endpoint=f"/CSAM/api/v1/systems/{system_id}/controls/AC-1",
        )

        # Get the controls
        if imp[0].get("controlSet") in ["NIST 800-53 Rev4", "NIST 800-53 Rev5"]:
            results = retrieve_controls(
                csam_token=csam_token,
                csam_url=csam_url,
                csam_id=system_id,
                controls=rev4_controls if imp[0].get("controlSet") == "NIST 800-53 Rev4" else rev5_controls,
                regscale_id=regscale_ssp_id,
            )
        else:
            logger.warning(
                f"System framework {imp.get('controlSet')} \
                           for system {system_id} is not supported"
            )
            continue

        if not results:
            logger.warning(f"No controls found for system id: {system_id}")
            continue

        # Build the controls
        control_implementations = build_implementations(results=results, csam_id=system_id, regscale_id=regscale_ssp_id)

        # Save the control implementations
        for index in track(
            range(len(control_implementations)),
            description=f"Saving {len(control_implementations)} control implementations...",
        ):
            control_implementation = control_implementations[index]
            control_implementation.create() if control_implementation.id == 0 else control_implementation.save()


def import_csam_poams():
    # Check Custom Fields
    custom_fields_basic_map = FormFieldValue.check_custom_fields(
        fields_list=[FISMA_FIELD_NAME, CSAM_FIELD_NAME], module_name="securityplans", tab_name=SSP_BASIC_TAB
    )

    # Get the SSPs
    ssp_map = retrieve_ssps_custom_form_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    # Get a list of users and create a map to id
    users = User.get_all()
    user_map = {user.userName: user.id for user in users}

    # Grab the data from CSAM
    app = Application()
    csam_token = app.config.get("csamToken")
    csam_url = app.config.get("csamURL")
    results = retrieve_from_csam(
        csam_token=csam_token, csam_url=csam_url, csam_endpoint="/CSAM/api/v1/reports/POAM_Details_Report_CBP"
    )

    # Parse the results
    poam_list = []
    for index in track(
        range(len(results)),
        description=f"Importing {len(results)} POA&Ms...",
    ):
        result = results[index]

        # Get the existing SSP:
        ssp_id = ssp_map.get(str(result[SYSTEM_ID]))
        if not ssp_id:
            logger.error(
                f"A RegScale Security Plan does not exist for CSAM id: {result[SYSTEM_ID]}\
             create or import the Security Plan prior to importing POA&Ms"
            )
            continue

        # Check if the POAM exists:
        existing_issue = Issue.find_by_other_identifier(result[POAM_ID])
        if existing_issue:
            new_issue = existing_issue
        else:
            new_issue = Issue()

        # Update the issue
        new_issue.isPoam = True
        new_issue.parentId = ssp_id
        new_issue.parentModule = "securityplans"
        new_issue.otherIdentifier = result[POAM_ID]
        new_issue.title = result["POAM Title"]
        new_issue.affectedControls = result["Controls"]
        new_issue.securityPlanId = ssp_id
        new_issue.identification = "Vulnerability Assessment"
        new_issue.description = result["Detailed Weakness Description"]
        new_issue.poamComments = f"{result['Weakness Comments']}\n \
            {result['POA&M Delayed Comments']}\n \
            {result['POA&M Comments']}"
        new_issue.dateFirstDetected = safe_date_str(result["Create Date"])
        new_issue.dueDate = safe_date_str(result["Planned Finish Date"])
        # Need to convert cost to a int
        # new_issue.costEstimate = result['Cost']
        new_issue.issueOwnerId = (
            user_map.get(result["Email"]) if user_map.get(result["Email"]) else RegScaleModel.get_user_id()
        )
        # Update with IssueSeverity String
        new_issue.severityLevel = result["Severity"]
        # Update with IssueStatus String
        new_issue.status = result["Status"]

        poam_list.append(new_issue)

    for index in track(
        range(len(poam_list)),
        description=f"Updating RegScale with {len(poam_list)} POA&Ms...",
    ):
        poam = poam_list[index]
        if poam.id == 0:
            poam.create()
        else:
            poam.save()
    logger.info(f"Added or updated {len(poam_list)} POA&Ms in RegScale")


def import_csam_pocs(import_ids: Optional[List[int]] = None):
    """
    Import the Points of Contact from CSAM
    Into RegScale
    """
    custom_fields_system_list = [
        "Certifying Official",
        "Alternate Information System Security Manager",
        "Alternate Information System Security Officer",
    ]
    # Check Custom Fields exist
    custom_fields_system_map = FormFieldValue.check_custom_fields(
        custom_fields_system_list, "securityplans", SSP_SYSTEM_TAB
    )

    # Get existing ssps by CSAM Id
    custom_fields_basic_map = FormFieldValue.check_custom_fields([CSAM_FIELD_NAME], "securityplans", SSP_BASIC_TAB)
    ssp_map = retrieve_custom_form_ssp_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    plans = import_ids if import_ids else list(ssp_map.keys())

    # Get a list of users and create a map to id
    users = User.get_all()
    user_map = {user.userName: user.id for user in users}

    # TO DO... Add the rest of the logic
    # Delete these lines: Added to shut up sonarqube
    logger.debug(f"Custom Fields Map: {custom_fields_system_map}, User Map: {user_map}")
    logger.debug(f"SSP Map: {ssp_map}, Plans: {plans}")


def import_csam_privacy_info(import_ids: Optional[List[int]] = None):
    """
    Import the Privacy Info from CSAM
    Into RegScale
    """
    custom_fields_privacy_list = ["PIA Date", "PTA Date", "SORN Date", "SORN Id"]

    # Check for custom fields
    custom_fields_privacy_map = FormFieldValue.check_custom_fields(
        custom_fields_privacy_list, "securityplans", SSP_PRIVACY_TAB
    )

    # Grab the data from CSAM
    app = Application()
    csam_token = app.config.get("csamToken")
    csam_url = app.config.get("csamURL")

    # Get existing ssps by CSAM Id
    custom_fields_basic_map = FormFieldValue.check_custom_fields([CSAM_FIELD_NAME], "securityplans", SSP_BASIC_TAB)
    ssp_map = retrieve_custom_form_ssp_map(
        tab_name=SSP_BASIC_TAB, field_form_id=custom_fields_basic_map[CSAM_FIELD_NAME]
    )

    plans = import_ids if import_ids else list(ssp_map.keys())

    for regscale_ssp_id in plans:
        system_id = ssp_map.get(regscale_ssp_id)

        # Get Privacy Status
        privacy_status = retrieve_from_csam(
            csam_token=csam_token,
            csam_url=csam_url,
            csam_endpoint=f"/CSAM/api/v1/systems/{system_id}/privacy",
        )
        pia_date = privacy_status.get("privacyImpactAssessmentDateCompleted")
        pta_date = privacy_status.get("privacyThresholdAnalysisDateCompleted")

        # Get SORN Status
        sorn_statuses = retrieve_from_csam(
            csam_token=csam_token,
            csam_url=csam_url,
            csam_endpoint=f"/CSAM/api/v1/systems/{system_id}/sorn",
        )
        sorn_date = 0
        sorn_id = ""
        for sorn_status in sorn_statuses:
            if date_obj(sorn_status.get("publishedDate")) > date_obj(sorn_date):
                sorn_date = sorn_status.get("publishedDate")
                sorn_id = sorn_status.get("systemOfRecordsNoticeId").strip()

        # Set the records
        record = {"pia_date": pia_date, "pta_date": pta_date, "sorn_date": sorn_date, "sorn_id": sorn_id}
        save_privacy_records(regscale_id=regscale_ssp_id, custom_fields_map=custom_fields_privacy_map, record=record)


def save_privacy_records(regscale_id: int, custom_fields_map: dict, record: dict):
    privacy_fields = []
    if record.get("pia_date"):
        privacy_fields.append(
            {
                "record_id": regscale_id,
                "form_field_id": custom_fields_map["PIA Date"],
                "field_value": format_to_regscale_iso(record.get("pia_date")),
            }
        )
    if record.get("pta_date"):
        privacy_fields.append(
            {
                "record_id": regscale_id,
                "form_field_id": custom_fields_map["PTA Date"],
                "field_value": format_to_regscale_iso(record.get("pta_date")),
            }
        )
    if record.get("sorn_date"):
        privacy_fields.append(
            {
                "record_id": regscale_id,
                "form_field_id": custom_fields_map["SORN Date"],
                "field_value": format_to_regscale_iso(record.get("sorn_date")),
            }
        )
    if record.get("sorn_id"):
        privacy_fields.append(
            {
                "record_id": regscale_id,
                "form_field_id": custom_fields_map["SORN Id"],
                "field_value": record.get("sorn_id"),
            }
        )
    if len(privacy_fields) > 0:
        FormFieldValue.save_custom_fields(privacy_fields)


def import_csam_status():
    """
    Import the Status Info from CSAM
    Into RegScale
    """
    # TO DO... Add the rest of the logic
    pass


def import_csam_inheritance(import_ids: Optional[List[int]] = None):
    """
    Import control inheritance from CSAM

    :param list import_ids: List of SSPs to import
    :return: None
    """

    # Get list of existing SSPs in RegScale
    existing_ssps = SecurityPlan.get_ssp_list()
    ssp_map = {ssp["title"]: ssp["id"] for ssp in existing_ssps}

    if not import_ids:
        import_ids = [ssp["id"] for ssp in existing_ssps]

    # Get Inheritance data from CSAM
    app = Application()
    for index in track(
        range(len(import_ids)),
        description=f"Importing inheritance for {len(import_ids)} Systems...",
    ):
        ssp = SecurityPlan.get_object(object_id=import_ids[index])
        linked_ssps = []
        # Get the inheritance data from CSAM

        inheritances = retrieve_from_csam(
            csam_url=app.config.get("csamURL"),
            csam_token=app.config.get("csamToken"),
            csam_endpoint=f"/CSAM/api/v1/systems/{ssp.otherIdentifier}/inheritedcontrols",
        )
        if not inheritances:
            logger.debug(f"No inheritance data found for SSP {ssp.systemName} (ID: {ssp.id})")
            continue
        # Process each inheritance record
        imp_map = ControlImplementation.get_control_label_map_by_plan(plan_id=ssp.id)

        process_inheritances(
            inheritances=inheritances, ssp=ssp, ssp_map=ssp_map, imp_map=imp_map, linked_ssps=linked_ssps
        )


def retrieve_from_csam(csam_url: str, csam_token: str, csam_endpoint: str) -> list:
    """
    Connect to CSAM and retrieve data

    :param str csam_url: URL of CSAM System
    :param str csam_token: Bearer Token
    :param str csam_endpoint: API Endpoint
    :return: List of dict objects
    :return_type: list
    """
    logger.debug("Retrieving data from CSAM")
    reg_api = Api()
    if "Bearer" not in csam_token:
        csam_token = f"Bearer {csam_token}"

    url = urljoin(csam_url, csam_endpoint)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": csam_token,
    }

    issue_response = reg_api.get(url=url, headers=headers)
    if not issue_response or issue_response.status_code in [204, 404]:
        logger.warning(f"Call to {url} Returned error: {issue_response.text}")
        return []
    if issue_response and issue_response.ok:
        return issue_response.json()

    return []


def retrieve_ssps_custom_form_map(tab_name: str, field_form_id: int) -> dict:
    """
    Retreives a list of the SSPs in RegScale
    Returns a map of Custom Field Value: RegScale Id

    :param str tab_name: The RegScale tab name where the custom field is located
    :param int field_form_id: The RegScale Form Id of custom field
    :param int tab_id: The RegScale tab id
    :return: dictionary of FieldForm Id: regscale_ssp_id
    :return_type: dict
    """
    tab = Module.get_tab_by_name(regscale_module_name="securityplans", regscale_tab_name=tab_name)

    field_form_map = {}
    ssps = SecurityPlan.get_ssp_list()
    form_values = []
    for ssp in ssps:
        form_values = FormFieldValue.get_field_values(
            record_id=ssp["id"], module_name=SecurityPlan.get_module_slug(), form_id=tab.id
        )

        for form in form_values:
            if form.formFieldId == field_form_id and form.data:
                field_form_map[form.data] = ssp["id"]
        form_values = []
    return field_form_map


def retrieve_custom_form_ssp_map(tab_name: str, field_form_id: int) -> dict:
    """
    Retreives a list of the SSPs in RegScale
    Returns a map of RegScale ID: Custom Field Value

    :param str tab_name: The RegScale tab name where the custom field is located
    :param int field_form_id: The RegScale Form Id of custom field
    :param int tab_id: The RegScale tab id
    :return: dictionary of FieldForm Id: regscale_ssp_id
    :return_type: dict
    """
    tab = Module.get_tab_by_name(regscale_module_name="securityplans", regscale_tab_name=tab_name)

    field_form_map = {}
    ssps = SecurityPlan.get_ssp_list()
    form_values = []
    for ssp in ssps:
        form_values = FormFieldValue.get_field_values(
            record_id=ssp["id"], module_name=SecurityPlan.get_module_slug(), form_id=tab.id
        )
        for form in form_values:
            if form.formFieldId == field_form_id and form.data:
                field_form_map[ssp["id"]] = form.data
        form_values = []
    return field_form_map


def update_ssp_general(ssp: SecurityPlan, record: dict, org_map: dict) -> SecurityPlan:
    """
    Update or Create the SSP Record
    Based upon the values in Record

    :param SecurityPlan ssp: RegScale Security Plan
    :param dict record: record of values
    :param dict org_map: map of org names to orgId
    :return: SecurityPlan Object
    :return_type: SecurityPlan
    """

    ssp.otherIdentifier = record["id"]
    ssp.overallCategorization = record["categorization"]
    ssp.confidentiality = record["categorization"]
    ssp.integrity = record["categorization"]
    ssp.availability = record["categorization"]
    ssp.status = record["operationalStatus"]
    ssp.systemType = record["systemType"]
    ssp.description = record["purpose"]
    if record["organization"] and org_map.get(record["organization"]):
        ssp.orgId = org_map.get(record["organization"])

    if ssp.id == 0:
        new_ssp = ssp.create()
    else:
        new_ssp = ssp.save()

    return new_ssp


def save_ssp_front_matter(
    results: list, ssp_map: dict, custom_fields_basic_map: dict, custom_fields_financial_map: dict, org_map: dict
) -> list:
    """
    Save the SSP data from the /systems endpoint

    :param list results: list of results from CSAM
    :param dict ssp_map: map of existing SSPs in RegScale
    :param dict custom_fields_basic_map: map of custom fields in RegScale
    :param dict custom_fields_financial_map: map of custom fields in RegScale
    :param dict org_map: map of existing orgs in RegScale
    :return: list of updated SSPs
    :return_type: List[SecurityPlan]
    """
    updated_ssps = []
    for index in track(
        range(len(results)),
        description=f"Importing {len(results)} SSP front matter...",
    ):
        result = results[index]

        # Get the existing SSP:
        ssp_id = ssp_map.get(result["externalId"])
        if ssp_id:
            ssp = SecurityPlan.get_object(ssp_id)
        else:
            ssp = SecurityPlan(systemName=result["name"])
        # Update the SSP
        ssp = update_ssp_general(ssp, result, org_map)

        # Grab the Custom Fields
        field_values = set_front_matter_fields(
            ssp=ssp,
            result=result,
            custom_fields_basic_map=custom_fields_basic_map,
            custom_fields_financial_map=custom_fields_financial_map,
        )

        # System Custom Fields
        FormFieldValue.save_custom_fields(field_values)
        updated_ssps.append(ssp)
    logger.info(f"Updated {len(results)} Security Plans Front Matter")
    return updated_ssps


def update_ssp_agency_details(ssps: list, csam_token: str, csam_url: str, custom_fields_basic_map: dict) -> list:
    """
    Update the Agency Details of the SSPs
    This requires a call to the /system/{id}/agencydefineddataitems
    endpoint

    :param list ssps: list of RegScale SSPs
    :param str csam_token: CSAM Bearer Token
    :param str csam_url: CSAM URL
    :param dict custom_fields_basic_map: map of custom fields in RegScale
    :return: list of updated SSPs
    :return_type: List[SecurityPlan]
    """
    updated_ssps = []
    if len(ssps) == 0:
        return updated_ssps
    for index in track(
        range(len(ssps)),
        description=f"Importing {len(ssps)} SSP agency details...",
    ):
        ssp = ssps[index]
        csam_id = ssp.otherIdentifier
        if not csam_id:
            logger.error(f"Could not find CSAM ID for SSP {ssp.systemName} id: {ssp.id}")
            continue
        else:
            updated_ssps.append(ssp)

        result = retrieve_from_csam(
            csam_token=csam_token,
            csam_url=csam_url,
            csam_endpoint=f"/CSAM/api/v1/systems/{csam_id}/agencydefineddataitems",
        )
        if len(result) == 0:
            logger.error(
                f"Could not retrieve details for CSAM ID {csam_id}. RegScale SSP: Name: {ssp.systemName} id: {ssp.id}"
            )
            continue
        # Get the custom fields
        set_agency_details(result, ssp, custom_fields_basic_map)

    logger.info(f"Updated {len(updated_ssps)} Security Plans with Agency Details")
    return updated_ssps


def set_agency_details(result: list, ssp: SecurityPlan, custom_fields_basic_map: dict):
    """
    Loop through results of agencydefineddataitems
    and set the custom fields in RegScale

    :param list result: list of dict objects from CSAM
    :param SecurityPlan ssp: RegScale Security Plan
    :param dict custom_fields_basic_map: map of custom field names to ids
    """
    field_values = []
    # Update the fields we need
    for item in result:
        if item.get("attributeName") == "High Value Asset":
            ssp.hva = True if item.get("value") == "1" else False

        # Binary Values
        if item.get("attributeName") in [
            "External Web Interface",
            "CFO Designation",
            "Law Enforcement Sensitive",
            "AI/ML Components",
        ]:
            field_values.append(set_binary_fields(item, ssp, custom_fields_basic_map))

        if item.get("attributeName") == "Cloud System":
            ssp = set_cloud_system(ssp, item)

        if item.get("attributeName") == "Cloud Service Model":
            ssp = set_cloud_service(ssp, item)

        if item.get("attributeName") == "HVA Identifier":
            field_values.append(set_custom_fields(item, ssp, custom_fields_basic_map))

    # Save the SSP & Custom Fields
    ssp.save()
    if len(field_values) > 0:
        FormFieldValue.save_custom_fields(field_values)


def set_front_matter_fields(
    ssp: SecurityPlan, result: dict, custom_fields_basic_map: dict, custom_fields_financial_map: dict
) -> list:
    """
    parse the front matter custom fields
    and return a list of field values to be saved

    :param SecurityPlan ssp: RegScale Security Plan object
    :param dict result: response from CSAM
    :param dict custom_fields_basic_map: map of basic custom fields
    :param dict custom_fields_financial_map: map of financial custom fields
    :return: list of dictionaries with field values
    :return_type: list
    """
    field_values = []
    # FISMA ID
    field_values.append(
        {
            "record_id": ssp.id,
            "form_field_id": custom_fields_basic_map[FISMA_FIELD_NAME],
            "field_value": str(result["externalId"]),
        }
    )
    # CSAM ID
    field_values.append(
        {
            "record_id": ssp.id,
            "form_field_id": custom_fields_basic_map[CSAM_FIELD_NAME],
            "field_value": str(result["id"]),
        }
    )
    # Basic Tab
    for key in result.keys():
        if key in custom_fields_basic_map.keys() and key not in [CSAM_FIELD_NAME, FISMA_FIELD_NAME]:
            if isinstance(result.get(key), bool):
                field_values.append(
                    {
                        "record_id": ssp.id,
                        "form_field_id": custom_fields_basic_map[key],
                        "field_value": "Yes" if result.get(key) else "No",
                    }
                )
            else:
                field_values.append(
                    {
                        "record_id": ssp.id,
                        "form_field_id": custom_fields_basic_map[key],
                        "field_value": str(result.get(key)),
                    }
                )

    # Financial Info Tab
    # custom fields and csam values match
    for key in result.keys():
        if key in custom_fields_financial_map.keys():
            field_values.append(
                {
                    "record_id": ssp.id,
                    "form_field_id": custom_fields_financial_map[key],
                    "field_value": str(result.get(key)),
                }
            )
    return field_values


def set_cloud_system(ssp: SecurityPlan, item: dict) -> SecurityPlan:
    """
    Set the cloud system values in the SSP
    :param SeucrityPlan ssp: RegScale Security Plan
    :param dict item: record from CSAM
    :return: SecurityPlan object with updated cloud system values
    :return_type: SecurityPlan
    """
    ssp.bDeployPublic = True if item.get("value") == "Public" else False
    ssp.bDeployPrivate = True if item.get("value") == "Private" else False
    ssp.bDeployHybrid = True if item.get("value") == "Hybrid" else False
    ssp.bDeployGov = True if item.get("value") == "GovCloud" else False
    ssp.bDeployOther = True if item.get("value") == "Community" else False
    if ssp.bDeployHybrid or ssp.bDeployOther:
        ssp.deployOtherRemarks = "Hybrid or Community"

    return ssp


def set_cloud_service(ssp: SecurityPlan, item: dict) -> SecurityPlan:
    """
    Set the cloud service model values in the SSP

    :param SecurityPlan ssp: RegScale Security Plan
    :param dict item: record from CSAM
    :return: Updated SecurityPlan object
    :return_type: SecurityPlan
    """
    ssp.bModelIaaS = True if "IaaS" in item.get("value") else False
    ssp.bModelPaaS = True if "PaaS" in item.get("value") else False
    ssp.bModelSaaS = True if "SaaS" in item.get("value") else False
    return ssp


def set_binary_fields(item: dict, ssp: SecurityPlan, custom_fields_map: dict) -> dict:
    return {
        "record_id": ssp.id,
        "form_field_id": custom_fields_map[item.get("attributeName")],
        "field_value": "Yes" if (item.get("value")) == "1" else "No",
    }


def set_custom_fields(item: dict, ssp: SecurityPlan, custom_fields_map: dict) -> dict:
    """
    Set the custom fields for the SSP

    :param dict item: record from CSAM
    :param SecurityPlan ssp: RegScale Security Plan
    :param dict custom_fields_map: map of custom fields in RegScale
    :return: dictionary of field values to be saved
    :return_type: dict
    """
    return {
        "record_id": ssp.id,
        "form_field_id": custom_fields_map[item.get("attributeName")],
        "field_value": str(item.get("value")),
    }


def get_catalogs() -> Tuple[Optional[int], Optional[int]]:
    """
    Get the catalog ids for NIST SP 800-53 Rev 5 and Rev 4

    :return: tuple of catalog ids
    :return_type: Tuple[Optional[int], Optional[int]]
    """
    # Find the Catalogs
    rev5_catalog = Catalog.find_by_guid("b0c40faa-fda4-4ed3-83df-368908d9e9b2")  # NIST SP 800-53 Rev 5
    rev5_catalog_id = rev5_catalog.id if rev5_catalog else None
    rev4_catalog = Catalog.find_by_guid("02158108-e491-49de-b9a8-3cb1cb8197dd")  # NIST SP 800-53 Rev 4
    rev4_catalog_id = rev4_catalog.id if rev4_catalog else None

    return rev5_catalog_id, rev4_catalog_id


def build_implementations(results: list, csam_id: str, regscale_id: int) -> list:
    """
    Build out the control implementations
    from the results returned from CSAM

    :param list results: records from CSAM
    :param int csam_id: CSAM System Id
    :param int regscale_id: RegScale SSP Id
    :return: list of ControlImplementation objects
    :return_type: list
    """
    existing_implementations = ControlImplementation.get_list_by_parent(
        regscale_id=regscale_id, regscale_module="securityplans"
    )
    implementations_map = {normalize_controlid(impl["controlId"]): impl["id"] for impl in existing_implementations}
    control_implementations = []
    # Loop through the results and create or update the controls
    for index in track(
        range(len(results)),
        description=f"Importing {len(results)} controls for system id: {csam_id}...",
    ):
        result = results[index]
        # Debug
        imp_id = (
            implementations_map.get(normalize_controlid(result["controlId"]))
            if normalize_controlid(result["controlId"]) in implementations_map
            else 0
        )

        control_implementations.append(
            ControlImplementation(
                id=imp_id,
                status=(
                    "Fully Implemented" if result["statedImplementationStatus"] == "Implemented" else "Not Implemented"
                ),  # Implemented
                responsibility=(
                    result["applicability"]
                    if result["applicability"] in ["Hybrid", "Inherited"]
                    else "Provider (System Specific)"
                ),  # Hybrid, Applicable
                controlSource="Baseline",
                implementation=result["implementationStatement"],
                controlID=result["controlID"],
                parentId=result["securityPlanId"],
                parentModule="securityplans",
            )
        )
    return control_implementations


def retrieve_controls(csam_token: str, csam_url: str, csam_id: int, controls: list, regscale_id: int) -> list:
    """
    Takes a system id and list of controls
    returns a list of implmentations for
    that system id and framework

    :param str csam_token: access token for CSAM
    :param str csam_url: url for CSAM API
    :param int system_id: CSAM system id
    :param str framework: Framework name
    :param list controls: list of possible controls
    :param int regscale_id: RegScale SSP Id
    :return: list of control implementations
    :return_type: list
    """
    imps = []
    # Loop through the controls and get the implementations
    for index in track(
        range(len(controls)),
        description=f"Retrieving implementations for system id: {csam_id}...",
    ):
        control = controls[index]
        implementations = retrieve_from_csam(
            csam_token=csam_token,
            csam_url=csam_url,
            csam_endpoint=f"/CSAM/api/v1/systems/{csam_id}/controls/{control.controlId}",
        )

        if len(implementations) == 0:
            logger.debug(f"No implementations found for control {control.controlId} in system id: {csam_id}")
            continue

        # Add the RegScale SSP Id and controlID to the implementation
        for impl in implementations:
            if "NotApplicable" in impl["applicability"]:
                continue

            impl["securityPlanId"] = regscale_id
            impl["controlID"] = control.id
            imps.append(impl)
    return imps


def set_inheritable(regscale_id: int):
    """
    Given a RegScale SSP Id
    Sets the inheritable flag on all control implementations

    :param int regscale_id: id of Security Plan
    :return: None
    """

    # Get list of existing controlimplementations
    implementations = ControlImplementation.get_list_by_parent(regscale_id=regscale_id, regscale_module="securityplans")

    for index in track(
        range(len(implementations)),
        description="Setting controls Inheritable...",
    ):
        implementation = implementations[index]
        imp = ControlImplementation.get_object(object_id=implementation["id"])
        imp.inheritable = True
        imp.save()


def process_inheritances(
    inheritances: List[Dict[str, Any]],
    ssp: SecurityPlan,
    ssp_map: Dict[str, int],
    imp_map: Dict[str, int],
    linked_ssps: List[SecurityPlan],
):
    for inheritance in inheritances:
        # Check if the control exists in plan
        control_id = normalize_controlid(inheritance.get("controlId"))
        if control_id not in imp_map:
            logger.debug(f"Control {control_id} not found in RegScale for SSP {ssp.systemName} (ID: {ssp.id})")
            continue

        # Find the baseControl in RegScale
        # Find the SSP
        base_ssp = ssp_map.get(inheritance.get("offeringSystemName"))
        if not base_ssp:
            logger.debug(f"Base SSP {inheritance.get('offeringSystemName')} not found in RegScale, skipping")
            continue

        base_control_map = ControlImplementation.get_control_label_map_by_plan(plan_id=base_ssp)
        base_control_id = base_control_map.get(normalize_controlid(inheritance.get("controlId")))

        # Create or update the inheritance record
        if inheritance.get("isInherited") is False:
            continue

        # Add the parent if not already linked
        if base_ssp not in linked_ssps:
            linked_ssps.append(base_ssp)

        # Create the records
        create_inheritance(
            parent_id=ssp.id,
            parent_module="securityplans",
            hybrid=inheritance.get("isHybrid", True),
            base_id=base_ssp,
            control_id=imp_map[control_id],
            base_control_id=base_control_id,
        )

    # Create the Inheritance Record(s)
    for inheritance_ssp in linked_ssps:
        create_inheritance_linage(
            parent_id=ssp.id,
            parent_module="securityplans",
            base_id=inheritance_ssp,
        )


def create_inheritance(
    parent_id: int, parent_module: str, base_id: int, hybrid: bool, control_id: int, base_control_id: int
):
    """
    Creates the records for inheritance

    :param int parent_id: Id of inheriting record
    :param str parent_module: Module of inheriting record
    :param int base_id: Id of inherited record
    :param bool hybrid: Is the control hybrid
    :param int control_id: Id of inheriting control
    :param int base_control_id: Id of inherited control
    :return: None
    """

    # Update the control implementation
    control_impl = ControlImplementation.get_object(object_id=control_id)
    if control_impl:
        control_impl.bInherited = True
        control_impl.responsibility = "Hybrid" if hybrid else "Inherited"
        control_impl.inheritedControlId = base_control_id
        control_impl.inheritedSecurityPlanId = base_id
        control_impl.save()

    # Check if the Inherited Control already exists
    existing = InheritedControl.get_all_by_control(control_id=control_id)
    for exists in existing:
        if exists["inheritedControlId"] == base_control_id:
            return

    InheritedControl(
        parentId=parent_id, parentModule=parent_module, baseControlId=control_id, inheritedControlId=base_control_id
    ).create()


def create_inheritance_linage(parent_id: int, parent_module: str, base_id: int):
    """
    Creates a RegScale Inheritance Record

    :param int parent_id: Id of inheriting record
    :param str parent_module: Module of inheriting record
    :param int base_control_id: Id of inherited control
    :return: None
    """
    # Check if the Inheritance already exists
    existing = Inheritance.get_all_by_parent(parent_id=parent_id, parent_module=parent_module)
    for exists in existing:
        if exists.planId == base_id:
            return

    # Update Lineage (no way to update.. only create)
    Inheritance(recordId=parent_id, recordModule=parent_module, planId=base_id).create()
