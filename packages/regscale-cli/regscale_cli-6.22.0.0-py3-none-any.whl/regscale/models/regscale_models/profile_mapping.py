#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Model for Profile Mapping in the application"""
import importlib
from typing import TYPE_CHECKING, List, Optional
from urllib.parse import urljoin

from pydantic import ConfigDict, Field

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models.regscale_models.security_control import SecurityControl

if TYPE_CHECKING:
    from regscale.models import ControlImplementation, ControlImplementationStatus


class ProfileMapping(RegScaleModel):
    """
    Profile Mapping Model
    """

    _module_slug = "profileMapping"

    id: int = 0
    profileID: int
    controlID: int  # the int id of the security control
    controlId: Optional[str] = Field(alias="control_id", default=None)  # the control id string i.e. AC-1
    title: Optional[str] = None
    family: Optional[str] = None
    control: Optional[SecurityControl] = None
    tenantsId: Optional[int] = None
    createdById: Optional[str] = None
    dateCreated: Optional[str] = None
    dateLastUpdated: Optional[str] = None
    isPublic: bool = True
    lastUpdatedById: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)

    # Create a lazily loaded reference to avoid circular imports
    def _get_control_implementation_classes(self):
        """
        Get the control implementation classes in a lazy manner

        :return: The control implementation classes
        :rtype: Tuple[ControlImplementation, ControlImplementationStatus]
        :raises ImportError: If the module cannot be imported
        """
        module = importlib.import_module("regscale.models")
        return (module.ControlImplementation, module.ControlImplementationStatus)

    def to_implementation(self, security_plan_id: int):
        """
        Convert a profile mapping to a control implementation.

        :param int security_plan_id: The parent Security Plan ID
        :rtype: ControlImplementation
        :return: The control implementation
        """
        # Create a lazily loaded reference to avoid circular imports, will only import once, and subsequent calls will
        # use the already imported classes
        ControlImplementation, ControlImplementationStatus = self._get_control_implementation_classes()

        return ControlImplementation(
            status=ControlImplementationStatus.NotImplemented.value,
            controlID=self.controlID,
            assessmentFrequency=365,
            parentId=security_plan_id,
            parentModule="securityplans",
        )

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ProfileMapping model, using {model_slug} as a placeholder for the model slug.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """

        return ConfigDict(  # type: ignore
            get_all_by_parent="/api/{model_slug}/getByProfile/{intParentID}",
            lookup="/api/{model_slug}/lookup/{intProfileID}/{intControlID}",
            get_by_profile="/api/{model_slug}/getByProfile/{intProfileID}",
            oscal_prep="/api/{model_slug}/oscalPrep/{intProfileID}",
            create_profile_mapping="/api/{model_slug}",
            batch_create="/api/{model_slug}/batchCreate",
            batch_delete="/api/{model_slug}/batchDelete",
            delete_mapping="/api/{model_slug}/deleteMapping/{intProfileID}/{intControlID}",
        )

    @classmethod
    def get_by_profile(cls, profile_id: int) -> List["ProfileMapping"]:
        """
        Get profile mappings by profile ID

        :param int profile_id: Profile ID
        :return: List of profile mappings
        :rtype: List[ProfileMapping]
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        response = cls._get_api_handler().get(
            endpoint=cls.get_endpoint("get_by_profile").format(intProfileID=profile_id)
        )
        mappings = []
        if response and response.ok:
            mappings = [cls(**map) for map in response.json()]
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(SecurityControl.get_object, object_id=mapping.controlID) for mapping in mappings
                ]
            for future, mapping in zip(as_completed(futures), mappings):
                if control := future.result():
                    mapping.control = control
        return mappings

    def insert_profile_mapping(self, app: Application) -> dict:
        """
        Insert a new profile mapping

        :param Application app: Application
        :raises Exception: API request failed
        :return: dict of profile mapping
        :rtype: dict
        """
        api = Api()
        # Convert the model to a dictionary
        data = self.dict()
        api_url = urljoin(app.config["domain"], "/api/profileMapping")

        # Make the API call
        response = api.post(url=api_url, json=data)

        # Check the response
        if not response.ok:
            api.logger.debug(
                f"API Call failed to: {api_url}\n{response.status_code}: {response.reason} {response.text}"
            )
            raise response.raise_for_status()

        return response.json()

    @staticmethod
    def insert_batch(app: Application, mappings: List["ProfileMapping"]) -> list[dict]:
        """
        Insert a new list of profile mappings as a batch

        :param Application app: Application
        :param List[ProfileMapping] mappings: List of profile mappings
        :return: list[dict] of profile mappings
        :rtype: list[dict]
        """
        api = Api()
        # Convert the model to a dictionary

        data = [item.dict() for item in mappings]
        for d in data:
            d["isPublic"] = "true"
        api_url = urljoin(app.config["domain"], "/api/profileMapping/batchCreate")

        # Make the API call
        response = api.post(url=api_url, json=data)

        # Check the response
        return response.json() if response.ok else response.raise_for_status()
