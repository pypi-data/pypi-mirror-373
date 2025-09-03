#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Class for a RegScale SystemRoles"""
import copy
import logging
from typing import List, Optional
from typing import cast
from urllib.parse import urljoin

import requests
from pydantic import Field, ConfigDict

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.models.regscale_models.regscale_model import RegScaleModel

logger = logging.getLogger("regscale")


class SystemRole(RegScaleModel):
    """Class for a RegScale SystemRoles"""

    _module_slug = "systemRoles"

    roleName: str  # Required Field
    roleType: str  # Required Field
    accessLevel: str  # Required Field
    sensitivityLevel: str  # Required field
    privilegeDescription: str  # Required Field
    securityPlanId: int  # Required Field
    functions: str  # Required Field
    createdById: str = Field(default_factory=RegScaleModel.get_user_id)
    id: int = 0
    uuid: str = ""
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    isPublic: bool = True
    dateCreated: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    assignedUserId: Optional[str] = Field(default_factory=RegScaleModel.get_user_id)
    fedrampRoleId: Optional[str] = None
    tenantsId: int = 1
    externalUserId: Optional[str] = None

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the SystemRole

        :return: Additional endpoints for the SystemRole
        :rtype: ConfigDict
        """
        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getAllByParent/{intParentID}",
        )

    @staticmethod
    def from_dict(obj: dict) -> "SystemRole":  # type: ignore
        """
        Create a SystemRoles object from a dictionary

        :param dict obj: The dictionary to convert to a SystemRoles object
        :return: A SystemRoles object
        :rtype: SystemRole
        """
        copy_obj = copy.copy(obj)
        if "id" in copy_obj:
            del copy_obj["id"]
        if isinstance(copy_obj["functions"], list):
            copy_obj["functions"] = ", ".join(copy_obj["functions"])
        return SystemRole(**copy_obj)

    def __eq__(self, other: "SystemRole") -> bool:
        """
        Compare two SystemRoles objects

        :param SystemRole other: The object to compare to
        :return: True if the SystemRoles objects are equal
        :rtype: bool
        """
        if not isinstance(other, SystemRole):
            return NotImplemented
        return self.dict() == other.dict()

    def __hash__(self) -> hash:
        """
        Hash a SystemRoles object

        :return: The hash of the SystemRoles object
        :rtype: hash
        """
        return hash(
            (
                self.roleName,
                self.roleType,
                self.accessLevel,
                self.sensitivityLevel,
                self.privilegeDescription,
                tuple(self.functions),
                self.securityPlanId,
                self.isPublic,
                self.assignedUserId,
                self.fedrampRoleId,
            )
        )

    def insert_systemrole(self, app: Application) -> dict:
        """
        Insert a SystemRoles object into the database

        :param Application app: The application object
        :return: The dict of the SystemRoles object
        :rtype: dict
        """
        # Convert the object to a dictionary
        api = Api()
        url = urljoin(app.config.get("domain", ""), "/api/systemRoles/")
        if hasattr(self, "id"):
            del self.id
        if hasattr(self, "uuid"):
            del self.uuid
        if hasattr(self, "dateCreated"):
            del self.dateCreated
        data = self.dict()
        # Make the API call
        try:
            response = api.post(url, json=data)
            if response.ok:
                # Parse the response to a SystemRoles object
                logger.info(
                    "Successfully saved System Role %s to RegScale Security" + " Plan %i",
                    data["roleName"],
                    data["securityPlanId"],
                )
                return response.json()
        except requests.exceptions.RequestException as err:
            logger.warning(
                "Unable to post System Role to RegScale Security Plan #%i, \n%s",
                self.securityPlanId,
                err,
            )
        return {}

    @classmethod
    def get_or_create(cls, app: Application, role_name: str, ssp_id: int, **kwargs) -> dict:
        """
        Get or create a SystemRoles object for a given SSP ID

        :param Application app: The application object
        :param str role_name: The name of the role
        :param int ssp_id: The SSP ID
        :param **kwargs: Additional keyword arguments
        :return: The SystemRoles dict object
        :rtype: dict
        """

        # Check if a role with the same name already exists
        if "all_roles" not in kwargs:
            all_roles = cls.get_all_by_ssp_id(app, ssp_id)
        else:
            all_roles = kwargs["all_roles"]

        existing_role = next(
            (role for role in all_roles if role["roleName"].lower().strip() == role_name.lower().strip()),
            None,
        )
        if existing_role:
            logger.debug("Role: %s already exists in RegScale, skipping insert..", role_name.strip())
            return existing_role
        else:
            # If it doesn't exist, create a new one
            new_role = cls(roleName=role_name.strip(), **kwargs)
            return new_role.insert_systemrole(app=app)

    @staticmethod
    def get_all_by_ssp_id(app: Application, ssp_id: int) -> List["SystemRole"]:
        """
        Get a list of SystemRoles objects for a given SSP ID

        :param Application app: The application object
        :param int ssp_id: The SSP ID
        :return: A list of SystemRoles objects
        :rtype: List[SystemRole]
        """
        api = Api()
        url = urljoin(app.config.get("domain", ""), f"/api/systemRoles/getAllByParent/{ssp_id}")
        response = api.get(url)
        # Parse the response to a list of SystemRoles objects
        return cast(List[SystemRole], [role for role in response.json()] if response.json() else [])
