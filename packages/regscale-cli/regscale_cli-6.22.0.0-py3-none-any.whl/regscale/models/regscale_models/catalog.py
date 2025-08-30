#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Model for Catalog in the application"""
from __future__ import annotations

import io
import json
import warnings
from typing import List, Optional, Union
from urllib.parse import urljoin

from pydantic import ConfigDict
from requests import Response

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.api_handler import APIRetrieveError
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models.regscale_models.security_control import SecurityControl


class Catalog(RegScaleModel):
    """Catalog class"""

    _module_slug = "catalogues"

    id: int = 0
    abstract: Optional[str] = None
    datePublished: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    lastRevisionDate: Optional[str] = None
    title: str = ""
    url: Optional[str] = None
    tenantsId: Optional[int] = None
    uuid: Optional[str] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    lastUpdatedById: Optional[str] = None
    master: bool = False
    sourceOscalURL: Optional[str] = None
    archived: bool = False
    isPublic: bool = True
    securityControls: List[SecurityControl] = []

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Catalogues model

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_count="/api/{model_slug}/getCount",
            get_list="/api/{model_slug}/getList",
            get_catalog_with_all_details="/api/{model_slug}/getCatalogWithAllDetails/{intID}",
            filter_catalogues="/api/{model_slug}/filterCatalogues",
            graph="/api/{model_slug}/graph",
            convert_mappings="/api/{model_slug}/convertMappings/{intID}",
            find_by_guid="/api/{model_slug}/findByGUID/{strID}",
            get_titles="/api/{model_slug}/getTitles",
            get_nist="/api/{model_slug}/getNIST",
            get_updatable="/api/{model_slug}/getUpdatableCatalogs",
            compare_and_update="/api/{model_slug}/compareAndUpdate/{intID}",
            update_regscale_catalog="/api/{model_slug}/updateRegScaleCatalog/{intID}",
            get_update_report_for_catalog="/api/{model_slug}/getUpdateReportForCatalog/{intID}",
        )

    @classmethod
    def get_list(cls) -> List["Catalog"]:
        """
        Use the get_list method instead.

        Get all catalogs from database

        :return: list of catalogs
        :rtype: List["Catalog"]
        """
        return cls._handle_list_response(cls._get_api_handler().get(cls.get_endpoint("get_list")))

    def insert_catalog(self, app: Application) -> "Catalog":  # noqa
        """
        DEPRECATED: This method is deprecated and will be removed in a future version.
        Use the create method instead.

        Insert catalog into database

        :param Application app: Application
        :return: Newly created catalog object
        :rtype: Catalog
        """
        warnings.warn(
            "insert_catalog is deprecated and will be removed in a future version. Use create method instead.",
            DeprecationWarning,
        )
        # Convert the model to a dictionary
        return self.create()

    @staticmethod
    def get_catalogs(app: Application) -> list:
        """
        DEPRECATED: This method is deprecated and will be removed in a future version.
        Use the get_list method instead.

        Get all catalogs from database

        :param Application app: Application
        :raises APIRetrieveError: API request failed
        :return: list of catalogs
        :rtype: list
        """
        warnings.warn(
            "get_catalogs is deprecated and will be removed in a future version. Use get_list method instead.",
            DeprecationWarning,
        )
        api = Api()
        api_url = urljoin(app.config["domain"], "/api/catalogues")
        response = api.get(api_url)
        if not response.ok:
            api.logger.debug(
                f"API request failed with status: {response.status_code}: {response.reason} {response.text}"
            )
            raise APIRetrieveError(f"API request failed with status {response.status_code}")
        return response.json()

    @classmethod
    def get_with_all_details(cls, catalog_id: int) -> Optional[dict]:
        """
        Retrieves a catalog with all details by its ID.

        :param int catalog_id: The ID of the catalog
        :return: The response from the API or None
        :rtype: Optional[dict]
        """
        endpoint = cls.get_endpoint("get_catalog_with_all_details").format(
            model_slug=cls.get_module_slug(), intID=catalog_id
        )
        response = cls._get_api_handler().get(endpoint)

        if response and response.ok and response.status_code not in [204, 404]:
            return response.json()
        return {}

    @classmethod
    def get_update_report_for_catalog(
        cls,
        catalog_id: int,
    ) -> Response:
        """ """
        endpoint = cls.get_endpoint("get_update_report_for_catalog").format(
            model_slug=cls.get_module_slug(),
            intID=catalog_id,
        )
        response = cls._get_api_handler().get(endpoint)

        return response

    @classmethod
    def get_updatable_catalogs(cls) -> Optional[list]:
        """
        Get updatable catalogues

        :return: List of updatable catalogues
        :rtype: Optional[list]
        """

        endpoint = cls.get_endpoint("get_updatable").format(model_slug=cls.get_module_slug())
        response = cls._get_api_handler().get(endpoint)
        if (
            response
            and response.ok
            and response.status_code
            not in [
                204,
                404,
            ]
        ):
            return response.json()
        return None

    @classmethod
    def update_regscale_catalog(
        cls,
        catalog_id: int,
    ) -> Union[Response | list]:
        """
        Update a regscale catalog

        :param int catalog_id: The ID of the catalog
        :return: A Response object
        :rtype: Union[Response | list]
        """

        endpoint = cls.get_endpoint("update_regscale_catalog").format(
            model_slug=cls.get_module_slug(),
            intID=catalog_id,
        )
        response = cls._get_api_handler().put(endpoint=endpoint)  # data is optional here, not needed for this.
        if (
            response
            and response.ok
            and response.status_code
            not in [
                204,
                404,
            ]
        ):
            return response.json()
        return response

    @classmethod
    def compare_and_update(
        cls,
        new_catalog: dict,
        catalog_id: int,
        format: str = "json",
        structure: str = "flatReport",
        apply_updates: bool = False,
    ) -> Response:
        """
        Get updatable catalogues

        :param dict new_catalog: The new catalog to compare
        :param int catalog_id: The ID of the catalog
        :param str format: The format of the catalog
        :param str structure: The structure of the catalog
        :param bool apply_updates: Whether to apply updates
        :return: List of updatable catalogues
        :rtype: Response
        """
        bytes_object = json.dumps(new_catalog).encode("utf-8")
        files = {"newCatalogFile": io.BytesIO(bytes_object)}
        # convert files to bytes like object
        endpoint = cls.get_endpoint("compare_and_update").format(
            model_slug=cls.get_module_slug(),
            intID=catalog_id,
            format=format,
            structure=structure,
            apply_updates=apply_updates,
        )
        params = {
            "format": format.lower(),
            "structure": structure,
            "applyUpdates": apply_updates,
        }
        response = cls._get_api_handler().post(endpoint=endpoint, files=files, params=params)

        if (
            response
            and response.ok
            and response.status_code
            not in [
                204,
                404,
            ]
        ):
            return response
        cls.log_response_error(response, suppress_error=True)
        return response

    @classmethod
    def find_by_guid(cls, guid: str) -> Optional["Catalog"]:
        """
        Find a catalog by its GUID.

        :param str guid: The GUID of the catalog
        :return: The catalog object or None if not found
        :rtype: Optional["Catalog"]
        """
        endpoint = cls.get_endpoint("find_by_guid").format(model_slug=cls.get_module_slug(), strID=guid)
        response = cls._get_api_handler().get(endpoint)

        if response and response.ok and response.status_code not in [204, 404]:
            return cls(**response.json())
        return None
