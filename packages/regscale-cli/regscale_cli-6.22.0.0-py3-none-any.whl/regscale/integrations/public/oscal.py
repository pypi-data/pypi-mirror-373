#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates OSCAL into RegScale"""

# standard python imports
import json
import re
import tempfile
import uuid
from os import remove, sep
from typing import Tuple, Union, Optional

import click
import requests
import xmltodict
import yaml
from bs4 import BeautifulSoup
from packaging import version as package_version
from pathlib import Path

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    check_file_path,
    create_progress_object,
    error_and_exit,
    find_keys,
    get_file_name,
    reformat_str_date,
    save_data_to,
)
from regscale.models.regscale_models import Catalog, ControlImplementation, Component, SecurityControl
from regscale.utils.threading.threadhandler import create_threads, thread_assignment

# create global variables
job_progress = create_progress_object()
logger = create_logger()
OBJ_TO_CONTROLS = False

(
    new_controls,
    new_regscale_controls,
    errors,
    new_params,
    new_tests,
    new_objectives,
    updates,
) = ([], [], [], [], [], [], [])
SC_URL = "/api/securitycontrols/"
UL_CLOSE = "</ul>"
LI = "<li>"
LI_CLOSE = "</li>"


@click.group()
def oscal():
    """Performs bulk processing of OSCAL files."""


# OSCAL Version Support
@oscal.command()
def version():
    """Info on current OSCAL version supported by RegScale."""
    logger.info("RegScale currently supports OSCAL Version 1.0.")


def convert_oscal_comp_to_regscale(j_data: dict) -> None:
    """
    Convert OSCAL component dict into a RegScale Component

    :param dict j_data: OSCAL component
    :rtype: None
    """
    app = Application()
    config = app.config
    api = Api()
    component_id = None
    regscale_components = []
    components = []
    existing_components = api.get(url=config["domain"] + "/api/components/getList").json()
    controls_to_be_added = []

    try:
        components = j_data["component-definition"]["components"]
    except KeyError as kex:
        error_and_exit(f"Key Error! {kex}")

    for comp in components:
        control_implementations = comp["control-implementations"]

        base_catalog = ""
        title = ""

        # alternative
        if len(comp["control-implementations"]) > 0:
            base_catalog = comp["control-implementations"][0]["source"]
        else:
            logger.info(f"Component {comp['title']} contains no control implementation statements")

        component = Component(
            title=comp.get("title", ""),
            componentOwnerId=app.config["userId"],
            componentType=comp.get("type", "").lower(),
            description=comp.get("description", ""),
            purpose=comp.get("purpose", ""),
        )
        regscale_components.append(component.dict())
        for control_implements in control_implementations:
            if "implemented-requirements" in control_implements:
                for control_data in control_implements["implemented-requirements"]:
                    control_data = {
                        "component": comp["title"],
                        # "id": control_data["control-id"],
                        "title": control_data["control-id"],
                        "description": control_data["description"],
                    }
                    controls_to_be_added.append(control_data)
            elif base_catalog and "implemented-requirements" not in control_implements:
                # Get control data from base catalog
                logger.debug("base_catalog: %s\ntitle: %s", base_catalog, title)

    for reg in regscale_components:
        check_component = [x for x in existing_components if x["title"] == reg["title"]]
        if not check_component:
            response = api.post(url=f'{config["domain"]}/api/components/', json=reg)
            if not response.raise_for_status():
                component_id = response.json()["id"]
                logger.info("Successfully posted %s to RegScale.", reg["title"])
        else:
            for cmp in check_component:
                # update the id for the reg object
                reg["id"] = cmp["id"]
                response = api.put(url=f'{config["domain"]}/api/components/{cmp["id"]}', json=reg)
                if not response.raise_for_status():
                    component_id = cmp["id"]
                    logger.info("Successfully updated component %s in RegScale.", cmp["title"])
        # Load controls to RegScale and associate with new component
        load_controls(
            controls_to_be_added=controls_to_be_added,
            component_id=component_id,
            base_catalog=base_catalog,
        )


@oscal.command(name="component")
@click.option(
    "--file_name",
    type=click.Path(exists=True, dir_okay=False),
    help="Enter the path to the file to parse OSCAL Complonents.",
    required=True,
)
def upload_component(file_name: str) -> None:
    """Upload OSCAL Component to RegScale."""
    # Load Controls and assign to component
    process_component(file_name=file_name)


def load_controls(controls_to_be_added: list[dict], component_id: int, base_catalog: str) -> None:
    """
    Load control implementations to RegScale

    :param list[dict] controls_to_be_added: Controls to load from RegScale
    :param int component_id: Component ID from RegScale
    :param str base_catalog: base catalogue to filter components
    :rtype: None
    """
    app = Application()
    config = app.config
    all_implementations = [
        imp.dict()
        for imp in ControlImplementation.get_all_by_parent(parent_id=component_id, parent_module="components")
    ]

    if cat := [cat.dict() for cat in Catalog.get_list() if cat.title == base_catalog]:
        cat_id = cat[0]["id"]
        controls = [control.dict() for control in SecurityControl.get_list_by_catalog(catalog_id=cat_id)]
        for imp_control in controls_to_be_added:
            logger.debug("imp_control: %s", imp_control)
            try:
                if reg_control := [
                    control for control in controls if control["controlId"].lower() == imp_control["title"].lower()
                ]:
                    control_implementation = ControlImplementation(
                        parentId=component_id,
                        parentModule="components",
                        controlOwnerId=config["userId"],
                        status="Fully Implemented",
                        controlID=reg_control[0]["id"],
                        implementation=imp_control["description"],
                    )
                    control = SecurityControl.lookup_control(app=app, control_id=control_implementation.controlID)
                    create_or_update_control(
                        control=control,
                        control_implementation=control_implementation,
                        all_implementations=all_implementations,
                    )
            except requests.RequestException as rex:
                logger.error(rex)
    else:
        logger.debug(f"Catalog '{base_catalog}' not found")

    # Insert or update new control implementations
    ControlImplementation.bulk_save()


def create_or_update_control(
    control: SecurityControl, control_implementation: ControlImplementation, all_implementations: list[dict]
) -> None:
    """
    Create or update control implementation

    :param SecurityControl control: Control object
    :param ControlImplementation control_implementation: Control implementation object
    :param list[dict] all_implementations: List of all control implementations
    :rtype: None
    """
    try:
        if control.controlId not in [
            imp["controlName"] for imp in all_implementations if imp["parentId"] == control_implementation.parentId
        ]:
            control_implementation.create(bulk=True)
        else:
            dat = [
                imp
                for imp in all_implementations
                if imp["controlName"] == control.controlId and imp["parentId"] == control_implementation.parentId
            ][0]
            dat["implementation"] = control_implementation.implementation
            dat["status"] = control_implementation.status
            ControlImplementation(**dat).save(bulk=True)
    except IndexError as iex:
        logger.error("Index Error: %s\n%s", dat, iex)


