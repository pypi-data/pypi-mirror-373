"""Data model class"""

from enum import Enum
from typing import List, Optional, cast

from pydantic import Field, ConfigDict
from requests import Response

from regscale.core.app.utils.app_utils import (
    get_current_datetime,
    create_progress_object,
)
from .regscale_model import RegScaleModel, T
from ...core.app.internal.model_editor import get_all_by_parent


class DataListItem(RegScaleModel):
    """
    Data list item model class
    """

    id: int
    dateCreated: str
    dataType: str
    dataSource: str


class DataDataType(str, Enum):
    """
    Data data type enum
    """

    JSON = "JSON"
    XML = "XML"
    YAML = "YAML"

    def __str__(self):
        return self.value


class Data(RegScaleModel):
    """
    Data model class
    """

    _module_slug = "data"
    _unique_fields = [
        ["parentId", "parentModule", "dataSource", "dataType"],
    ]

    id: Optional[int] = 0
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    isPublic: bool = True
    dataSource: str
    dataType: Optional[str] = None
    rawData: Optional[str] = None
    parentId: int
    parentModule: str
    tenantsId: int = 1
    dateLastUpdated: str = Field(default_factory=get_current_datetime)

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Data model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            batch_create="/api/{model_slug}/batchCreate",
            batch_update="/api/{model_slug}/batchUpdate",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",
        )

    @classmethod
    def get_map(cls, plan_id: int, key_field: str = "parentId") -> dict[str, "Data"]:
        """
        Get the asset map for the asset and cache it in Redis.

        :param int plan_id: Security Plan ID
        :param str key_field: Key field to use, defaults to "identifier"
        :return: Data Map
        :rtype: dict[str, "Data"]

        # TODO: Implement filter by plan_id in RegScale API
        """
        search_data = f"""query {{
            data(skip: 0, take: 50) {{
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
        objects = cast(List["Data"], cls._handle_graph_response(response))
        return_assets = {}
        for obj in objects:
            identifier = getattr(obj, key_field, None)
            if identifier:
                return_assets[identifier] = obj

        return {k: v.model_dump_json() for k, v in return_assets.items()}
