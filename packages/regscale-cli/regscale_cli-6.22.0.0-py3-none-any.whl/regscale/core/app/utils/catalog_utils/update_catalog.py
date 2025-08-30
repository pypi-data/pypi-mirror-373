#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add functionality to upgrade application catalog information via API."""


# pylint: disable=line-too-long, global-statement, global-at-module-level, abstract-class-instantiated, too-many-lines

# Standard Imports
import contextlib
import operator
import sys
from typing import Optional, Tuple

import click  # type: ignore
from requests import JSONDecodeError  # type: ignore

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import create_progress_object, error_and_exit
from regscale.core.app.utils.catalog_utils.common import get_new_catalog
from regscale.models.app_models.catalog_compare import CatalogCompare

# create logger function to log to the console
logger = create_logger()
# create progress object
job_progress = create_progress_object()

DOWNLOAD_URL: str = ""
CAT_UUID: str = ""
SECURITY_CONTROL_ID_KEY: list = []


def display_menu() -> None:
    """
    Start the process of comparing two catalogs, one from the master catalog list
    and one from the user's RegScale instance

    :rtype: None
    """
    # set system environment variables
    api = Api()
    api.timeout = 180

    # start menu build process
    menu_counter: list = []
    # import master catalog list
    data = CatalogCompare.get_master_catalogs(api=api)
    # sort master catalogue list
    catalogues = data["catalogues"]
    catalogues.sort(key=operator.itemgetter("id"))
    for i, catalog in enumerate(catalogues):
        # print each catalog in the master catalog list
        print(f'{catalog["id"]}: {catalog["value"]}')
        menu_counter.append(i)
    # set status to False to run loop
    status: bool = False
    while not status:
        # select catalog to run diagnostic
        value = click.prompt(
            "Please enter the number of the catalog you would like to run diagnostics on",
            type=int,
        )
        # check if value exist that is selected
        if value < min(menu_counter) or value > max(menu_counter):
            print("That is not a valid selection, please try again")
        else:
            status = True
        # choose catalog to run diagnostics on
        for catalog in catalogues:
            if catalog["id"] == value:
                global CAT_UUID
                CAT_UUID = catalog["metadata"]["uuid"]
                if catalog["download"] is True:
                    if catalog["paid"] is False:
                        global DOWNLOAD_URL
                        DOWNLOAD_URL = catalog["link"]
                    if catalog["paid"] is True:
                        logger.warning("This is a paid catalog, please contact RegScale customer support.")
                        sys.exit()
                break
    compare_and_update_catalog_elements(api=api)


def compare_and_update_catalog_elements(api: Api) -> None:
    """
    Function to compare and update elements between catalogs

    :param Api api: Api object
    :rtype: None
    """
    new_catalog_elements = parse_new_catalog()
    old_catalog_elements = parse_old_catalog(api=api)
    update_security_controls(
        new_security_controls=new_catalog_elements[0],
        old_security_controls=old_catalog_elements[0],
        api=api,
    )
    update_ccis(
        new_ccis=new_catalog_elements[1],
        old_ccis=old_catalog_elements[1],
        api=api,
    )
    update_objectives(
        new_objectives=new_catalog_elements[2],
        old_objectives=old_catalog_elements[2],
        api=api,
    )
    update_parameters(
        new_parameters=new_catalog_elements[3],
        old_parameters=old_catalog_elements[3],
        api=api,
    )
    update_tests(
        new_tests=new_catalog_elements[4],
        old_tests=old_catalog_elements[4],
        api=api,
    )