def process_component(file_name: str) -> None:
    """
    OSCAL Component to RegScale

    :param str file_name: File Name
    :rtype: None
    """
    output_name = tempfile.gettempdir() + sep + "component.json"
    logger.debug(file_name)
    file_convert_json(file_name, output_name)
    try:
        json_d = open(output_name, "r").read()
    except FileNotFoundError:
        error_and_exit(f"File not found!\n{file_name}")
    convert_oscal_comp_to_regscale(j_data=json.loads(json_d))
    remove(output_name)


def file_convert_json(input: str, output: str) -> None:
    """
    Convert file from YML/XML to JSON

    :param str input: Path to the original file to convert
    :param str output: Desired path of the converted file
    :rtype: None
    """
    # Create object
    with open(input, "r") as file_in, open(output, "w") as file_out:
        if Path(input).suffix == ".json":
            obj = json.load(file_in)
        if Path(input).suffix == ".xml":
            obj = xmltodict.parse((file_in.read()))
        if Path(input).suffix in [".yaml", ".yml"]:
            obj = yaml.safe_load(file_in.read())
        json.dump(obj, file_out)


# OSCAL Profile Loader Support
@oscal.command()
@click.option(
    "--title",
    type=click.STRING,
    help="RegScale will name the profile with the title provided.",
    prompt="Enter the title for the OSCAL profile",
    required=True,
)
@click.option(
    "--categorization",
    type=click.Choice(["Low", "Moderate", "High"], case_sensitive=False),
    help="Choose from Low, Moderate, or High.",
    prompt="Enter the FIPS categorization level",
    required=True,
)
@click.option(
    "--catalog",
    type=click.INT,
    help="Primary key (unique ID) of the RegScale catalogue.",
    prompt="Enter the RegScale Catalogue ID to use",
    required=True,
)
@click.option(
    "--file_name",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="RegScale will process and load the profile along with all specified controls.",
    prompt="Enter the file name of the OSCAL profile to process",
    required=True,
)
def profile(title: str, categorization: str, catalog: int, file_name: Path):
    """OSCAL Profile Loader."""
    upload_profile(title=title, categorization=categorization, catalog=catalog, file_name=file_name)


# flake8: noqa: C901
def upload_profile(title: str, categorization: str, catalog: int, file_name: Path) -> None:
    """
    OSCAL Profile Uploader

    :param str title: Title
    :param str categorization: Category information
    :param int catalog: Catalogue Title
    :param Path file_name: Desired file name
    :rtype: None
    """
    app = Application()
    config = app.config
    api = Api()
    # validation
    if catalog <= 0:
        error_and_exit("No catalogue provided or catalogue invalid.")
    elif categorization.title() not in ["Low", "Moderate", "High"]:
        error_and_exit("Categorization not provided or invalid.")

    # load the catalog
    try:
        oscal = open(file_name, "r", encoding="utf-8-sig")
        oscal_data = json.load(oscal)
    except Exception as ex:
        logger.debug(file_name)
        error_and_exit(f"Unable to open the specified OSCAL file for processing.\n{ex}")
    # load the config from YAML
    try:
        config = app.load_config()
    except FileNotFoundError:
        error_and_exit("Unable to open the init.yaml file.")

    global schema

    # set headers
    str_user = config["userId"]
    headers = {"Accept": "application/json", "Authorization": config["token"]}

    # create a new profile
    profile = {
        "id": 0,
        "uuid": "",
        "name": title,
        "confidentiality": "",
        "integrity": "",
        "availability": "",
        "category": categorization,
        "profileOwnerId": str_user,
        "createdById": str_user,
        "dateCreated": None,
        "lastUpdatedById": str_user,
        "dateLastUpdated": None,
        "isPublic": True,
    }

    # create the profile
    url_prof = f'{config["domain"]}/api/profiles/'
    logger.info("RegScale creating a new profile...")
    try:
        prof_response = api.post(url=url_prof, headers=headers, json=profile)
        prof_json_response = prof_response.json()
        logger.info("\nProfile ID: " + str(prof_json_response["id"]))
        # get the profile ID
        int_profile = prof_json_response["id"]
    except requests.exceptions.RequestException as ex:
        error_and_exit(f"Unable to create profile in RegScale.\n{ex}")

    # get the list of existing controls for the catalog
    url_sc = f'{config["domain"]}/api/SecurityControls/getList/{catalog}'
    try:
        sc_response = api.get(url_sc, headers=headers)
        sc_data = sc_response.json()
    except requests.exceptions.RequestException as ex:
        error_and_exit(
            f"Unable to retrieve security controls for this catalogue in RegScale.\nError: \
                {ex}\n{sc_response.text}"
        )

    # loop through each item in the OSCAL control set
    mappings = []
    for m in oscal_data["profile"]["imports"][0]["include-controls"][0]["with-ids"]:
        b_match = False
        for sc in sc_data:
            if m == sc["controlId"]:
                b_match = True
                mapping = {
                    "id": 0,
                    "profileID": int_profile,
                    "controlID": int(sc["id"]),
                }
                mappings.append(mapping)
                break
        if b_match is False:
            logger.error("Unable to locate control: %s.", m)

    # upload the controls to the profile as mappings
    url_maps = config["domain"] + "/api/profileMapping/batchCreate"
    try:
        api.post(url_maps, headers=headers, json=mappings)
        logger.info(
            "%s total mappings created in RegScale for this profile.",
            str(len(mappings)),
        )
    except requests.exceptions.RequestException as ex:
        error_and_exit(f"Unable to create mappings for this profile in RegScale.\n{ex}")


# Process catalog from OSCAL
@oscal.command()
@click.option(
    "--file_name",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    help="RegScale will process and load the catalogue along with all controls, statements, and \
        parameters.",
    prompt="Enter the file name of catalogue in NIST OSCAL to process",
    required=True,
)
@click.option(
    "--obj_to_controls",
    type=click.BOOL,
    default=0,
    show_default=True,
    help="Convert objectives to RegScale controls.",
)
@click.option(
    "--fedramp",
    type=click.BOOL,
    default=0,
    show_default=True,
    required=False,
    help="Specific processing for using the FedRAMP namespace to handle response points and assessment objectives differently",
)
@click.option(
    "--new_catalog_name",
    type=click.STRING,
    help="RegScale will give the catalogue this new name.",
    required=False,
    default=None,
)
def catalog(
    file_name: Path,
    obj_to_controls: click.BOOL,
    fedramp: click.BOOL,
    new_catalog_name: str,
):
    """Process and load catalog to RegScale."""
    upload_catalog(
        file_name=file_name,
        obj_to_controls=obj_to_controls,
        fedramp=fedramp,
        new_catalog_name=new_catalog_name,
    )


