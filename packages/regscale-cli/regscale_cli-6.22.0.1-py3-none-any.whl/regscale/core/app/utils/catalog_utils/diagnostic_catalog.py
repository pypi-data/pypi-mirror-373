#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add functionality to diagnose catalog via API."""

# Standard Imports
import logging
import operator
from typing import Optional

import click  # type: ignore
import requests  # type: ignore
from pathlib import Path

from regscale.core.app.utils.app_utils import save_data_to
from regscale.core.app.utils.catalog_utils.common import get_new_catalog
from regscale.models.app_models.catalog_compare import CatalogCompare


def display_menu() -> None:
    """
    Display menu for catalog diagnostic and start the diagnostic process

    :rtype: None
    """
    # set environment and application configuration
    from regscale.core.app.api import Api

    api = Api()
    api.timeout = 180

    # create logger function to log to the console
    logger = api.logger
    menu_counter: list = []
    download_url: str = ""
    # import master catalog list
    data = CatalogCompare.get_master_catalogs(api=api)
    # sort master catalogue list
    catalogues = data["catalogs"]
    catalogues.sort(key=operator.itemgetter("title"))
    for i, catalog in enumerate(catalogues):
        index = i + 1
        # print each catalog in the master catalog list
        print(f'{index}: {catalog["title"]}')
        menu_counter.append(index)
    # set status to False to run loop
    status: bool = False
    value: Optional[int] = None
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
    for i, catalog in enumerate(catalogues):
        index = i + 1
        if index == value and catalog["downloadURL"]:
            download_url = catalog["downloadURL"]
            break
    # retrieve new catalog to run diagnostics on
    new_catalog = get_new_catalog(url=download_url)
    # run the diagnostic output for the selected catalog
    save_data_to(
        file=Path("diagnostics.json"),
        data=run_diagnostics(diagnose_cat=new_catalog, logger=logger).dict(),
    )


def run_diagnostics(diagnose_cat: dict, logger: logging.Logger) -> CatalogCompare:
    """
    Function to run diagnostics on a catalog

    :param dict diagnose_cat: dictionary of a catalog to run diagnostics on
    :param logging.Logger logger: Logger to log to the console
    :return: CatalogCompare object
    :rtype: CatalogCompare
    """
    diagnostic_results = CatalogCompare().run_new_diagnostics(diagnose_cat)

    # print information to the terminal
    logger.info("The catalog you have selected for diagnostics is:")
    logger.info(diagnostic_results.title)
    logger.info("The uuid for this catalog is:")
    logger.info(diagnostic_results.uuid)
    logger.info("The list of contained keywords in this catalog is:")
    logger.info(diagnostic_results.keywords)
    logger.info(f"The number of CCIs in this catalog is: {diagnostic_results.cci_count}")
    logger.info(f"The number of Objectives in this catalog is: {diagnostic_results.objective_count}")
    logger.info(f"The number of Parameters in this catalog is: {diagnostic_results.parameter_count}")
    logger.info(f"The number of Security Controls in this catalog is: {diagnostic_results.security_control_count}")
    logger.info(f"The number of Tests in this catalog is: {diagnostic_results.test_count}")
    return diagnostic_results