def update_security_controls(new_security_controls: list[dict], old_security_controls: list[dict], api: Api) -> None:
    """
    Function to compare and update security controls

    :param list[dict] new_security_controls: security controls from new catalog
    :param list[dict] old_security_controls: security controls from old catalog
    :param Api api: api object
    :rtype: None
    """
    archived_list = []
    updated_list = []
    created_list = []
    element_exists = False
    for new_security_control in new_security_controls:
        for old_security_control in old_security_controls:
            if new_security_control.get("controlId") == old_security_control.get("controlId"):
                key_dict = {
                    "old_sc_id": old_security_control["id"],
                    "new_sc_id": new_security_control["id"],
                }
                SECURITY_CONTROL_ID_KEY.append(key_dict)
                element_exists = True
                with contextlib.suppress(KeyError):
                    if new_security_control["archived"] is True:
                        old_security_control["archived"] = True
                        archived_list.append(old_security_control)
                        break
                for key in old_security_control:
                    try:
                        if key not in [
                            "id",
                            "catalogueID",
                            "tenantsId",
                            "sortId",
                            "lastUpdatedById",
                        ]:
                            old_security_control[key] = new_security_control[key]
                        else:
                            continue
                    except KeyError:
                        old_security_control["archived"] = False
                update = api.put(
                    url=api.config["domain"] + f"/api/SecurityControls/{old_security_control['id']}",
                    json=old_security_control,
                )
                update.raise_for_status()
                if update.ok:
                    logger.info(
                        "Updated Security Control for Control ID: %i",
                        old_security_control["id"],
                    )
                    updated_list.append(old_security_control)
        if element_exists is False:
            try:
                new_security_control["catalogueID"] = old_security_controls[0]["controls"]["catalogueID"]
            except KeyError:
                new_security_control["catalogueID"] = old_security_controls[0]["catalogueID"]
            create = api.post(
                url=api.config["domain"] + "/api/SecurityControls",
                json=new_security_control,
            )
            create.raise_for_status()
            if create.ok:
                logger.info(
                    "Created Security Control for Control ID: %i",
                    new_security_control["id"],
                )
                created_list.append(new_security_control)
    data_report(
        data_name="SecurityControls",
        archived=archived_list,
        updated=updated_list,
        created=created_list,
    )


def update_ccis(new_ccis: list[dict], old_ccis: list[dict], api: Api) -> None:
    """
    Function to compare and update ccis

    :param list[dict] new_ccis: ccis from new catalog
    :param list[dict] old_ccis: ccis from old catalog
    :param Api api: api object
    :rtype: None
    """
    archived_list = []
    updated_list = []
    created_list = []
    element_exists = False
    for new_cci in new_ccis:
        for old_cci in old_ccis:
            for cci in old_cci:
                if new_cci["name"] == cci["name"]:
                    element_exists = True
                    with contextlib.suppress(KeyError):
                        if new_cci["archived"] is True:
                            cci["archived"] = True
                            archived_list.append(cci)
                            break
                    for key in cci:
                        if key == "isPublic":
                            cci["isPublic"] = False
                        elif key not in ["id", "securityControlId"]:
                            cci[key] = new_cci[key]
                        else:
                            continue
                    key_set = next(
                        (item for item in SECURITY_CONTROL_ID_KEY if item["new_sc_id"] == new_cci["securityControlId"]),
                        None,
                    )
                    old_sc_id = key_set.get("old_sc_id")
                    cci["securityControlId"] = old_sc_id
                    update = api.put(
                        url=api.config["domain"] + f"/api/cci/{cci['id']}",
                        json=cci,
                    )
                    update.raise_for_status()
                    if update.ok:
                        logger.info(
                            "Updated CCI for CCI ID: %i",
                            cci["id"],
                        )
                        updated_list.append(cci)
        if element_exists is False:
            key_set = next(
                (item for item in SECURITY_CONTROL_ID_KEY if item["new_sc_id"] == new_cci["securityControlId"]),
                None,
            )
            old_sc_id = key_set.get("old_sc_id")
            new_cci["securityControlId"] = old_sc_id
            create = api.post(
                url=api.config["domain"] + "/api/cci",
                json=new_cci,
            )
            create.raise_for_status()
            if create.ok:
                logger.info(
                    "Created CCI for CCI ID: %i",
                    new_cci["id"],
                )
                created_list.append(new_cci)
    data_report(
        data_name="CCIs",
        archived=archived_list,
        updated=updated_list,
        created=created_list,
    )