# flake8: noqa: C901
def upload_catalog(
    file_name: Path,
    obj_to_controls: click.BOOL = 0,
    fedramp: click.BOOL = 0,
    new_catalog_name: str = None,
) -> None:
    """
    Process and load catalogue to RegScale

    :param Path file_name: Path to the catalogue to upload
    :param click.BOOL obj_to_controls: Flag to indicate converting objectives to controls
    :param click.BOOL fedramp: Flag to indicate it is a FedRAMP catalog so it processes differently
    :param str new_catalog_name: New name to give the catalogue when uploaded, defaults to None
    :rtype: None
    """
    import pandas as pd  # Optimize import performance

    app = Application()
    config = app.config
    api = Api()
    # Create directory if not exists
    check_file_path("processing")

    # load the catalog
    try:
        with open(file_name, "r", encoding="utf-8-sig") as input:
            oscal_data = json.load(input)
    except requests.exceptions.RequestException as ex:
        error_and_exit(f"Unable to open the specified OSCAL file for processing.\n{ex}")
    # load the config from YAML
    try:
        config = app.load_config()
    except Exception:
        error_and_exit("Unable to open the init file.")
    # debug flag to pause upload when testing and debugging (always true for production CLI use)
    upload_flag = params_flag = tests_flag = objects_flag = deep_links_flag = True

    # set headers
    str_user = config["userId"]

    # parse the OSCAL JSON to get related data (used to enrich base spreadsheet)
    catalog_arr = (
        oscal_data["catalog"]
        if "catalog" in oscal_data
        else error_and_exit("catalogue key not found in dataset, exiting..")
    )
    str_uuid = catalog_arr["uuid"]
    metadata = catalog_arr["metadata"]
    global schema
    schema = oscal_version(metadata)
    resource_guid = ""
    resource_title = ""
    citation = ""
    links = ""

    # process resources for lookup
    resources = []
    if "back-matter" in catalog_arr:
        back_matter_arr = catalog_arr["back-matter"]
        for i in back_matter_arr["resources"]:
            # make sure values exist
            if "title" in i:
                resource_title = i["title"]
            if "uuid" in i:
                resource_guid = i["uuid"]
            if "citation" in i:
                citation = i["citation"]
                if "text" in citation:
                    citation = citation["text"]
            links = ""
            if "rlinks" in i:
                links = i["rlinks"]
                if len(links) > 1:
                    for x in links:
                        if "href" in x:
                            links += x["href"] + "<br/>"
                elif isinstance(links[0], dict) and len(links) == 1:
                    links = links[0].get("href")
            # add parsed/flattened resource to the array
            res = {
                "uuid": resource_guid,
                "short": resource_title,
                "title": citation,
                "links": links,
            }
            resources.append(res)

    # Write to file to visualize the output
    save_data_to(
        file=Path("./processing/resources.json"),
        data=resources,
        output_log=False,
    )
    # convert data to pandas dataframe
    raw_data = pd.DataFrame(resources)

    # copy the columns of data that we want while renaming them to a specific case
    resource_data = (
        raw_data[["uuid", "title", "links"]].copy().rename(columns={"uuid": "UUID", "title": "Title", "links": "Links"})
    )

    # convert the data table to an HTML formatted table
    str_resources = resource_data.to_html(index=False, justify="left")

    # determine the date to use
    date_format = "%Y-%m-%d %H:%M:%S.%f %z"
    if "fedramp" in catalog_arr["metadata"]["version"].lower():
        # format the dates into strings for RegScale
        date_published = reformat_str_date(catalog_arr["metadata"]["published"], dt_format=date_format)
        last_modified = reformat_str_date(
            catalog_arr["metadata"]["last-modified"],
            dt_format=date_format,
        )
    else:
        # published date is required in RegScale but not found in NIST OSCAL catalog.  Defaulting to last-modified date which is required in NIST OSCAL catalog
        date_published = reformat_str_date(
            catalog_arr["metadata"]["last-modified"],
            dt_format=date_format,
        )
        last_modified = reformat_str_date(
            catalog_arr["metadata"]["last-modified"],
            dt_format=date_format,
        )

    # setup catalog data
    cat = Catalog(
        **{
            "title": (
                catalog_arr["metadata"]["title"]
                if (new_catalog_name is None or new_catalog_name == "")
                else new_catalog_name
            ),
            "description": "This publication provides a catalog of security and privacy controls for information systems and organizations to protect organizational operations and assets, individuals, other organizations, and the Nation from a diverse set of threats and risks, including hostile attacks, human errors, natural disasters, structural failures, foreign intelligence entities, and privacy risks. <br/><br/><strong>Resources</strong><br/><br/>"
            + str_resources,
            "datePublished": date_published,
            "uuid": str_uuid,
            "lastRevisionDate": last_modified,
            "url": "https://csrc.nist.gov/",
            "abstract": "This publication provides a catalog of security and privacy controls for federal information systems and organizations and a process for selecting controls to protect organizational operations (including mission, functions, image, and reputation), organizational assets, individuals, other organizations, and the Nation from a diverse set of threats including hostile cyber attacks, natural disasters, structural failures, and human errors (both intentional and unintentional). The security and privacy controls are customizable and implemented as part of an organization-wide process that manages information security and privacy risk. The controls address a diverse set of security and privacy requirements across the federal government and critical infrastructure, derived from legislation, Executive Orders, policies, directives, regulations, standards, and/or mission/business needs. The publication also describes how to develop specialized sets of controls, or overlays, tailored for specific types of missions/business functions, technologies, or environments of operation. Finally, the catalog of security controls addresses security from both a functionality perspective (the strength of security functions and mechanisms provided) and an assurance perspective (the measures of confidence in the implemented security capability). Addressing both security functionality and assurance helps to ensure that information technology component products and the information systems built from those products using sound system and security engineering principles are sufficiently trustworthy.",
            "keywords": "FIPS Publication 200; FISMA; Privacy Act; Risk Management Framework; security controls; FIPS Publication 199; security requirements; computer security; assurance;",
            "createdById": str_user,
            "lastUpdatedById": str_user,
        }
    )

    # create the catalog and print success result
    if upload_flag is True:
        logger.debug("Creating new catalogue in RegScale.")
        # update the timeout
        if api.timeout < 120:
            api.timeout = 120
        new_cat = cat.create()
        catalogue_id = new_cat.id
        logger.info("Created Catalogue ID: %s in RegScale", catalogue_id)
        # get the catalog ID
    else:
        # don't set ID in debug mode
        catalogue_id = 0

    # process NIST families of controls
    families = []
    oscal_controls = []
    parameters = []
    parts = []
    assessments = []
    objectives = []

    # process groups of controls
    groups = catalog_arr["groups"]

    for i in groups:
        str_family = i["title"]
        f = {
            "id": (i["id"] if package_version.parse(schema) <= package_version.parse("1.0.2") else None),
            "title": i["title"],
        }
        # add parsed item to the family array
        families.append(f)

        controls = (
            list(find_keys(i, "controls"))
            if package_version.parse(schema) > package_version.parse("1.0.2")
            else i["controls"]
        )

        # loop through controls
        for ctrl in controls:
            # process the control
            if isinstance(ctrl, dict):
                oscal_controls = append_controls(
                    oscal_controls,
                    ctrl,
                    resources,
                    str_family,
                    parameters,
                    parts,
                    assessments,
                    objectives,
                    fedramp,
                )

            if isinstance(ctrl, list):
                for cnt in ctrl:
                    oscal_controls = append_controls(
                        oscal_controls,
                        cnt,
                        resources,
                        str_family,
                        parameters,
                        parts,
                        assessments,
                        objectives,
                        fedramp,
                    )

            # check for child controls/enhancements
            if "controls" in ctrl:
                child_ctrls = ctrl["controls"]
                for child_ctrl in child_ctrls:
                    oscal_controls = append_controls(
                        oscal_controls,
                        child_ctrl,
                        resources,
                        str_family,
                        parameters,
                        parts,
                        assessments,
                        objectives,
                        fedramp,
                    )

    # more unique processing for FedRAMP
    if fedramp:
        # arrays to hold processed fields
        assessments = []
        processed_objectives = []
        # loop over each objective
        for obj in objectives:
            # replace response point language
            if obj["description"].find("You must fill in this response point. ") > 0:
                obj["description"] = obj["description"].replace("You must fill in this response point. ", "")
                obj["description"] += " (REQUIRED)"
            # put in the right bucket
            if obj["objectiveType"] == "objective":
                processed_objectives.append(obj)
            else:
                new_test = {
                    "id": 0,
                    "name": obj["name"],
                    "testType": "TEST",
                    "description": obj["description"],
                    "parentControl": obj["parentControl"],
                }
                assessments.append(new_test)
        objectives = processed_objectives

    # Write to file to visualize the output
    save_data_to(
        file=Path("./processing/families.json"),
        data=families,
        output_log=False,
    )

    # Write to file to visualize the output
    save_data_to(
        file=Path("./processing/controls.json"),
        data=oscal_controls,
        output_log=False,
    )

    # Write to file to visualize the output
    save_data_to(
        file=Path("./processing/parameters.json"),
        data=parameters,
        output_log=False,
    )

    # Write to file to visualize the output
    save_data_to(
        file=Path("./processing/parts.json"),
        data=parts,
        output_log=False,
    )

    # Write to file to visualize the output
    save_data_to(
        file=Path("./processing/tests.json"),
        data=assessments,
        output_log=False,
    )

    # Write to file to visualize the output
    save_data_to(
        file=Path("./processing/objectives.json"),
        data=objectives,
        output_log=False,
    )

    # output the items processed from the provided OSCAL catalog
    logger.info(
        "%s familys, %s controls, %s parameters, %s objectives %s parts & %s assessments processed from %s.",
        len(families),
        len(oscal_controls),
        len(parameters),
        len(objectives),
        len(parts),
        len(assessments),
        get_file_name(file_name),
    )

    # use the progress object for the threaded process
    with job_progress:
        global new_regscale_controls
        if oscal_controls:
            # log the information
            logger.debug("Posting %s OSCAL controls to RegScale.", len(oscal_controls))
            # create task for job progress object
            creating_controls = job_progress.add_task(
                f"[#f8b737]Creating {len(oscal_controls)} controls in RegScale...",
                total=len(oscal_controls),
            )
            # create threads to create controls
            create_threads(
                process=post_controls,
                args=(
                    oscal_controls,
                    catalogue_id,
                    upload_flag,
                    creating_controls,
                    api,
                ),
                thread_count=len(oscal_controls),
            )
            # log the outcome
            logger.info(
                "%s/%s OSCAL controls created in RegScale.",
                len(new_regscale_controls),
                len(oscal_controls),
            )
            # Write to file to visualize the output
            save_data_to(
                file=Path("./processing/mappedControls.json"),
                data=new_controls,
                output_log=False,
            )
        # Write to file to visualize the output
        if upload_flag:
            save_data_to(
                file=Path("./processing/newControls.json"),
                data=new_regscale_controls,
                output_log=False,
            )
        else:
            with open(f"processing{sep}newControls.json", "r", encoding="utf-8-sig") as infile:
                new_regscale_controls = json.load(infile)
        # only process if the controls exists to map to
        if len(new_regscale_controls) > 0:
            if parameters:
                # log the information
                logger.debug("Posting %s parameters to RegScale.", len(parameters))
                # create task for analyzing child controls
                posting_child_controls = job_progress.add_task(
                    f"[#ef5d23]Creating {len(parameters)} parameters in RegScale...",
                    total=len(parameters),
                )
                # create threads to post child controls
                create_threads(
                    process=post_child_controls,
                    args=(
                        parameters,
                        new_regscale_controls,
                        params_flag,
                        posting_child_controls,
                        api,
                    ),
                    thread_count=len(parameters),
                )
                # log the outcome
                logger.info(
                    "%s/%s OSCAL parameters created in RegScale.",
                    len(new_params),
                    len(parameters),
                )

                # output the result
                save_data_to(
                    file=Path("processing/newParameters.json"),
                    data=new_params,
                    output_log=False,
                )
            if assessments:
                # log the information
                logger.debug("Posting %s assessments to RegScale.", len(assessments))
                # create task for creating assessments
                assigning_tests = job_progress.add_task(
                    f"[#21a5bb]Creating {len(assessments)} assessments in RegScale...",
                    total=len(assessments),
                )
                # create threads to create tests
                create_threads(
                    process=assign_control_tests,
                    args=(
                        assessments,
                        new_regscale_controls,
                        tests_flag,
                        assigning_tests,
                        api,
                    ),
                    thread_count=len(assessments),
                )
                # output the result
                save_data_to(
                    file=Path("./processing/newTests.json"),
                    data=new_tests,
                    output_log=False,
                )
                # log the outcome
                logger.info(
                    "%s/%s assessments created in RegScale.",
                    len(new_tests),
                    len(assessments),
                )
            # process objectives based on FedRAMP flag
            if not fedramp:
                obj_parts = [
                    part
                    for part in parts
                    if part["objectiveType"] in ["objective", "assessment-objective"]
                    and part["description"] not in ["Determine if the organization:", "Determine if:"]
                ]
                if obj_parts:
                    # log the information
                    logger.debug("Analyzing %s objectives for posting to RegScale.", len(parts))
                    # create task for creating objectives
                    creating_objectives = job_progress.add_task(
                        f"[#0866b4]Analyzing {len(parts)} OSCAL objectives for creation in RegScale...",
                        total=len(parts),
                    )
                    # create threads to loop through controls
                    create_threads(
                        process=create_objectives,
                        args=(
                            obj_parts,
                            new_regscale_controls,
                            objects_flag,
                            creating_objectives,
                            api,
                        ),
                        thread_count=len(obj_parts),
                    )
                    # complete the task for creating objectives
                    job_progress.advance(creating_objectives, len(parts))

                    # log the outcome
                    logger.info("%s objectives created in RegScale.", len(new_objectives))
                    # output the result
                    save_data_to(
                        file=Path("./processing/newObjectives.json"),
                        data=new_objectives,
                        output_log=False,
                    )
            else:
                # log the information
                logger.debug("Analyzing %s objectives for posting to RegScale.", len(objectives))
                # create task for creating objectives
                creating_objectives = job_progress.add_task(
                    f"[#0866b4]Creating {len(objectives)} objectives in RegScale...",
                    total=len(objectives),
                )
                # create threads to loop through controls
                create_threads(
                    process=create_objectives,
                    args=(
                        objectives,
                        new_regscale_controls,
                        objects_flag,
                        creating_objectives,
                        api,
                    ),
                    thread_count=len(objectives),
                )
                # complete the task for creating objectives
                job_progress.advance(creating_objectives, len(objectives))
            if deep_links_flag:
                # process deep links
                try:
                    logger.info(
                        "Retrieving all objectives for this catalogue # %i from RegScale (this might take a minute)...",
                        catalogue_id,
                    )
                    # extend the api timeout for this api call
                    api.timeout = 60
                    url_deep = f'{config["domain"]}/api/controlObjectives/getByCatalogue/{catalogue_id}'
                    obj_list_response = api.get(url_deep, headers={"Authorization": config["token"]})
                    obj_list = obj_list_response.json()
                    logger.info(
                        "%i total objectives now retrieved from RegScale for processing.",
                        len(obj_list),
                    )
                except Exception:
                    error_and_exit("Unable to retrieve control objective information from RegScale.")
                # log the information
                logger.debug(
                    "Analyzing %s objectives for potential updating in RegScale.",
                    len(assessments),
                )
                # create task for creating objectives
                updating_objectives = job_progress.add_task(
                    f"[#05d1b7]Analyzing {len(obj_list)} objectives in RegScale...",
                    total=len(obj_list),
                )
                # create threads to loop through controls
                create_threads(
                    process=update_objectives,
                    args=(obj_list, parts, updating_objectives, api),
                    thread_count=len(obj_list),
                )
                # log the outcome
                logger.info(
                    "%s objectives analyzed & %s objectives updated in RegScale.",
                    len(obj_list),
                    len(updates),
                )
            if errors:
                # output the errors
                save_data_to(
                    file=Path("./processing/errors.json"),
                    data=new_objectives,
                )
            if obj_to_controls:
                # create task for creating objectives
                inserting_controls_from_objectives = job_progress.add_task(
                    f"[#c42843]Creating {len(new_objectives)} control(s) from objectives..."
                )
                # Post Objectives as Controls
                create_threads(
                    process=post_alternative_controls,
                    args=(
                        new_objectives,
                        parts,
                        inserting_controls_from_objectives,
                        api,
                    ),
                    thread_count=len(new_objectives),
                )


