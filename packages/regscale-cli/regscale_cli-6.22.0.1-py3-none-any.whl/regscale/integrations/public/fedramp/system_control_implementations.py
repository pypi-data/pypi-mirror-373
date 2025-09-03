#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""standard python imports"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from json import JSONDecodeError
from typing import Any, List

import requests
from lxml.etree import Element
from packaging.version import Version

from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.integrations.public.fedramp.fedramp_traversal import FedrampTraversal
from regscale.models.regscale_models.control_implementation import ControlImplementation
from regscale.models.regscale_models.implementation_objective import ImplementationObjective
from regscale.models.regscale_models.implementation_option import ImplementationOptionDeprecated
from regscale.models.regscale_models.security_plan import SecurityPlan
from regscale.utils.version import RegscaleVersion

logger = logging.getLogger("regscale")

FULLY_IMPLEMENTED = "Fully Implemented"
NOT_IMPLEMENTED = "Not Implemented"


def get_parts_list(ele: Any) -> list[dict]:
    """
    Get the parts list

    :param Any ele: The element
    :return: A list of parts
    :rtype: list[dict]
    """
    oscal_component = ".//oscal:by-component"
    parts_list = []
    nsmap = {"oscal": "http://csrc.nist.gov/ns/oscal/1.0"}
    statements = ele.xpath("//*[contains(@statement-id, 'smt')]", namespaces=nsmap)
    parameters = ele.xpath("//*[contains(@param-id, 'prm') or contains(@param-id, 'odp')]", namespaces=nsmap)
    objectives = ele.xpath("//*[contains(@statement-id, 'obj')]", namespaces=nsmap)

    for statement in statements:
        parts = {}
        component_uuid = statement.xpath(oscal_component, namespaces=nsmap)[0].attrib["component-uuid"]
        parts["part_id"] = statement.attrib["statement-id"]
        parts["uuid"] = statement.attrib["uuid"]
        if component_uuid:
            parts["component_uuid"] = component_uuid
        p_texts = statement.xpath(
            ".//oscal:by-component/oscal:description/oscal:p/text()",
            namespaces=nsmap,
        )
        parts["text"] = p_texts
        if statement.attrib["statement-id"] not in {part["part_id"] for part in parts_list}:
            parts_list.append(parts)

    for objective in objectives:
        parts = {}
        parts["part_id"] = objective.attrib["statement-id"]
        comp = objective.xpath(oscal_component, namespaces=nsmap)
        if comp:
            component_uuid = comp[0].attrib["component-uuid"]
        b_texts = objective.xpath(
            ".//oscal:by-component/oscal:description/oscal:p/text()",
            namespaces=nsmap,
        )
        parts["text"] = b_texts
        if component_uuid:
            parts["component_uuid"] = component_uuid
        if objective.attrib["statement-id"] not in {part["part_id"] for part in parts_list}:
            parts_list.append(parts)

    for parameter in parameters:
        parts = {}
        parts["part_id"] = parameter.attrib["param-id"]
        comp = parameter.xpath(oscal_component, namespaces=nsmap)
        if comp:
            component_uuid = comp[0].attrib["component-uuid"]
        b_texts = parameter.xpath(
            ".//oscal:set-parameter/value/text()",
            namespaces=nsmap,
        )
        b_texts = parameter.xpath(
            ".//oscal:value/text()",
            namespaces=nsmap,
        )
        if b_texts:
            parts["text"] = b_texts.pop()
        if component_uuid:
            parts["component_uuid"] = component_uuid
        if parameter.attrib["param-id"] not in {part["part_id"] for part in parts_list}:
            parts_list.append(parts)
    return parts_list


def get_maps() -> tuple:
    """
    Get the status and responsibility maps

    :return: A tuple of status and responsibility maps
    :rtype: tuple
    """
    status_map = {
        FULLY_IMPLEMENTED: "Implemented",
        "Partially Implemented": "Partially Implemented",
        "Not Applicable": "Not Applicable",
        NOT_IMPLEMENTED: NOT_IMPLEMENTED,
        "Planned": "Planned",
    }
    responsibility_map = {
        "Provider": "Service Provider Corporate",
        "Provider (System Specific)": "Service Provider System Specific",
        "Customer": "Provided by Customer (Customer System Specific)",
        "Hybrid": "Service Provider Hybrid (Corporate and System Specific)",
        "Customer Configured": "Configured by Customer (Customer System Specific)",
        "Shared": "Shared (Service Provider and Customer Responsibility)",
        "Inherited": "Inherited from pre-existing FedRAMP Authorization",
    }

    return status_map, responsibility_map