def update_objectives(new_objectives: list[dict], old_objectives: list[dict], api: Api) -> None:
    """
    Function to compare and update objectives

    :param list[dict] new_objectives: objectives from new catalog
    :param list[dict] old_objectives: objectives from old catalog
    :param Api api: Api object
    :rtype: None
    """
    archived_list = []
    updated_list = []
    created_list = []
    element_exists = False
    for new_objective in new_objectives:
        for old_objective in old_objectives:
            if new_objective["name"] == old_objective["name"]:
                element_exists = True
                with contextlib.suppress(KeyError):
                    if new_objective["archived"] is True:
                        old_objective["archived"] = True
                        archived_list.append(old_objective)
                        break
                for key in old_objective:
                    if key == "isPublic":
                        old_objective["isPublic"] = False
                    elif key not in ["id", "securityControlId", "tenantsId"]:
                        old_objective[key] = new_objective[key]
                    else:
                        continue
                key_set = next(
                    (
                        item
                        for item in SECURITY_CONTROL_ID_KEY
                        if item["new_sc_id"] == new_objective["securityControlId"]
                    ),
                    None,
                )
                old_sc_id = key_set.get("old_sc_id")
                old_objective["securityControlId"] = old_sc_id
                if old_objective.get("tenantsId") is not None:
                    del old_objective["tenantsId"]
                update = api.put(
                    url=api.config["domain"] + f"/api/controlObjectives/{old_objective['id']}",
                    json=old_objective,
                )
                update.raise_for_status()
                if update.ok:
                    logger.info(
                        "Updated Objective for Objective ID: %i",
                        old_objective["id"],
                    )
                    updated_list.append(old_objective)
        if element_exists is False:
            key_set = next(
                (item for item in SECURITY_CONTROL_ID_KEY if item["new_sc_id"] == new_objective["securityControlId"]),
                None,
            )
            old_sc_id = key_set.get("old_sc_id")
            new_objective["securityControlId"] = old_sc_id
            create = api.post(
                url=api.config["domain"] + "/api/controlObjectives",
                json=new_objective,
            )
            create.raise_for_status()
            if create.ok:
                logger.info(
                    "Created Objective for Objective ID: %i",
                    new_objective["id"],
                )
                created_list.append(new_objective)
    data_report(
        data_name="Objectives",
        archived=archived_list,
        updated=updated_list,
        created=created_list,
    )


def parse_parameters(data: dict) -> dict:
    """
    Function to parse keys from the provided dictionary

    :param dict data: parameters from catalog
    :return: dictionary with parsed keys
    :rtype: dict
    """
    for key in data:
        if key == "isPublic":
            data["isPublic"] = False
        elif key == "default":
            data["default"] = None
        elif key == "dataType":
            data["dataType"] = None
        elif key != "id" or key != "securityControlId":
            continue
    return data


def update_parameters(new_parameters: list[dict], old_parameters: list[dict], api: Api) -> None:
    """
    Function to compare and update parameters

    :param list[dict] new_parameters: parameters from new catalog
    :param list[dict] old_parameters: parameters from old catalog
    :param Api api: Api object
    :rtype: None
    """
    archived_list = []
    updated_list = []
    created_list = []
    element_exists = False
    for new_parameter in new_parameters:
        for old_parameter in old_parameters:
            if new_parameter["parameterId"] == old_parameter["parameterId"]:
                element_exists = True
                with contextlib.suppress(KeyError):
                    if new_parameter["archived"] is True:
                        old_parameter["archived"] = True
                        archived_list.append(old_parameter)
                        break
                old_parameter = parse_parameters(old_parameter)
                key_set = next(
                    (
                        item
                        for item in SECURITY_CONTROL_ID_KEY
                        if item["new_sc_id"] == new_parameter["securityControlId"]
                    ),
                    None,
                )
                old_sc_id = key_set.get("old_sc_id")
                old_parameter["securityControlId"] = old_sc_id
                update = api.put(
                    url=api.config["domain"] + f"/api/controlParameters/{old_parameter['id']}",
                    json=old_parameter,
                )
                update.raise_for_status()
                if update.ok:
                    logger.info(
                        "Updated Parameter for Parameter ID: %i",
                        old_parameter["id"],
                    )
                    updated_list.append(old_parameter)
        if element_exists is False:
            key_set = next(
                (item for item in SECURITY_CONTROL_ID_KEY if item["new_sc_id"] == new_parameter["securityControlId"]),
                None,
            )
            old_sc_id = key_set.get("old_sc_id")
            new_parameter["securityControlId"] = old_sc_id
            create = api.post(
                url=api.config["domain"] + "/api/controlParameters",
                json=new_parameter,
            )
            create.raise_for_status()
            if create.ok:
                logger.info(
                    "Created Parameter for Parameter ID: %i",
                    new_parameter["id"],
                )
                created_list.append(new_parameter)
    data_report(
        data_name="Parameters",
        archived=archived_list,
        updated=updated_list,
        created=created_list,
    )