def post_controls(args: Tuple, thread: int) -> None:
    """
    Function to analyze controls from OSCAL catalog and post them to RegScale while using threads

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """
    # set up local variables from args passed
    controls, catalog_id, upload_flag, task, api = args

    # set up RegScale URL
    url_sc = api.config["domain"] + SC_URL

    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(controls))

    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        # set the recommendation for the thread for later use in the function
        control = controls[threads[i]]
        str_parts = strip_tag(
            control["parts"], "_obj"
        )  # Strip objectives from the tag, we still need to keep them in the original parts list.
        # create each security control

        description = str_parts.replace(
            "<ul><li>{{" + control["id"] + "_smt}} - </li><ul>",
            "<ul><li>{{" + control["id"] + "_smt}} - Control:</li><ul>",
        )

        security_control = {
            "title": control["id"] + " - " + control["title"],
            "controlType": "Stand-Alone",
            "controlId": control["id"],
            "sortId": control["sortId"],
            "description": description + control["guidance"],
            "references": control["links"],
            "relatedControls": "",
            "subControls": "",
            "enhancements": control["enhancements"],
            "family": control["family"],
            "mappings": control["parameters"],
            "assessmentPlan": control["assessment"],
            "weight": 0,
            "practiceLevel": "",
            "catalogueID": catalog_id,
            "createdById": api.config["userId"],
            "lastUpdatedById": api.config["userId"],
        }
        # attempt to create the security control
        if upload_flag:
            try:
                # upload to RegScale

                response = api.post(url=url_sc, json=security_control)
                json_response = response.json()
                logger.debug("\n\nSuccess - %s", security_control["title"])

                # update id to the new control id
                security_control["id"] = json_response["id"]
                new_controls.append(security_control)

                # add the new controls
                new_regscale_controls.append(json_response)
            except requests.exceptions.RequestException:
                logger.error("Unable to create security control %s,", security_control["title"])
                errors.append(security_control)
        else:
            # append the result
            new_regscale_controls.append(security_control)
        job_progress.update(task, advance=1)


