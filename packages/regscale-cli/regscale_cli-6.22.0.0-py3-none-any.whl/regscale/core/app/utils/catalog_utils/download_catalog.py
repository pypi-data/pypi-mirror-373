#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add functionality to download a catalog via API."""
import json.decoder

# Standard Imports
import operator
from pathlib import Path
from typing import Optional, Tuple

import click  # type: ignore
import requests  # type: ignore

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import save_data_to
from regscale.core.app.utils.catalog_utils.common import get_new_catalog, is_valid_url
from regscale.models.app_models.catalog_compare import CatalogCompare

MENU_COUNTER: list = []


def pull_catalogs() -> list[dict]:
    """
    Function to pull the master catalogs from the API

    :rtype: list[dict]
    :return: The list of master catalogs
    """
    api = Api()
    data = CatalogCompare.get_master_catalogs(api=api)
    # sort master catalog list
    catalogues = data["catalogs"]
    catalogues.sort(key=operator.itemgetter("title"))
    return catalogues


def display_menu(show_menu: bool) -> int:
    """
    Function to display the menu for the catalog export and handle exporting the selected catalog

    :param bool show_menu: Show the menu
    :rtype: int
    :return: The max index + 1 of the menu (one based for real world)
    """
    api = Api()
    catalogues = pull_catalogs()
    # set environment and application configuration
    api.timeout = 180
    # import master catalog list
    for i, catalog in enumerate(catalogues):
        if show_menu:
            print(f'{i + 1}: {catalog["title"]}')
        MENU_COUNTER.append(i)
    return max(MENU_COUNTER)


def select_catalog(catalog_index: int, logging: bool = True) -> Tuple[dict, dict]:
    """
    Function to download the selected catalog

    :param int catalog_index: Index of the selected catalog
    :param bool logging: Enable logging
    :rtype: Tuple[dict, dict]
    :return: The new catalog as a dictionary and the registry dict of the selected catalog
    """
    catalogues = pull_catalogs()
    new_catalog = None
    registry_item = None
    app = Application()
    logger = app.logger
    status: bool = False
    value: Optional[int] = None
    download_url: str = ""
    catalog_name: str = ""
    while not status:
        if catalog_index == 0:
            value = click.prompt(
                "Please enter the number of the catalog you would like to download",
                type=int,
            )
        else:
            value = catalog_index
        if MENU_COUNTER and value < min(MENU_COUNTER) or MENU_COUNTER and value > max(MENU_COUNTER):
            print("That is not a valid selection, please try again")
        else:
            status = True
    # Choose catalog to export
    for i, catalog in enumerate(catalogues):
        if i + 1 == value and catalog["url"]:
            registry_item = catalog
            download_url = catalog["downloadURL"].strip()
            logger.debug("ix+1: %i, URL: %s", i + 1, download_url)
            catalog_name = catalog["defaultName"].replace(" ", "_")
            break
    if is_valid_url(download_url):
        new_catalog = get_new_catalog(url=download_url)
        save_data_to(
            file=Path(f"{catalog_name}.json"),
            data=new_catalog,
            output_log=logging,
        )
    return new_catalog, registry_item