def update_tests(new_tests: list[dict], old_tests: list[dict], api: Api) -> None:
    """
    Function to compare and update tests

    :param list[dict] new_tests: tests from new catalog
    :param list[dict] old_tests: tests from old catalog
    :param Api api: API Object
    :rtype: None
    """
    archived_list = []
    updated_list = []
    created_list = []
    element_exists = False
    for new_test in new_tests:
        for old_test in old_tests:
            if new_test["testId"] == old_test["testId"]:
                element_exists = True
                with contextlib.suppress(KeyError):
                    if new_test["archived"] is True:
                        old_test["archived"] = True
                        archived_list.append(old_test)
                        break
                for key in old_test:
                    if key == "isPublic":
                        old_test["isPublic"] = False
                    elif key not in ["id", "securityControlId", "tenantsId"]:
                        old_test[key] = new_test[key]
                    else:
                        continue
                key_set = next(
                    (item for item in SECURITY_CONTROL_ID_KEY if item["new_sc_id"] == new_test["securityControlId"]),
                    None,
                )
                old_sc_id = key_set.get("old_sc_id")
                old_test["securityControlId"] = old_sc_id
                update = api.put(
                    url=api.config["domain"] + f"/api/controlTestPlans/{old_test['id']}",
                    json=old_test,
                )
                update.raise_for_status()
                if update.ok:
                    logger.info(
                        "Updated test for test ID: %i",
                        old_test["id"],
                    )
                    updated_list.append(old_test)
        if element_exists is False:
            key_set = next(
                (item for item in SECURITY_CONTROL_ID_KEY if item["new_sc_id"] == new_test["securityControlId"]),
                None,
            )
            old_sc_id = key_set.get("old_sc_id")
            new_test["securityControlId"] = old_sc_id
            create = api.post(
                url=api.config["domain"] + "/api/controlTestPlans",
                json=new_test,
            )
            create.raise_for_status()
            if create.ok:
                logger.info(
                    "Created test for test ID: %i",
                    new_test["id"],
                )
                created_list.append(new_test)
    data_report(
        data_name="Tests",
        archived=archived_list,
        updated=updated_list,
        created=created_list,
    )


def parse_new_catalog() -> Tuple[list, list, list, list, list]:
    """
    Function to parse elements from the new catalog

    :return: Tuple containing lists of new catalog data elements
    :rtype: Tuple[list, list, list, list, list]
    """
    with job_progress:
        # add task for retrieving new catalog
        retrieving_new_catalog = job_progress.add_task(
            "[#f8b737]Retrieving selected catalog from RegScale.com/regulations.",
            total=6,
        )
        # retrieve new catalog to run diagnostics on
        new_catalog = get_new_catalog(url=DOWNLOAD_URL)
        # update the task as complete
        job_progress.update(retrieving_new_catalog, advance=1)
        # retrieve new catalog security controls
        new_security_controls = parse_dict_and_sublevel(
            data=new_catalog,
            key="catalogue",
            sub_key="securityControls",
            del_key="tenantsId",
        )
        # update the task as complete
        job_progress.update(retrieving_new_catalog, advance=1)
        # retrieve new catalog ccis
        new_ccis = parse_dict_and_sublevel(data=new_catalog, key="catalogue", sub_key="ccis")
        # update the task as complete
        job_progress.update(retrieving_new_catalog, advance=1)
        # retrieve new catalog objectives
        new_objectives = parse_dict_and_sublevel(data=new_catalog, key="catalogue", sub_key="objectives")
        # update the task as complete
        job_progress.update(retrieving_new_catalog, advance=1)
        # retrieve new catalog parameters
        new_parameters = parse_dict_and_sublevel(data=new_catalog, key="catalogue", sub_key="parameters")
        # update the task as complete
        job_progress.update(retrieving_new_catalog, advance=1)
        # retrieve new catalog tests
        new_tests = parse_dict_and_sublevel(data=new_catalog, key="catalogue", sub_key="tests")
        # update the task as complete
        job_progress.update(retrieving_new_catalog, completed=6)
    return new_security_controls, new_ccis, new_objectives, new_parameters, new_tests


def parse_old_catalog(api: Api) -> Tuple[list, list, list, list, list]:
    """
    Function to parse elements from the old catalog

    :param Api api: RegScale API object
    :return: Tuple containing lists of old catalog elements
    :rtype: Tuple[list, list, list, list, list]
    """
    with job_progress:
        # add task for retrieving old catalog
        retrieving_old_catalog = job_progress.add_task(
            "[#ef5d23]Retrieving selected catalog from RegScale application instance.",
            total=5,
        )
        # retrieve old catalog security controls
        security_controls = parse_controls(api=api)
        old_security_controls = security_controls[0]
        # update the task as complete
        job_progress.update(retrieving_old_catalog, advance=1)
        # retrive old catalog ccis
        old_ccis = security_controls[4]
        # update the task as complete
        job_progress.update(retrieving_old_catalog, advance=1)
        # retrieve old catalog objectives
        old_objectives = security_controls[2]
        # update the task as complete
        job_progress.update(retrieving_old_catalog, advance=1)
        # retrieve old catalog parameters
        old_parameters = security_controls[1]
        # update the task as complete
        job_progress.update(retrieving_old_catalog, advance=1)
        # retrieve old catalog tests
        old_tests = security_controls[3]
        # update the task as complete
        job_progress.update(retrieving_old_catalog, advance=1)

    return old_security_controls, old_ccis, old_objectives, old_parameters, old_tests