def extract_text(html_string: str, elem: str) -> dict:
    """
    Function to return an object with a representation of a string formatted and cleaned

    :param str html_string: A string of HTML
    :param str elem: An HTML tag type (ex. li)
    :return: A dictionary object with a representation of a string formatted and cleaned
    :rtype: dict
    """
    result = {
        "key": "",
        "original_text": html_string,
        "clean_text": "",
        "extract_text": "",
    }
    pattern = r"{([^{{]*?)}"
    soup = BeautifulSoup(html_string, "html.parser")
    for elem in soup.find_all(elem):
        txt = elem.text.strip()
        result["clean_text"] = txt
        match = re.search(pattern, txt)
        if match:
            key = match.group(1)
            result["key"] = key
        dat_ix = txt.find(" -")
        result["extract_text"] = txt[dat_ix:]
    return result


def strip_tag(html_string: str, sub_str_to_find: str) -> str:
    """
    Function to strip an HTML tag from a string based on a substring

    :param str html_string: A string of HTML
    :param str sub_str_to_find: A substring to search for
    :return: String with HTML tag removed
    :rtype: str
    """
    result = html_string
    try:
        soup = BeautifulSoup(html_string, "html.parser")
        for tag in soup.find_all(lambda tag: tag.name == "li" and sub_str_to_find in tag.text):
            tag.extract()
        # Strip empty HTML tags
        for tag in soup.find_all(lambda tag: not tag.contents or tag.contents == [""]):
            tag.extract()
        for datx in soup.find_all():
            if len(datx.get_text(strip=True)) == 0:
                # Remove empty tags
                datx.extract()
        result = str(soup)
    except ValueError as vex:
        logger.error(vex)
    return result


def post_alternative_controls(args: Tuple, thread: int) -> None:
    """
    Function to post controls from objectives

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """
    new_objs, parts, task, api = args

    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(new_objs))

    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        obj = new_objs[threads[i]]
        # Please don't automate my job ChatGPT
        title = reformat_title(obj["name"])
        label = [part["part_label"] for part in parts if part["name"] == obj["name"]][0]
        # Create a Child Control for this special case
        security_control_id = obj["securityControlId"]
        ctrl_lookup = api.get(url=api.config["domain"] + f"{SC_URL}{security_control_id}").json()
        security_control = {
            "title": (
                f"objective: {label} - {obj['description']}" if title else "objective"
            ),  # f"{ctrl_lookup['controlId']} objective: {title}",
            "controlType": "Mapping",  # Can also be Stand-Alone
            "controlId": ctrl_lookup["controlId"],
            "description": obj["description"],
            "references": ctrl_lookup["references"],
            "relatedControls": ctrl_lookup["id"],
            "subControls": "",
            "enhancements": "",
            "family": ctrl_lookup["family"],
            "mappings": "",
            "assessmentPlan": ctrl_lookup["assessmentPlan"],
            "weight": 0,
            "practiceLevel": "",
            "catalogueID": ctrl_lookup["catalogueID"],
            "createdById": api.config["userId"],
            "lastUpdatedById": api.config["userId"],
        }
        api.post(url=api.config["domain"] + SC_URL, json=security_control)
        job_progress.update(task, advance=1)