def fetch_implementations(trv: FedrampTraversal, root: Element, ssp: SecurityPlan) -> list:
    """
    Fetch the control implementations for the provided SSP in RegScale

    :param FedrampTraversal trv: FedrampTraversal instance
    :param Element root: The root element of the OSCAL document
    :param SecurityPlan ssp: RegScale security plan object
    :return: List of control implementations
    :rtype: list
    """
    app = trv.api.app
    api = trv.api
    # Compliance settings groups are too inconsistent to auto map, so we need to manually map them
    status_map, responsibility_map = get_maps()
    ns = {"ns1": "http://csrc.nist.gov/ns/oscal/1.0"}
    parts = []
    imps = []
    reqs = root.xpath("//ns1:implemented-requirement", namespaces=ns)
    ssp.parentId = trv.catalogue_id
    ssp.parentModule = "catalogues"
    cat_id = ssp.parentId
    detail = {}
    trv.log_info(
        {
            "model_layer": "System Control Implementation",
            "record_type": "Control Implementation",
            "event_msg": "Pulling Catalog details.",
        }
    )

    detail_res = api.get(url=app.config["domain"] + f"/api/catalogues/getCatalogWithAllDetails/{cat_id}")
    if detail_res.ok:
        try:
            detail = detail_res.json()
        except JSONDecodeError as jex:
            logger.error(jex)
            return
    control_objectives = detail["objectives"] if "objectives" in detail else []
    options = detail["options"] if "options" in detail else []
    existing_parameters = detail["parameters"] if "parameters" in detail else []
    existing_controls = detail["controls"] if "controls" in detail else []
    # Build options if they do not exist
    updated_options = build_options(app=app, existing_options=options, control_objectives=control_objectives)
    options.extend(updated_options)

    new_options = post_options(trv, updated_options)
    options.extend(new_options)
    # TODO: Pull the options for just the control objectives we are working with.
    # Get Parts data, mapped to a compoment id.
    uuid = ""
    for req in reqs:
        for name, value in req.attrib.items():
            if name == "uuid":
                uuid = value
            if name == "control-id":
                logger.debug(f"Property: {name}, Value: {value}")
                if ssp.parentModule == "catalogues":
                    logger.info("Building implementation: %s", value)

                    # This try catch is tied to modification to catalogs object returned by above API call
                    # The otherId field is to be added to new OSCAL catalogs which will be migrated for existing customers.
                    # If otherId exists use it to match to control otherwise use original controlId
                    # Handle case where otherId does not exist in catalog object and do not throw an error
                    # if otherid exists in catalog object make sure it has something in it before matching
                    # this case may exist while new catalogs are being migrated to for customers
                    matching_controls = [
                        control for control in existing_controls if control.get("otherId", "") == value
                    ]
                    if not matching_controls:
                        matching_controls = [
                            control for control in existing_controls if control.get("controlId", "") == value
                        ]

                    control = matching_controls[0] if matching_controls else None

                    if control is None:
                        trv.log_error(
                            {
                                "record_type": "System Control Implementation",
                                "event_msg": f"Failed to locate control {value} in the selected profile.",
                                "missing_element": f"Control {value}",
                                "model_layer": "System Control Implementation",
                            }
                        )
                        logger.warning("Unable to find a control, do you have a catalog?")
                        break

                    implementation = ControlImplementation.from_oscal_element(app=app, obj=req, control=control)
                    implementation.parentId = ssp.id
                    implementation.uuid = uuid
                    implementation.parentModule = "securityplans"

                    implementation.controlOwnerId = app.config["userId"]

                    # do a version check to use new compliance settings
                    regscale_version = RegscaleVersion.get_platform_version()
                    if len(regscale_version) >= 10 or Version(regscale_version) >= Version("6.13.0.0"):
                        implementation.status = status_map.get(implementation.status.value)
                        implementation.responsibility = responsibility_map.get(implementation.responsibility.value)
                    imps.append(implementation)
                    if control is None:
                        logger.error("Unable to locate the control in RegScale.")

        parts.extend(get_parts_list(req))

    logger.info("Loading control implementations to RegScale")
    num_successful_post = 0
    num_failed_post = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        post_futures = {
            executor.submit(ControlImplementation.post_implementation, app=app, implementation=imp): imp for imp in imps
        }

        for future in as_completed(post_futures):
            imp = post_futures[future]
            try:
                data = future.result()
                if data is not None:
                    num_successful_post += 1
            except Exception as ex:
                logger.warning(f"An error occurred while posting implementation {imp}: {ex}")
                num_failed_post += 1
            else:
                logger.info(f"Finished posting Implementation {num_successful_post} to RegScale")

    trv.log_info(
        {
            "model_layer": "System Control Implementation",
            "record_type": "Control Implementation",
            "event_msg": f"Finished loading {num_successful_post} Control Implementations (Failed: {num_failed_post})",
        }
    )

    logger.info("Processing Control Parts...")
    imps = ControlImplementation.fetch_existing_implementations(
        app=app, regscale_parent_id=ssp.id, regscale_module="securityplans"
    )

    process_parts(
        trv,
        control_objectives,
        existing_parameters,
        parts,
        imps,
        options,
    )

    # Update implementation options with implementation objectives.
    return imps