def parse_dict_and_sublevel(data: dict, key: str, sub_key: str, del_key: Optional[str] = None) -> list:
    """
    Function to parse a dictionary and retrieve data from the sublevel dictionary key

    :param dict data: dictionary to parse
    :param str key: key to be extracted from the dictionary
    :param str sub_key: the sub-level key being looked for
    :param Optional[str] del_key: the sub-level key to delete, defaults to None
    :return: a list containing the parsed data elements
    :rtype: list
    """
    parse_list = []
    with contextlib.suppress(KeyError):
        parse_list.extend(iter(data[key][sub_key]))
        if del_key:
            for parsed_item in parse_list:
                del parsed_item[del_key]
    return parse_list


def data_report(data_name: str, archived: list, updated: list, created: list) -> None:
    """Creates output data report for changed data elements in the catalog

    :param str data_name: catalog data element being updated
    :param list archived: archived data elements
    :param list updated: updated data elements
    :param list created: created data elements
    :rtype: None
    """
    import pandas as pd  # Optimize import performance

    archived_data = pd.DataFrame.from_dict(archived)
    updated_data = pd.DataFrame.from_dict(updated)
    created_data = pd.DataFrame.from_dict(created)
    with pd.ExcelWriter(f"{data_name}.xlsx") as writer:
        archived_data.to_excel(writer, sheet_name="Archived", index=False)
        updated_data.to_excel(writer, sheet_name="Updated", index=False)
        created_data.to_excel(writer, sheet_name="Created", index=False)


def get_old_security_controls(uuid_value: str, api: Api) -> list[dict]:
    """
    Function to retrieve the old catalog security controls from a RegScale instance via API & GraphQL

    :param str uuid_value: UUID of the catalog to retrieve
    :param Api api: RegScale API object
    :return: a list containing security controls
    :rtype: list[dict]
    """
    body = """
                query {
                    catalogues(
                        skip: 0
                        take: 50
                        where: { uuid: { eq: "uuid_value" } }
                    ) {
                        items {
                        id
                        }
                        pageInfo {
                        hasNextPage
                        }
                        totalCount
                    }
                    }""".replace(
        "uuid_value", uuid_value
    )
    try:
        catalogue_id = api.graph(query=body)["catalogues"]["items"][0]["id"]
    except (IndexError, KeyError):
        error_and_exit(f"Catalog with UUID: {uuid_value} not found in RegScale instance.")
    try:
        old_security_controls = api.get(
            url=api.config["domain"] + f"/api/SecurityControls/getAllByCatalogWithDetails/{catalogue_id}"
        ).json()
        if len(old_security_controls) == 0:
            error_and_exit("This catalog does not currently exist in the RegScale application")
    except JSONDecodeError as ex:
        error_and_exit(f"Unable to retrieve control objectives from RegScale.\n{ex}")
    except TimeoutError:
        error_and_exit("The selected catalog is too large to update, please contact RegScale customer service.")
    return old_security_controls


def parse_controls(
    api: Api,
) -> Tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
    """
    Function to retrieve the old catalog security controls from a RegScale instance via API & GraphQL

    :param Api api: RegScale API object
    :return: a tuple containing a list for each catalog element
    :rtype: Tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]
    """
    old_security_controls = get_old_security_controls(uuid_value=CAT_UUID, api=api)
    parsed_old_security_controls = []
    for old_control in old_security_controls:
        parsed_old_security_controls.append(old_control["control"])
    old_parameters = []
    for control in old_security_controls:
        for parameter in control["parameters"]:
            old_parameters.append(parameter)
    old_objectives = []
    for control in old_security_controls:
        for objective in control["objectives"]:
            old_objectives.append(objective)
    old_tests = []
    for control in old_security_controls:
        for test in control["tests"]:
            old_tests.append(test)
    old_ccis = []
    for control in old_security_controls:
        id_number = control["control"]["id"]
        try:
            ccis = api.get(url=api.config["domain"] + f"/api/cci/getByControl/{id_number}").json()
            if ccis:
                old_ccis.append(ccis)
        except JSONDecodeError as ex:
            error_and_exit(f"Unable to retrieve control objectives from RegScale.\n{ex}")
    return (
        parsed_old_security_controls,
        old_parameters,
        old_objectives,
        old_tests,
        old_ccis,
    )