def reformat_title(string: str) -> str:
    """
    Function to reformat the title of a string

    :param str string: A string to reformat
    :return: Reformatted string
    :rtype: str
    """
    # strip everything before 'obj'
    new_string = None
    try:
        new_string = string.split("obj.")[1]
    except IndexError:
        new_string = string.split("obj")[1]
    new_string = new_string.replace("_", " ")
    new_string = (new_string.lstrip(".")).lstrip("-")
    return new_string


def post_child_controls(args: Tuple, thread: int) -> None:
    """
    Function to analyze child controls from OSCAL catalog and posts them to RegScale while using \
        threads

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """
    # set up local variables from args passed
    parameters, regscale_controls, params_flag, task, api = args

    # set up RegScale URL
    url_params = api.config["domain"] + "/api/controlParameters/"

    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(parameters))

    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        # set the parameter for the thread for later use in the function
        parameter = parameters[threads[i]]

        # find the parent control
        ctrl_lookup = next(
            (item for item in regscale_controls if (item["controlId"] == parameter["controlId"])),
            None,
        )
        if ctrl_lookup is None:
            logger.error(
                "Unable to locate %s for this parameter: %s.",
                parameter["controlId"],
                parameter["name"],
            )
        else:
            # create a new parameter to upload
            new_param = {
                "id": 0,
                "uuid": "",
                "text": parameter["value"],
                "dataType": "string",
                "parameterId": parameter["name"],
                "default": parameter["default"],
                "securityControlId": ctrl_lookup["id"],
                "archived": False,
                "createdById": api.config["userId"],
                "dateCreated": None,
                "lastUpdatedById": api.config["userId"],
                "dateLastUpdated": None,
            }

            # attempt to create the parameter
            if params_flag:
                try:
                    # upload to RegScale
                    response = api.post(url_params, json=new_param)
                    response_data = response.json()
                    logger.debug(
                        "\n\nSuccess - %s parameter uploaded successfully.",
                        new_param["parameterId"],
                    )
                    # update the id to the new parameter id
                    new_param["id"] = response_data["id"]

                    # add the control to the new array
                    new_params.append(new_param)
                except requests.exceptions.RequestException:
                    logger.error("Unable to create parameter: %s.", new_param["parameterId"])
                    errors.append(new_param)
            else:
                # add the control to the new array
                new_params.append(new_param)
        job_progress.update(task, advance=1)


def assign_control_tests(args: Tuple, thread: int) -> None:
    """
    Function to analyze match controls to assessments while using threads

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """
    # set up local variables from args passed
    assessments, regscale_controls, fedramp, tests_flag, task, api = args

    # set up RegScale URL
    url_tests = api.config["domain"] + "/api/controlTestPlans/"

    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(assessments))

    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        # set the recommendation for the thread for later use in the function
        assessment = assessments[threads[i]]
        # find the parent control
        ctrl_lookup = next(
            (item for item in regscale_controls if (item["controlId"] == assessment["parentControl"])),
            None,
        )
        if ctrl_lookup is None:
            logger.error("Unable to locate %s for this test.", assessment["parentControl"])
        else:
            # create a new test to upload
            new_test = {
                "id": 0,
                "uuid": "",
                "test": f'{assessment["testType"]} - {assessment["description"]}',
                "testId": assessment["name"] if fedramp else str(uuid.uuid4()),
                "securityControlId": ctrl_lookup["id"],
                "archived": False,
                "createdById": api.config["userId"],
                "dateCreated": None,
                "lastUpdatedById": api.config["userId"],
                "dateLastUpdated": None,
            }
            # attempt to create the test
            if tests_flag:
                try:
                    # upload to RegScale
                    response = api.post(url_tests, json=new_test)
                    json_response = response.json()
                    logger.debug(
                        "\n\nSuccess - %s -  test uploaded successfully.",
                        new_test["test"],
                    )
                    # update the id to the new test id
                    new_test["id"] = json_response["id"]

                    # add the test to the new array
                    new_tests.append(new_test)
                except requests.exceptions.RequestException:
                    logger.error("Unable to create test: %s.", new_test["test"])
                    errors.append(new_test)
            else:
                # add the test to the new array
                new_tests.append(new_test)
        job_progress.update(task, advance=1)


def create_objectives(args: Tuple, thread: int) -> None:
    """
    Function to create objectives from OSCAL catalog and post them to RegScale while using threads

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """

    # set up local variables from args passed
    (
        objectives,
        regscale_controls,
        objects_flag,
        task,
        api,
    ) = args

    # set up RegScale URL
    url_objs = api.config["domain"] + "/api/controlObjectives/"

    # find which records should be executed by the current thread

    obj_parts = list(objectives)
    threads = thread_assignment(thread=thread, total_items=len(obj_parts))

    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        # set the recommendation for the thread for later use in the function
        objective: dict = obj_parts[threads[i]]

        # find the parent control
        ctrl_lookup = next(
            (item for item in regscale_controls if (item["controlId"] == objective["parentControl"])),
            None,
        )
        if ctrl_lookup is None:
            logger.error(
                "Unable to locate %s for this objective/part: %s.",
                objective["parentControl"],
                objective["name"],
            )
            job_progress.update(task, advance=1)
            return

        # create a new test to upload
        new_obj = {
            "id": 0,
            "uuid": "",
            "name": objective["name"],
            "description": objective["description"],
            "objectiveType": objective["objectiveType"],
            "otherId": "",
            "securityControlId": ctrl_lookup["id"],
            "parentObjectiveId": None,
            "archived": False,
            "createdById": api.config["userId"],
            "dateCreated": None,
            "lastUpdatedById": api.config["userId"],
            "dateLastUpdated": None,
        }

        # attempt to create the objective
        if objects_flag:
            try:
                # upload to RegScale
                response = api.post(url_objs, json=new_obj)
                json_response = response.json()
                logger.debug(
                    "\n\nSuccess - %s -  objective uploaded successfully.",
                    new_obj["name"],
                )
                # try to update the id to the new control id
                try:
                    new_obj["id"] = json_response["id"]
                except KeyError:
                    continue

                # add the objective to the new array
                new_objectives.append(new_obj)
            except requests.exceptions.RequestException as rex:
                logger.error("Unable to create objective: %s.\n%s", new_obj["name"], rex)
                errors.append(new_obj)
        else:
            # add the part to the new array
            new_objectives.append(new_obj)
        job_progress.update(task, advance=1)


def update_objectives(args: Tuple, thread: int) -> None:
    """
    Loop through each objective and see if it has a parent, if so,
    update parent ID and send update to RegScale while using threads

    :param Tuple args: Tuple of args to use during the process
    :param int thread: Thread number of current thread
    :rtype: None
    """
    # set up local variables from args passed
    objectives, parts, task, api = args

    # set up RegScale URL
    url_objs = api.config["domain"] + "/api/controlObjectives/"

    # find which records should be executed by the current thread
    threads = thread_assignment(thread=thread, total_items=len(objectives))

    # iterate through the thread assignment items and process them
    for i in range(len(threads)):
        # set the recommendation for the thread for later use in the function
        objective = objectives[threads[i]]

        # find the part by name
        part_lookup = next((item for item in parts if (item["name"] == objective["name"])), None)
        if part_lookup is not None:
            # see if the part has a parent
            if part_lookup["parentObjective"] != "":
                # lookup the parent objective from RegScale
                parent_lookup = next(
                    (item for item in objectives if (item["name"] == part_lookup["parentObjective"])),
                    None,
                )
                if parent_lookup is not None:
                    logger.debug("Found Parent: %s.", parent_lookup["name"])
                    # update the parent
                    update_parent = parent_lookup["objective"]
                    update_parent["parentObjectiveId"] = parent_lookup["id"]
                    try:
                        # upload to RegScale
                        update_response = api.put(
                            f'{url_objs}{update_parent["id"]}',
                            json=update_parent,
                        )
                        logger.debug(
                            "Success - %s -  objective parent updated successfully.",
                            update_parent["name"],
                        )
                        updates.append(update_response)
                    except requests.exceptions.RequestException:
                        logger.error(
                            "Unable to update parent objective: %s.",
                            update_parent["name"],
                        )
                        errors.append(update_parent)
        job_progress.update(task, advance=1)


