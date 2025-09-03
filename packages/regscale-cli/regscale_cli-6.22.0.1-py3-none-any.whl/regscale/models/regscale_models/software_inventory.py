#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for SoftwareInventory in the application"""

from typing import List, Optional, cast

from pydantic import ConfigDict, Field

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models.regscale_model import RegScaleModel


class SoftwareInventory(RegScaleModel):
    """
    SoftwareInventory
    """

    _module_slug = "softwareInventory"
    _unique_fields = [
        ["name", "version", "parentHardwareAssetId"],
    ]
    _parent_id_field = "parentHardwareAssetId"

    # UUID: Optional[str] = None
    name: str
    version: Optional[str] = None
    function: Optional[str] = None
    patchLevel: Optional[str] = None
    parentHardwareAssetId: Optional[int] = None
    parentSoftwareAssetId: Optional[int] = None
    # parentSoftwareInventoryId: Optional[int] = None
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)
    lastUpdatedById: str = Field(default_factory=RegScaleModel.get_user_id)
    isPublic: bool = True
    # references: Optional[List[str]] = []

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        return ConfigDict(
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}",
            batch_create="/api/{model_slug}/batchCreate",
            batch_update="/api/{model_slug}/batchUpdate",
        )

    def __eq__(self, other: "SoftwareInventory") -> bool:
        """
        Override the default Equals behavior

        :param SoftwareInventory other: SoftwareInventory to compare
        :return: True if equal, False otherwise
        :rtype: bool
        """
        if isinstance(other, SoftwareInventory):
            return (
                self.name == other.name
                and self.version == other.version
                and self.parentHardwareAssetId == other.parentHardwareAssetId
            )
        return False

    def __hash__(self) -> hash:
        """
        Override the default hash behavior

        :return: hash of the SoftwareInventory
        :rtype: hash
        """
        return hash((self.name, self.version, self.parentHardwareAssetId))

    @classmethod
    def insert(cls, app: Application, obj: "SoftwareInventory") -> "SoftwareInventory":
        """
        Insert a new SoftwareInventory into RegScale

        :param Application app: application
        :param SoftwareInventory obj: SoftwareInventory to insert
        :return: SoftwareInventory object
        :rtype: SoftwareInventory
        """
        api = Api()
        result = {}
        res = api.post(url=app.config["domain"] + "/api/softwareinventory", json=obj.dict())
        if res.status_code == 200 and res.ok:
            result = SoftwareInventory(**res.json())
        return result

    @classmethod
    def update(cls, app: Application, obj: "SoftwareInventory") -> "SoftwareInventory":
        """
        Update an existing SoftwareInventory in RegScale

        :param Application app: application
        :param SoftwareInventory obj: SoftwareInventory to update
        :return: SoftwareInventory object
        :rtype: SoftwareInventory
        """
        api = Api()
        result = {}
        res = api.put(
            url=app.config["domain"] + f"/api/softwareinventory/{obj.id}",
            json=obj.dict(),
        )
        if res.status_code == 200 and res.ok:
            result = SoftwareInventory(**res.json())
        return result

    @classmethod
    def fetch_by_asset(cls, app: Application, asset_id: int) -> List["SoftwareInventory"]:
        """
        Fetch all SoftwareInventory for a given asset

        :param Application app: application
        :param int asset_id: The asset id
        :return: A list of SoftwareInventory objects
        :rtype: List[SoftwareInventory]
        """
        api = Api()
        result = []
        res = api.get(url=app.config["domain"] + f"/api/softwareinventory/getAllByParent/{asset_id}")
        if res.status_code == 200 and res.ok:
            result = [SoftwareInventory(**inv) for inv in res.json()]
        return result

    @classmethod
    def get_map(cls, plan_id: int, key_field: str = "parentId") -> dict[str, "SoftwareInventory"]:
        """
        Get the asset map for the asset and cache it in Redis.

        :param int plan_id: Security Plan ID
        :param str key_field: Key field to use, defaults to "identifier"
        :return: Data Map
        :rtype: dict[str, "Data"]

        # TODO: Implement filter by plan_id in RegScale API
        """
        search_data = f"""query {{
            {cls.get_module_string()}(skip: 0, take: 50) {{
                items {{
                    {cls.build_graphql_fields()}
                }}
                totalCount
                pageInfo {{
                    hasNextPage
                }}
            }}
        }}"""
        response = cls._get_api_handler().graph(query=search_data)
        objects = cast(List["SoftwareInventory"], cls._handle_graph_response(response))
        return_assets = {}
        for obj in objects:
            identifier = getattr(obj, key_field, None)
            if identifier:
                return_assets[identifier] = obj

        return {k: v.model_dump_json() for k, v in return_assets.items()}