def process_parts(
    trv: FedrampTraversal,
    control_objectives: List[dict],
    existing_parameters: List[dict],
    parts: List[dict],
    imps: List[dict],
    single_system: bool = True,
):
    """
    Process parts of the implementation

    :param FedrampTraversal trv: FedrampTraversal instance
    :param List[dict] control_objectives: A list of control objectives
    :param List[dict] existing_parameters: A list of existing parameters
    :param List[dict] parts: A list of parts
    :param List[dict] imps: A list of implementations
    :param bool single_system: A flag to indicate if the system is a single system, defaults to True
    """
    app = trv.api.app
    api = trv.api
    config = app.config
    implementation_objectives = []
    all_params = []

    for imp in imps:
        status = imp["status"]
        imp_id = imp["id"]

        logger.info(f"Loading parts for {imp['controlName']}...")

        part_notes = [
            part
            for part in parts
            if "smt" in part["part_id"]
            and imp["controlName"] == part["part_id"].split("_")[0]
            and "_smt" in part["part_id"]
        ]

        params = [
            part
            for part in parts
            if (
                ("prm" in part["part_id"] and imp["controlName"] == part["part_id"].split("_prm")[0])
                or (
                    "odp" in part["part_id"]
                    and imp["controlName"] == part["part_id"].replace("-0", "-").split("_odp")[0]
                )
            )
        ]
        parameters = [dict(t) for t in set(tuple(d.items()) for d in params)]

        # Just load statement parts _smt parts
        for part in part_notes:
            prefix = part["part_id"].split("_")[0]
            control_objectives_items = {
                obj["name"]: obj
                for obj in control_objectives
                if obj["name"].startswith(f"{prefix}_smt") or "_fr_smt" in obj["name"]
            }

            c_objective = control_objectives_items.get(part.get("part_id"))
            if c_objective is None:
                continue
            cntrl_objectives = [obj for obj in control_objectives if obj["name"] == part["part_id"]]
            status_map, _ = get_maps()
            regscale_version = RegscaleVersion.get_platform_version()
            if len(regscale_version) >= 10 or Version(regscale_version) >= Version("6.13.0.0"):
                status = status_map.get(status)

            if cntrl_objectives:
                imp_objective = ImplementationObjective(
                    notes=part["part_id"],
                    status=status,
                    implementationId=imp_id,
                    # optionId=option["id"],
                    securityControlId=imp["controlID"],
                    objectiveId=c_objective["id"],  # controlObjective['id]
                    id=0,
                    uuid=part["uuid"],
                    createdById=config["userId"],
                    statement=part["text"].pop() if part["text"] else "",
                    # TODO: Find and update these data fields.
                    authorizationId=None,
                    responsibility=None,
                    cloudResponsibility=None,
                    customerResponsibility=None,
                )

                if imp_objective not in implementation_objectives:
                    implementation_objectives.append(imp_objective)

        params = update_parameters(trv, existing_parameters, parameters, imp)
        all_params.extend(params)
    post_params(trv, all_params)

    trv.log_info(
        {
            "model_layer": "System Control Implementation",
            "record_type": "Implementation Objective",
            "event_msg": f"Finished loading {len(implementation_objectives)} Implementation Objectives",
        }
    )

    def post_objective(obj: ImplementationObjective) -> requests.Response:
        """
        Post an objective to RegScale

        :param ImplementationObjective obj: An implementation objective
        :return: A response
        :rtype: requests.Response
        """
        url = config["domain"] + "/api/implementationObjectives"
        return api.post(url=url, json=obj.__dict__)

    num_impl_success = 0
    num_impl_failed = 0
    for obj in implementation_objectives:
        response = post_objective(obj)
        if not response:
            num_impl_failed += 1
        else:
            num_impl_success += 1

    trv.log_info(
        {
            "model_layer": "System Control Implementation",
            "record_type": "Implementation Objective",
            "event_msg": f"Finished posting {num_impl_success} Implementation Objectives (Failed: {num_impl_failed})",
        }
    )