def process_fedramp_objectives(part: dict, str_obj: str, objectives: list, ctrl, str_name: Optional[str] = "") -> str:
    """
    Function to handle processing of FedRAMP objectives

    :param dict part: Part from OSCAL
    :param str str_obj: Concatenated objective string
    :param list objectives: A list of OSCAL objective strings
    :param ctrl: Parent security control
    :param str str_name: Name of the part
    :return: Processed FedRAMP objective object
    :rtype: str
    """
    str_prose = part.get("prose", "")

    str_name = part.get("name", "") if not str_name else str_name
    if str_name == "statement":
        str_obj += f"{str_prose} "
    elif str_name == "item" or str_name == "objective":
        if "props" in part and str_name != "objective":
            str_obj += f"{part['props'][0]['value']} "
        str_obj += f"{str_prose} "
    str_type = "assessment" if str_name == "objective" else "objective"

    if sub_parts := part.get("parts", []):
        for sub_part in sub_parts:
            str_obj2 = str_obj
            _ = process_fedramp_objectives(sub_part, str_obj2, objectives, ctrl, str_name)
    else:
        if str_obj.rstrip() != "":
            new_obj = {
                "id": 0,
                "name": part["id"],
                "part_id": ctrl["id"],
                "objectiveType": str_type,
                "description": str_obj,
                "parentControl": ctrl["id"],
                "parentObjective": "",
            }
            objectives.append(new_obj)
    return str_obj.rstrip()


def process_objectives(objs: list, parts: list, ctrl: Union[list, dict], parent_id: int, fedramp: bool) -> str:
    """
    Function for recursively working through objectives and formatting it as HTML description

    :param list objs: List of RegScale object
    :param list parts: Parts of the object
    :param Union[list, dict] ctrl: Controls for the object
    :param int parent_id: Parent id of the Object
    :param bool fedramp: Flag if catalog is a FedRAMP catalog
    :return: HTML formatted string of object
    :rtype: str
    """
    str_obj = "<ul>"
    # loop through parts/objectives recursively
    for obj in objs:
        # check prose
        str_prose = obj.get("prose", "")

        # check name
        str_name = obj.get("name", "")

        # create the new part
        part = {
            "id": 0,
            "part_id": obj["id"].split("_")[0],
            "part_label": obj["props"][0]["value"] if "props" in obj else None,
            "name": obj["id"],
            "objectiveType": str_name if "objective" not in str_name else "objective",
            "description": str_prose,
            "parentControl": ctrl["id"],
            "parentObjective": parent_id,
        }
        if "obj" in obj["id"] or "item" in obj["name"] or "overview" in obj["name"]:
            parts.append(part)
            str_obj += LI + "{{" + obj["id"] + "}}"
            if "prose" in obj:
                str_obj += " - " + str_prose
            str_obj += LI_CLOSE
            if "parts" in obj:
                str_obj += process_objectives(obj["parts"], parts, ctrl, obj["id"], fedramp)
    str_obj += UL_CLOSE
    return str_obj


def process_control(
    ctrl: Union[list, dict],
    resources: list,
    str_family: str,
    parameters: list,
    parts: list,
    assessments: list,
    objectives: list,
    fedramp: bool,
) -> dict:
    """
    Function to process each control and formats it as a dictionary

    :param Union[list, dict] ctrl: RegScale control
    :param list resources: resources of control
    :param str str_family: Family of control
    :param list parameters: Parameters for the control
    :param list parts: Parts of the control
    :param list assessments: Assessments belonging to the control
    :param list objectives: A list of OSCAL objective strings
    :param bool fedramp: Boolean - is a FedRAMP catalog
    :return: Dictionary of new control
    :rtype: dict
    """
    # see if parameters exist
    if "params" in ctrl:
        # loop through each parameter
        for param in ctrl["params"]:
            # create a new parameter object
            p_new = {
                "name": param["id"],
                "value": "",
                "paramType": "",
                "default": "",
                "controlId": ctrl["id"],
            }
            # process basic label
            if "label" in param:
                p_new["paramType"] = "text"
                p_new["value"] = param["label"]
            else:
                # initialize
                str_params = "Select ("
                # process select types
                if "select" in param:
                    select = param["select"]
                    if "how-many" in select:
                        str_params += select["how-many"]
                        p_new["paramType"] = "how-many"
                    if "choice" in select:
                        p_new["paramType"] = "choice"
                        str_params += "select) - "
                        for cho in select["choice"]:
                            str_params += cho + ", "
                    p_new["value"] = str_params

            # check for default
            if "constraints" in param:
                for c in param["constraints"]:
                    p_new["default"] += c["description"] + "; "

            # add to the array
            parameters.append(p_new)

    # get enhancements
    str_enhance = ""
    if "controls" in ctrl:
        child_enhc = ctrl["controls"]
        str_enhance += "<strong>Enhancements</strong><br/><br/>"
        str_enhance += "<ul>"
        for che in child_enhc:
            str_enhance += LI + "{{" + che["id"] + "}} - " + che["title"] + LI_CLOSE
        str_enhance += UL_CLOSE

    # process control links
    int_link = 1
    str_links = ""
    if "links" in ctrl:
        for link in ctrl["links"]:
            # lookup the OSCAL control to enrich the data
            link_lookup = next(
                (item for item in resources if ("#" + item["uuid"]) == link["href"]),
                None,
            )
            if link_lookup is not None:
                str_links += (
                    str(int_link) + ") " + link_lookup["title"] + " (OSCAL ID: " + link_lookup["uuid"] + ")<br/>"
                )
                int_link += 1
            else:
                str_links += link["href"] + "<br/>"

    # process parts
    part_info = process_parts(ctrl, parts, assessments, objectives, fedramp)

    # process sort Id if provided (FedRAMP specific)
    str_sort_id = ctrl["id"]
    if "props" in ctrl:
        for p in ctrl["props"]:
            if p["name"] == "sort-id":
                str_sort_id = p["value"]

    # add control
    new_ctrl = {
        "id": ctrl["id"],
        "title": ctrl["title"],
        "sortId": str_sort_id,
        "family": (str_family if package_version.parse(schema) <= package_version.parse("1.0.2") else ctrl["class"]),
        "links": str_links,
        "parameters": "",
        "parts": part_info["parts"],
        "assessment": part_info["assessments"],
        "guidance": part_info["guidance"],
        "enhancements": str_enhance,
    }

    # return the result
    return new_ctrl


