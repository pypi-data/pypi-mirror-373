#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create Properties model."""
import json
import logging
import math
from typing import Any, List, Optional, Union

from pydantic import ConfigDict, Field, field_validator

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import get_current_datetime, recursive_items
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.utils import flatten_dict

logger = logging.getLogger("regscale")


class Property(RegScaleModel):
    """Properties plan model"""

    _module_slug = "properties"
    _unique_fields = [
        ["key", "parentId", "parentModule"],
    ]
    _parent_id_field = "parentId"

    id: int = 0
    createdById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    isPublic: bool = True
    key: Optional[str] = ""
    value: Optional[Union[str, int, float]] = ""
    label: Optional[str] = ""
    otherAttributes: Optional[str] = ""
    parentId: Optional[int] = 0
    parentModule: Optional[str] = ""
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    alt_id: Optional[str] = None

    @field_validator("value", mode="before")
    def validate_value(cls, value: Any) -> Any:
        """
        Validate the value field and convert it to a string if it is a boolean or list

        :param Any value: Value to validate
        :return: Value if valid
        :rtype: Any
        """
        import math

        if isinstance(value, bool):
            return "True" if value else "False"
        if isinstance(value, list):
            return ", ".join(value)
        if isinstance(value, float) and math.isnan(value):
            return "NULL"
        if isinstance(value, str) and value.strip() == "":
            return "NULL"
        if isinstance(value, dict):
            return json.dumps(value)
        return value or "NULL"

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Properties model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            batch_create="/api/{model_slug}/batchCreate",
            batch_update="/api/{model_slug}/batchUpdate",
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}/{strModule}",
        )

    @staticmethod
    def create_properties_from_list(
        parent_id: Union[str, int],
        parent_module: str,
        properties_list: List[dict],
    ) -> List["Property"]:
        """
        Create a list of Properties objects from a list of dicts

        :param Union[str, int] parent_id: ID of the SSP to create the Properties objects for
        :param str parent_module: Parent module of the Properties objects
        :param Union[str, int] properties_list: List of dicts to create objects from
        :return: List[dict] of Properties objects
        :rtype: List[Property]
        """
        properties = [
            Property(parentId=int(parent_id), parentModule=parent_module, **properties)
            for properties in properties_list
        ]
        return [property_.create_new_properties(return_object=True) for property_ in properties]

    def create_new_properties(self, return_object: Optional[bool] = False) -> Union[bool, "Property"]:
        """
        Create a new Properties object in RegScale

        :param Optional[bool] return_object: Whether to return the object if successful
                                            , defaults to False
        :return: True or the Properties created if successful, False otherwise
        :rtype: Union[bool, Property]
        """
        api = Api()
        data = self.dict()
        data["id"] = None
        data["createdById"] = api.config["userId"]
        data["lastUpdatedById"] = api.config["userId"]
        properties_response = api.post(
            f'{api.config["domain"]}/api/properties/',
            json=data,
        )
        if properties_response.ok:
            logger.info("Created Properties: %s", properties_response.json()["id"])
            if return_object:
                return Property(**properties_response.json())
            return True
        logger.error("Error creating Properties: %s", properties_response.text)
        return False

    def __eq__(self, other: "Property") -> bool:
        """
        Test equality of two Property objects

        :param Property other: Other Property object to compare to
        :return: Equality of two Property objects
        :rtype: bool
        """
        return (
            self.key == other.key
            and self.value == other.value
            and self.parentId == other.parentId
            and self.parentModule == other.parentModule
        )

    @staticmethod
    def generate_property_list_from_dict(dat: dict) -> list["Property"]:
        """
        Generate Property List from Dict

        :param dict dat: Data to generate Property list from
        :return: List of Properties
        :rtype: list["Property"]
        """
        kvs = recursive_items(dat)
        return [Property(key=k, value=v, createdById="", parentModule="") for k, v in kvs]

    @staticmethod
    def update_properties(app: Application, prop_list: list["Property"]) -> None:
        """
        Post a list of properties to RegScale

        :param Application app: Application object
        :param list[Property] prop_list: List of properties to post to RegScale
        :rtype: None
        """
        api = Api()
        props = [prop.dict() for prop in prop_list]
        res = api.put(
            url=app.config["domain"] + "/api/properties/batchupdate",
            json=props,
        )
        if res.status_code == 200:
            if len(prop_list) > 0:
                logger.info("Successfully updated %i properties to RegScale", len(prop_list))
        else:
            logger.error("Failed to update properties to RegScale\n%s", res.text)

    @staticmethod
    def existing_properties(app: Application, existing_assets: list[dict]) -> list["Property"]:
        """
        Return a list of existing properties in RegScale

        :param Application app: Application object
        :param list[dict] existing_assets: List of assets from RegScale
        :return: List of properties for the provided assets
        :rtype: list["Property"]
        """
        properties = []
        api = Api()
        for asset in existing_assets:
            res = api.get(url=app.config["domain"] + f"/api/properties/getAllByParent/{asset['id']}/assets")
            if res.status_code == 200:
                for prop in res.json():
                    prop["alt_id"] = asset["wizId"]
                    properties.append(Property(**prop))
        return properties

    @staticmethod
    def insert_properties(app: Application, prop_list: list["Property"]) -> list["Property"]:
        """
        Post a list of properties to RegScale

        :param Application app: Application instance
        :param list[Property] prop_list: List of properties to post
        :return: List of created properties in RegScale
        :rtype: list["Property"]
        """
        properties = []
        api = Api()
        res = api.post(
            url=app.config["domain"] + "/api/properties/batchcreate",
            json=[prop.dict() for prop in prop_list],
        )
        if res.status_code == 200:
            if len(prop_list) > 0:
                api.logger.info("Successfully posted %i properties to RegScale", len(prop_list))
            properties = [Property(**prop) for prop in res.json()]
        else:
            logger.error("Failed to post properties to RegScale\n%s", res.text)
        return properties

    @staticmethod
    def get_properties(wiz_data: str, wiz_id: str) -> List["Property"]:
        """
        Convert Wiz properties data into a list of Property objects.

        :param str wiz_data: JSON string containing Wiz information
        :param str wiz_id: Identifier for a Wiz issue
        :return: A list of Property objects derived from Wiz data
        :rtype: List[Property]
        """
        app = Application()
        wiz_dict = json.loads(wiz_data)
        flattened = flatten_dict(wiz_dict)
        properties = []

        current_datetime = get_current_datetime()
        user_id = app.config["userId"]

        for key, value in flattened:
            # Skip empty values or empty dictionaries converted to strings
            if not value or value == "{}":
                continue
            value = _value_checks(value)
            # Create and add Property object if there's a meaningful value
            if value:
                prop = Property(
                    createdById=user_id,
                    dateCreated=current_datetime,
                    lastUpdatedById=user_id,
                    isPublic=True,
                    alt_id=wiz_id,
                    key=key,
                    value=value,
                    parentId=0,
                    parentModule="assets",
                    dateLastUpdated=current_datetime,
                )
                properties.append(prop)

        return properties


def _value_checks(value: Any) -> Any:
    """
    Check if the value is a boolean or list and convert it to a string if needed
    :param Any value: Value to check
    :return: Converted value
    :rtype: Any
    """
    # Simplify handling of list and dict values
    if isinstance(value, list):
        value = value[0] if value else None  # Get first item of the list if not empty
    if isinstance(value, dict):
        value = next((v for _, v in flatten_dict(value)), None)

    # Replace NaN values with an empty string
    if isinstance(value, (int, float)) and math.isnan(value):
        value = ""
    return value
