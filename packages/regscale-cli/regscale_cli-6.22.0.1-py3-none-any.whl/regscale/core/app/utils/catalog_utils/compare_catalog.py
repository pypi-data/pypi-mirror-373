#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Enables comparison of catalogs from the master catalog list and the user's RegScale instance"""
import logging

# Standard Imports
import operator

import click  # type: ignore
import requests  # type: ignore

from regscale.core.app.api import Api
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import create_progress_object, error_and_exit
from regscale.core.app.utils.catalog_utils.common import get_new_catalog
from regscale.models.app_models.catalog_compare import CatalogCompare

# pylint: disable=line-too-long


def display_menu() -> None:
    """
    Start the process of comparing two catalogs, one from the master catalog list
    and one from the user's RegScale instance

    :rtype: None
    """
    # set environment and application configuration
    api = Api()
    api.timeout = 180

    # create logger function to log to the console
    job_progress = create_progress_object()
    logger = create_logger()
    menu_counter: list = []
    download_url: str = ""
    new_catalog: dict = {}
    # import master catalog list
    data = CatalogCompare.get_master_catalogs(api=api)
    # sort master catalogue list
    catalogues = data["catalogs"]
    catalogues.sort(key=operator.itemgetter("title"))
    for i, catalog in enumerate(catalogues):
        index = i + 1
        # print each catalog in the master catalog list
        print(f'{index}: {catalog["title"]}')
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
    with job_progress:
        # choose catalog to run diagnostics on
        for i, catalog in enumerate(catalogues):
            index = i + 1
            short_title = catalog["defaultName"]
            if index == value and catalog["downloadURL"]:
                cat_uuid = catalog["uuid"]
                download_url = catalog["downloadURL"]
                break

        # add task for retrieving new catalog
        retrieving_new_catalog = job_progress.add_task(
            f"[#f8b737]Retrieving selected catalog ({short_title}) from RegScale.com/resources.", total=1
        )
        # retrieve new catalog to run diagnostics on
        new_catalog = get_new_catalog(url=download_url)
        # update the task as complete
        job_progress.update(retrieving_new_catalog, advance=1)
        # add task for retrieving old catalog
        retrieving_old_catalog = job_progress.add_task(
            f"[#f8b737]Retrieving selected catalog ({short_title}) from RegScale application instance.",
            total=1,
        )
        # retrieve old catalog to run diagnostics on
        old_catalog = get_old_catalog(uuid_value=cat_uuid, api=api)
        # update the task as complete
        job_progress.update(retrieving_old_catalog, advance=1)
        # add task to run diagnostics on new catalog
        diagnosing_new_catalog = job_progress.add_task(
            "[#21a5bb]Running diagnostics on catalog from RegScale.com/resources.",
            total=1,
        )
        # run the diagnostics for the new selected catalog
        new_results = CatalogCompare.run_new_diagnostics(new_diagnose_cat=new_catalog)
        # update the task as complete
        job_progress.update(diagnosing_new_catalog, advance=1)
        # add task to run diagnostics on old catalog
        diagnosing_old_catalog = job_progress.add_task(
            "[#21a5bb]Running diagnosing on catalog from RegScale application instance.",
            total=1,
        )
        # run the diagnostics for the old selected catalog
        old_results = CatalogCompare.run_old_diagnostics(old_diagnose_cat=old_catalog)
        # update the task as complete
        job_progress.update(diagnosing_old_catalog, advance=1)
        # add task to compare catalogs
        comparing_catalogs = job_progress.add_task(
            "[#ef5d23]Performing comparison on output of complete catalog diagnostics.",
            total=1,
        )
        # compare catalog results
        compare_dicts_shallow(dict_1=new_results.dict(), dict_2=old_results.dict(), logger=logger)
        # update the task as complete
        job_progress.update(comparing_catalogs, advance=1)


def get_old_catalog(uuid_value: str, api: Api) -> dict:
    """
    Function to retrieve the old catalog from a RegScale instance via API & GraphQL

    :param str uuid_value: UUID of the catalog to retrieve
    :param Api api: API object
    :return: dictionary of the old catalog
    :rtype: dict
    """
    old_catalog_data = {}
    body = """
                query {
                    catalogues(
                        skip: 0
                        take: 50
                        where: { uuid: { eq: "uuid_value" } }
                    ) {
                        items {
                            title
                            uuid
                            keywords
                            securityControls {
                                id
                                objectives {
                                uuid
                                }
                                parameters {
                                uuid
                                }
                                cci {
                                uuid
                                }
                                tests {
                                uuid
                                }
                            }
                        }
                        pageInfo {
                        hasNextPage
                        }
                        totalCount
                    }
                    }
                    """.replace(
        "uuid_value", uuid_value
    )
    try:
        old_catalog_data = api.graph(query=body)["catalogues"]["items"][0]
    except (IndexError, KeyError):
        error_and_exit(f"Catalog with UUID: {uuid_value} not found in RegScale instance.")
    return old_catalog_data


def compare_dicts_shallow(dict_1: dict, dict_2: dict, logger: logging.Logger) -> None:
    """
    Function to compare two dictionaries and output the results

    :param dict dict_1: dictionary to compare
    :param dict dict_2: dictionary to compare
    :param logging.Logger logger: logger to use for console outputs
    :rtype: None
    """
    comparison = {
        "title": "Catalog Titles",
        "uuid": "Catalog UUIDs",
        "keywords": "Catalog Keywords",
        "cci_count": "CCI Counts",
        "objective_count": "Objective Counts",
        "parameter_count": "Parameter Counts",
        "security_control_count": "Security Control Counts",
        "test_count": "Test Counts",
    }
    for key, value in comparison.items():
        if dict_1.get(key) != dict_2.get(key):
            logger.info(f"{value} are not the same.")
        else:
            logger.info(f"{value} match.")