def process_parts(ctrl: Union[list, dict], parts: list, assessments: list, objectives: list, fedramp: bool) -> dict:
    """
    Function to format control

    :param Union[list, dict] ctrl: RegScale control
    :param list parts: Parts of the control
    :param list assessments: Assessments of the control
    :param list objectives: A list of OSCAL objective strings
    :param bool fedramp: Boolean - is a FedRAMP catalog
    :return: Formatted dictionary
    :rtype: dict
    """
    # process parts
    if "parts" in ctrl:
        # initialize
        str_parts = ""
        str_guidance = ""
        str_assessment = ""

        # create text field for human display
        str_parts += "<ul>"
        for dat in ctrl["parts"]:
            if (
                ("id" in dat)
                and (dat["name"].startswith("assessment") is False and dat["name"].startswith("assess") is False)
            ) or (
                ("id" in dat)
                and dat["name"]
                in [
                    "item",
                    "assessment-objective",
                    "statement",
                    "objective",
                    "overview",
                ]
            ):
                # check prose
                str_prose = ""
                if "prose" in dat:
                    str_prose = dat["prose"]

                # check name
                str_name = ""
                if "name" in dat:
                    str_name = dat["name"]

                # create the new part
                part = {
                    "id": 0,
                    "name": dat["id"],
                    "part_id": dat["id"].split("_")[0],
                    "objectiveType": str_name,
                    "description": (str_prose if str_prose else "Determine if the organization:"),
                    "parentControl": ctrl["id"],
                    "parentObjective": "",
                }

                # process statements and objectives
                if str_name in [
                    "assessment-objective",
                    "statement",
                    "objective",
                    "overview",
                ]:
                    parts.append(part)
                    try:
                        str_parts += LI + "{{" + dat["id"] + "}} - " + str_prose + LI_CLOSE
                    except Exception:
                        logger.error("Unable to parse part - %s.", dat["id"])
                    if "parts" in dat:
                        str_parts += process_objectives(dat["parts"], parts, ctrl, dat["id"], fedramp)

                # FedRAMP specific processing
                if fedramp:
                    process_fedramp_objectives(dat, "", objectives, ctrl)

                # process guidance
                if dat["name"] in ["guidance", "overview"]:
                    str_guidance = "<ul><li>Guidance</li>"
                    if "prose" in dat:
                        str_guidance += "<ul>"
                        str_guidance += LI + dat["prose"] + LI_CLOSE
                        str_guidance += UL_CLOSE
                    if "links" in dat:
                        str_guidance += "<ul>"
                        for lkp in dat["links"]:
                            str_guidance += LI + lkp["href"] + ", " + lkp["rel"] + LI_CLOSE
                        str_guidance += UL_CLOSE
                    str_guidance += UL_CLOSE
            else:
                # process assessments
                process_assessments(dat, ctrl, assessments)

        str_parts += UL_CLOSE
    else:
        # no parts - set default values
        str_parts = ""
        str_guidance = ""
        str_assessment = ""

    # return the result
    part_info = {
        "parts": str_parts,
        "guidance": str_guidance,
        "assessments": str_assessment,
    }
    return part_info


def process_assessments(dat: dict, ctrl: dict, assessments: list) -> None:
    """
    Process assessment data

    :param dict dat: Data to process
    :param dict ctrl: Controls
    :param list assessments: list of assessments
    :rtype: None
    """
    # process assessments
    if dat["name"].startswith("assessment") is True:
        # see if a lower level objective that has prose
        if "prose" in dat:
            # create new assessment objective
            ast = {
                "id": 0,
                "name": dat["id"],
                "testType": dat["name"],
                "description": dat["prose"],
                "parentControl": ctrl["id"],
            }

            # see if it has any child tests
            if "parts" in dat:
                if len(dat["parts"]) > 0:
                    for item in dat["parts"]:
                        process_assessments(item, ctrl, assessments)
        else:
            # check the id
            str_part_id = ""
            if "id" in dat:
                str_part_id = dat["id"]
            else:
                str_part_id = str(uuid.uuid4())

            # handle methods
            ast = {
                "id": 0,
                "name": str_part_id,
                "testType": "",
                "description": "",
                "parentControl": ctrl["id"],
            }
            props_data = dat.get("props", [{}])
            if "value" in props_data[0]:
                ast["testType"] = props_data[0]["value"]
            parts_data = dat.get("parts", [{}])
            if "prose" in parts_data[0]:
                ast["description"] = parts_data[0]["prose"]

        # add test of the array
        if ast["description"] != "":
            assessments.append(ast)
    elif dat["name"].startswith("assess") is True:
        # check the id
        str_part_id = ""
        if "id" in dat:
            str_part_id = dat["id"]
        else:
            str_part_id = str(uuid.uuid4())

        # handle methods
        ast = {
            "id": 0,
            "name": str_part_id,
            "testType": "",
            "description": "",
            "parentControl": ctrl["id"],
        }

        # check test type
        str_test_type = "TEST"
        props_data = dat.get("props", [{}])
        if "value" in props_data[0]:
            str_test_type = props_data[0]["value"]
        ast["testType"] = str_test_type

        # get the description
        str_description = ""
        parts_data = dat.get("parts", [{}])
        if "prose" in parts_data[0]:
            str_description = parts_data[0]["prose"]
        ast["description"] = str_description

        # add test of the array
        if ast["description"] != "":
            assessments.append(ast)


def oscal_version(metadata: dict) -> str:
    """
    Determine the oscal base version

    :param dict metadata: The metadata from OSCAL
    :raises ValueError: CLI support statement
    :return: The schema version
    :rtype: str
    """
    supported_versions = ["1.0.0", "1.0.2", "1.0.4", "1.1.1", "1.1.2"]
    oscal_schema = metadata["oscal-version"]
    if oscal_schema not in supported_versions:
        raise ValueError(
            f"The RegScale CLI does not support OSCAL version {oscal_schema}, only "
            f"versions {', '.join(supported_versions)} are supported."
        )
    logger.info("Oscal Version: %s", oscal_schema)
    return oscal_schema


def append_controls(
    oscal_controls: list,
    ctrl: Union[list, dict],
    resources: list,
    str_family: str,
    parameters: list,
    parts: list,
    assessments: list,
    objectives: list,
    fedramp: bool,
) -> list[dict]:
    """
    Process and append controls to list

    :param list oscal_controls: A list of oscal control dictionaries.
    :param Union[list, dict] ctrl: An OSCAL control dictionary or list
    :param list resources: resources of control
    :param str str_family: The name of the control family
    :param list parameters: A list of parameters dictionaries
    :param list parts: A list of OSCAL part strings.
    :param list assessments: A list of OSCAL assesment strings
    :param list objectives: A list of OSCAL objective strings
    :param bool fedramp: Boolean - is a FedRAMP catalog
    :return: list[dict]
    :rtype: list[dict]
    """
    new_ctrl = process_control(ctrl, resources, str_family, parameters, parts, assessments, objectives, fedramp)
    oscal_controls.append(new_ctrl)
    return oscal_controls