def post_params(trv: FedrampTraversal, params: List[dict]):
    """
    Post Parameters to RegScale

    :param FedrampTraversal trv: FedrampTraversal instance
    :param List[dict] params: A list of parameters to post
    """

    def post_parameter(param: dict) -> requests.Response:
        """
        Post a parameter to RegScale

        :param dict param: A parameter
        :return: A response
        :rtype: requests.Response
        """
        url = trv.api.app.config["domain"] + "/api/parameters"
        return trv.api.post(url=url, json=param)

    logger.info("Posting %i Parameters to RegScale", len(params))
    num_params_success = 0
    num_params_failed = 0
    with ThreadPoolExecutor(max_workers=10) as executor:  # Increase the number of workers
        post_futures = {executor.submit(post_parameter, param): param for param in params}

        for future in as_completed(post_futures):
            param = post_futures[future]
            try:
                data = future.result()
                if data is not None:
                    num_params_success += 1
            except Exception as ex:
                logger.debug(f"An error occurred while posting parameter {param}: {ex}")
                num_params_failed += 1

    trv.log_info(
        {
            "model_layer": "System Control Implementation",
            "record_type": "Parameters",
            "event_msg": f"Finished posting {num_params_success} Parameters (Failed: {num_params_failed})",
        }
    )


def update_parameters(
    trv: FedrampTraversal, existing_parameters: List[dict], parameters: List[dict], imp: dict
) -> list[dict]:
    """
    Update parameters

    :param FedrampTraversal trv: FedrampTraversal instance
    :param List[dict] existing_parameters: A list of existing parameters
    :param List[dict] parameters: A list of parameters
    :param dict imp: An implementation object
    :return: A list of updated parameters
    :rtype: list[dict]
    """
    app = trv.api.app
    new_params = []

    for param in parameters:
        dat = [
            par
            for par in existing_parameters
            if par["parameterId"] == param["part_id"] and par["securityControlId"] == imp["controlID"]
        ]
        if dat:
            param["default"] = dat[0]["text"]
        new_param = {
            "id": 0,
            "uuid": "",
            "name": param["part_id"],
            "value": param["text"],
            "controlImplementationId": imp["id"],
            "createdById": app.config["userId"],
            "lastUpdatedById": app.config["userId"],
        }
        new_params.append(new_param)
    return new_params


def get_control_objectives(control_id: int, existing_objectives: List[dict]) -> List[dict]:
    """
    Return control objectives for a given control ID

    :param int control_id: id to fetch objectives for
    :param List[dict] existing_objectives: A list of existing objectives
    :return: A list of control objectives
    :rtype: List[dict]
    """
    return [obj for obj in existing_objectives if obj["securityControlId"] == control_id]


def post_options(trv: FedrampTraversal, options: list[ImplementationOptionDeprecated]) -> list[dict]:
    """
    Post Implementation Option to RegScale

    :param FedrampTraversal trv: FedrampTraversal object
    :param list[ImplementationOptionDeprecated] options: A list of Implementation Options
    :return: A list of responses
    :rtype: list[dict]
    """
    api = trv.api
    res = []
    num_options_success = 0
    num_options_failed = 0
    num_duplicates = 0
    with ThreadPoolExecutor(max_workers=10) as executor:  # Increase the number of workers
        post_futures = {executor.submit(dt.insert, api): dt for dt in options}

        for future in as_completed(post_futures):
            dt = post_futures[future]
            try:
                response = future.result()
                if not response.raise_for_status():
                    res.append(response.json())
                    logger.debug(
                        "Created a New Implementation Option: #%i",
                        response.json()["id"],
                    )
                    num_options_success += 1
            except Exception as ex:
                #  rev 5 contains multiple parts for each control with implemention options
                #  there will be duplicates (which is ok)
                #  do not log a message but count them.
                if response.status_code != 400 and "Duplicate" not in response.text:
                    logger.warning(f"An error occurred while posting data {dt}: {ex}")
                    num_options_failed += 1
                else:
                    num_duplicates += 1

    trv.log_info(
        {
            "model_layer": "System Control Implementation",
            "record_type": "Implementation Option",
            "event_msg": f"Finished posting {num_options_success} Implementation Options (Failed: {num_options_failed} Duplicates: {num_duplicates})",
        }
    )

    return res


def build_options(
    app: Application, existing_options: List[dict], control_objectives: List[dict]
) -> List[ImplementationOptionDeprecated]:
    config = app.config
    results = []
    options = [
        {
            "Status": FULLY_IMPLEMENTED,
            "Description": "The control is fully implemented.",
        },
        {"Status": NOT_IMPLEMENTED, "Description": "The control is not implemented."},
    ]
    for obj in control_objectives:
        for option in options:
            if option["Status"] not in {opt["name"] for opt in existing_options if opt["objectiveId"] == obj["id"]}:
                results.append(
                    ImplementationOptionDeprecated(
                        id=0,
                        uuid="",
                        createdById=config["userId"],
                        dateCreated=get_current_datetime(),
                        lastUpdatedById=app.config["userId"],
                        dateLastUpdated=get_current_datetime(),
                        name=option["Status"],
                        description=option["Description"],
                        archived=False,
                        securityControlId=obj["securityControlId"],
                        objectiveId=obj["id"],
                        otherId="",
                        acceptability=FULLY_IMPLEMENTED,
                    )
                )
    return results
